// SPDX-License-Identifier: GPL-3.0-or-later
/*
 * x7-bench3d - how much 3D can the console draw? A small software renderer
 * (the console has no 3D GPU) that measures, on the real screen:
 *
 *   1. the raw cost of filling the whole screen, 16-bit and 32-bit
 *   2. a spinning, textured, per-vertex-lit model (a torus) at 12 to 4000
 *      triangles, rendered at 320x240 and scaled 2x to the screen, in
 *      16-bit and 32-bit screen modes; and at the full 640x480
 *   3. playing back a pre-rendered 36-frame "turntable" sprite (160x160),
 *      1 and 6 at a time - the cheap way to show 3D-looking objects
 *
 * Run it over the USB shell (as root):  x7-bench3d [--quick]
 * The screen console is paused while it runs and comes back afterwards.
 * Results are printed and saved to /share/x7-bench3d.txt (X7DATA).
 *
 * Renderer: 16-bit (RGB565) colour buffer and 16-bit z-buffer in normal
 * (cached) memory, affine texture mapping with a 64x64 texture, Gouraud
 * lighting, back-face culling - roughly what a PlayStation 1 does. The
 * frame is then copied (and scaled / converted) to the framebuffer, which
 * is uncached memory on this SoC: that copy is reported separately.
 */
#define _GNU_SOURCE
#include <fcntl.h>
#include <linux/fb.h>
#include <linux/kd.h>
#include <math.h>
#include <signal.h>
#include <stdarg.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <time.h>
#include <unistd.h>

#define TEX	64			/* texture size (power of two) */
#define MAXW	640
#define MAXH	480

static volatile sig_atomic_t stop;
static int fbfd = -1, ttyfd = -1, orig_bpp;
static uint8_t *fb;
static size_t fb_size;
static unsigned int fb_w, fb_h, fb_line, fb_bpp;
static struct fb_var_screeninfo var0;
static uint16_t texture[TEX * TEX];
static uint16_t cbuf[MAXW * MAXH];	/* colour buffer, RGB565 */
static uint16_t zbuf[MAXW * MAXH];	/* z-buffer, smaller = nearer */
static int rw, rh;			/* render size */
static FILE *report;

static double now(void)
{
	struct timespec ts;

	clock_gettime(CLOCK_MONOTONIC, &ts);
	return ts.tv_sec + ts.tv_nsec / 1e9;
}

static void out(const char *fmt, ...) __attribute__((format(printf, 1, 2)));
static void out(const char *fmt, ...)
{
	va_list ap;

	va_start(ap, fmt);
	vprintf(fmt, ap);
	va_end(ap);
	fflush(stdout);
	if (report) {
		va_start(ap, fmt);
		vfprintf(report, fmt, ap);
		va_end(ap);
		fflush(report);
	}
}

/* ------------------------------------------------------------ framebuffer */

static int set_bpp(unsigned int bpp)
{
	struct fb_var_screeninfo v;
	struct fb_fix_screeninfo f;

	if (ioctl(fbfd, FBIOGET_VSCREENINFO, &v))
		return -1;
	if (v.bits_per_pixel != bpp) {
		v.bits_per_pixel = bpp;
		v.activate = FB_ACTIVATE_NOW;
		if (ioctl(fbfd, FBIOPUT_VSCREENINFO, &v))
			return -1;
	}
	if (ioctl(fbfd, FBIOGET_VSCREENINFO, &v) || ioctl(fbfd, FBIOGET_FSCREENINFO, &f))
		return -1;
	fb_w = v.xres;
	fb_h = v.yres;
	fb_bpp = v.bits_per_pixel;
	fb_line = f.line_length;
	return fb_bpp == bpp ? 0 : -1;
}

static void restore(void)
{
	if (fbfd >= 0 && orig_bpp)
		set_bpp(orig_bpp);
	if (ttyfd >= 0) {
		ioctl(ttyfd, KDSETMODE, KD_TEXT);	/* the console redraws itself */
		close(ttyfd);
		ttyfd = -1;
	}
}

static void on_signal(int sig)
{
	(void)sig;
	stop = 1;
}

/* fill the whole screen with one colour (32-bit stores) */
static void fb_fill(uint32_t word)
{
	unsigned int y, x, words = fb_w * fb_bpp / 32;

	for (y = 0; y < fb_h; y++) {
		volatile uint32_t *row = (volatile uint32_t *)(fb + (size_t)y * fb_line);

		for (x = 0; x < words; x++)
			row[x] = word;
	}
}

static inline uint32_t rgb565_to_8888(uint16_t p)
{
	uint32_t r = (p >> 11) & 31, g = (p >> 5) & 63, b = p & 31;

	return 0xff000000u | (r << 19 | (r >> 2) << 16) | (g << 10 | (g >> 4) << 8) | (b << 3 | b >> 2);
}

/* copy the colour buffer to the screen: 2x scaled (320x240) or 1:1 */
static void present(void)
{
	unsigned int x, y, scale = fb_w / rw;

	for (y = 0; y < (unsigned int)rh; y++) {
		const uint16_t *src = cbuf + y * rw;
		unsigned int k;

		for (k = 0; k < scale; k++) {
			volatile uint32_t *row = (volatile uint32_t *)(fb + (size_t)(y * scale + k) * fb_line);

			if (fb_bpp == 16 && scale == 2) {
				for (x = 0; x < (unsigned int)rw; x++)
					row[x] = src[x] | (uint32_t)src[x] << 16;
			} else if (fb_bpp == 16) {
				for (x = 0; x < (unsigned int)rw; x += 2)
					row[x / 2] = src[x] | (uint32_t)src[x + 1] << 16;
			} else if (scale == 2) {
				for (x = 0; x < (unsigned int)rw; x++) {
					uint32_t c = rgb565_to_8888(src[x]);

					row[2 * x] = c;
					row[2 * x + 1] = c;
				}
			} else {
				for (x = 0; x < (unsigned int)rw; x++)
					row[x] = rgb565_to_8888(src[x]);
			}
		}
	}
}

/* ------------------------------------------------------------- the model */

struct vtx { float x, y, z, nx, ny, nz, u, v; };
struct sv { float x, y, z, u, v, l; int vis; };

static struct vtx *verts;
static int (*tris)[3];
static struct sv *scr;
static int nverts, ntris;

static void make_torus(int major, int minor)
{
	int i, j, t = 0;
	float R = 1.0f, r = 0.42f;

	nverts = (major + 1) * (minor + 1);
	ntris = 2 * major * minor;
	verts = realloc(verts, sizeof(*verts) * nverts);
	scr = realloc(scr, sizeof(*scr) * nverts);
	tris = realloc(tris, sizeof(*tris) * ntris);
	for (i = 0; i <= major; i++) {
		float a = 2 * (float)M_PI * i / major;

		for (j = 0; j <= minor; j++) {
			float b = 2 * (float)M_PI * j / minor;
			struct vtx *p = &verts[i * (minor + 1) + j];

			p->nx = cosf(a) * cosf(b);
			p->ny = sinf(a) * cosf(b);
			p->nz = sinf(b);
			p->x = cosf(a) * (R + r * cosf(b));
			p->y = sinf(a) * (R + r * cosf(b));
			p->z = r * sinf(b);
			p->u = 4.0f * i / major * TEX;
			p->v = 1.0f * j / minor * TEX;
		}
	}
	for (i = 0; i < major; i++)
		for (j = 0; j < minor; j++) {
			int a = i * (minor + 1) + j, b = a + minor + 1;

			tris[t][0] = a; tris[t][1] = b; tris[t][2] = a + 1; t++;
			tris[t][0] = a + 1; tris[t][1] = b; tris[t][2] = b + 1; t++;
		}
}

/* a cube: 12 triangles (the smallest test) */
static void make_cube(void)
{
	static const float P[8][3] = { {-1,-1,-1},{1,-1,-1},{1,1,-1},{-1,1,-1},{-1,-1,1},{1,-1,1},{1,1,1},{-1,1,1} };
	static const int F[6][4] = { {0,3,2,1},{4,5,6,7},{0,1,5,4},{2,3,7,6},{1,2,6,5},{0,4,7,3} };
	static const float N[6][3] = { {0,0,-1},{0,0,1},{0,-1,0},{0,1,0},{1,0,0},{-1,0,0} };
	int f, k, t = 0;

	nverts = 24;
	ntris = 12;
	verts = realloc(verts, sizeof(*verts) * nverts);
	scr = realloc(scr, sizeof(*scr) * nverts);
	tris = realloc(tris, sizeof(*tris) * ntris);
	for (f = 0; f < 6; f++) {
		for (k = 0; k < 4; k++) {
			struct vtx *p = &verts[f * 4 + k];

			p->x = P[F[f][k]][0] * 0.8f; p->y = P[F[f][k]][1] * 0.8f; p->z = P[F[f][k]][2] * 0.8f;
			p->nx = N[f][0]; p->ny = N[f][1]; p->nz = N[f][2];
			p->u = (k == 1 || k == 2) ? TEX - 1 : 0;
			p->v = (k >= 2) ? TEX - 1 : 0;
		}
		tris[t][0] = f * 4; tris[t][1] = f * 4 + 1; tris[t][2] = f * 4 + 2; t++;
		tris[t][0] = f * 4; tris[t][1] = f * 4 + 2; tris[t][2] = f * 4 + 3; t++;
	}
}

static void make_texture(void)
{
	int x, y;

	for (y = 0; y < TEX; y++)
		for (x = 0; x < TEX; x++) {
			int check = ((x >> 3) ^ (y >> 3)) & 1;
			int r = check ? 31 : (x >> 1), g = check ? 50 : 20 + (y >> 2), b = check ? 10 : 31 - (x >> 2);

			texture[y * TEX + x] = r << 11 | g << 5 | b;
		}
}

/* ------------------------------------------------------------ rasterizer */

static void draw_tri(const struct sv *a, const struct sv *b, const struct sv *c)
{
	const struct sv *t;
	float area, dudx, dudy, dvdx, dvdy, dldx, dldy, dzdx, dzdy;
	int y0, y1, y;

	if (a->y > b->y) { t = a; a = b; b = t; }
	if (b->y > c->y) { t = b; b = c; c = t; }
	if (a->y > b->y) { t = a; a = b; b = t; }
	area = (b->x - a->x) * (c->y - a->y) - (c->x - a->x) * (b->y - a->y);
	if (area > -0.5f && area < 0.5f)
		return;
#define GRAD(q) \
	d##q##dx = ((b->q - a->q) * (c->y - a->y) - (c->q - a->q) * (b->y - a->y)) / area; \
	d##q##dy = ((c->q - a->q) * (b->x - a->x) - (b->q - a->q) * (c->x - a->x)) / area
	GRAD(u); GRAD(v); GRAD(l); GRAD(z);
#undef GRAD
	y0 = (int)ceilf(a->y);
	y1 = (int)ceilf(c->y);
	if (y0 < 0) y0 = 0;
	if (y1 > rh) y1 = rh;
	for (y = y0; y < y1; y++) {
		float fy = y, xa, xb, xl, xr, dx0, dy0;
		int x0, x1, x, u, v, l, z, du, dv, dl, dz;
		uint16_t *cp, *zp;

		xa = a->x + (c->x - a->x) * (fy - a->y) / (c->y - a->y);
		if (fy < b->y)
			xb = a->x + (b->x - a->x) * (fy - a->y) / (b->y - a->y);
		else
			xb = (c->y > b->y) ? b->x + (c->x - b->x) * (fy - b->y) / (c->y - b->y) : b->x;
		xl = xa < xb ? xa : xb;
		xr = xa < xb ? xb : xa;
		x0 = (int)ceilf(xl);
		x1 = (int)ceilf(xr);
		if (x0 < 0) x0 = 0;
		if (x1 > rw) x1 = rw;
		if (x0 >= x1)
			continue;
		dx0 = x0 - a->x;
		dy0 = fy - a->y;
		u = (int)((a->u + dx0 * dudx + dy0 * dudy) * 65536.0f);
		v = (int)((a->v + dx0 * dvdx + dy0 * dvdy) * 65536.0f);
		l = (int)((a->l + dx0 * dldx + dy0 * dldy) * 65536.0f);
		z = (int)((a->z + dx0 * dzdx + dy0 * dzdy) * 65536.0f);
		du = (int)(dudx * 65536.0f); dv = (int)(dvdx * 65536.0f);
		dl = (int)(dldx * 65536.0f); dz = (int)(dzdx * 65536.0f);
		cp = cbuf + y * rw + x0;
		zp = zbuf + y * rw + x0;
		for (x = x0; x < x1; x++, cp++, zp++, u += du, v += dv, l += dl, z += dz) {
			unsigned int zz = (unsigned int)z >> 16, tx, li, r, g, bl;

			if (zz >= *zp)
				continue;
			*zp = zz;
			tx = texture[((v >> 16) & (TEX - 1)) * TEX + ((u >> 16) & (TEX - 1))];
			li = l < 0 ? 0 : (unsigned int)l >> 16;	/* light 0..256 */
			if (li > 256) li = 256;
			r = (((tx >> 11) & 31) * li) >> 8;
			g = (((tx >> 5) & 63) * li) >> 8;
			bl = ((tx & 31) * li) >> 8;
			*cp = r << 11 | g << 5 | bl;
		}
	}
}

/* transform, light and draw the model at angle t (seconds) into cbuf */
static int render(double t, int ox, int oy, int w, int h)
{
	float ay = (float)t * 1.1f, ax = (float)t * 0.7f;
	float cy = cosf(ay), sy = sinf(ay), cx = cosf(ax), sx = sinf(ax);
	float f = h * 1.1f, lx = 0.4f, ly = 0.5f, lz = -0.77f;
	int i, drawn = 0;

	for (i = 0; i < nverts; i++) {
		const struct vtx *p = &verts[i];
		float x = p->x * cy + p->z * sy, z = -p->x * sy + p->z * cy, y = p->y;
		float y2 = y * cx - z * sx, z2 = y * sx + z * cx + 3.2f;
		float nx = p->nx * cy + p->nz * sy, nz = -p->nx * sy + p->nz * cy, ny = p->ny;
		float ny2 = ny * cx - nz * sx, nz2 = ny * sx + nz * cx;
		float d = nx * lx + ny2 * ly + nz2 * lz;
		struct sv *s = &scr[i];

		s->x = ox + w / 2 + x * f / z2;
		s->y = oy + h / 2 - y2 * f / z2;
		s->z = (z2 - 1.0f) * 8000.0f;		/* 16-bit depth */
		s->u = p->u;
		s->v = p->v;
		s->l = 60.0f + (d > 0 ? d : 0) * 196.0f;
		/* facing the camera (at the origin)? normal . (camera - point) > 0 */
		s->vis = nx * x + ny2 * y2 + nz2 * z2 < 0;
	}
	for (i = 0; i < ntris; i++) {
		const struct sv *a = &scr[tris[i][0]], *b = &scr[tris[i][1]], *c = &scr[tris[i][2]];

		/* back-face culling: skip triangles whose corners all face away */
		if (!a->vis && !b->vis && !c->vis)
			continue;
		draw_tri(a, b, c);
		drawn++;
	}
	return drawn;
}

/* tiny 3x5 digits for the FPS counter in the corner */
static void draw_number(int n)
{
	static const uint16_t font[10] = { 0x7b6f, 0x2c97, 0x73e7, 0x73cf, 0x5bc9, 0x79cf, 0x79ef, 0x7249, 0x7bef, 0x7bcf };
	char s[12];
	int i, k, x0 = 4;

	snprintf(s, sizeof(s), "%d", n);
	for (i = 0; s[i]; i++, x0 += 8)
		for (k = 0; k < 15; k++)
			if (font[s[i] - '0'] & (1 << (14 - k))) {
				int px = x0 + (k % 3) * 2, py = 4 + (k / 3) * 2;

				cbuf[py * rw + px] = cbuf[py * rw + px + 1] = 0xffff;
				cbuf[(py + 1) * rw + px] = cbuf[(py + 1) * rw + px + 1] = 0xffff;
			}
}

/* one 3D test: returns frames per second, fills the per-frame times */
static double run_3d(double seconds, double *ms_render, double *ms_present, int *drawn)
{
	double start = now(), t0, r = 0, p = 0;
	int frames = 0, fps = 0;

	while (!stop && now() - start < seconds) {
		t0 = now();
		memset(cbuf, 0, (size_t)rw * rh * 2);
		memset(zbuf, 0xff, (size_t)rw * rh * 2);
		*drawn = render(t0 - start, 0, 0, rw, rh);
		draw_number(fps);
		r += now() - t0;
		t0 = now();
		present();
		p += now() - t0;
		frames++;
		fps = (int)(frames / (now() - start) + 0.5);
	}
	*ms_render = frames ? r * 1000 / frames : 0;
	*ms_present = frames ? p * 1000 / frames : 0;
	return frames / (now() - start);
}

/* ---------------------------------------------------- pre-rendered sprites */

#define SPR 160
#define SPR_FRAMES 36
static uint16_t *sprites;

static void prerender_sprites(void)
{
	int f, save_w = rw, save_h = rh;

	sprites = malloc((size_t)SPR * SPR * 2 * SPR_FRAMES);
	make_torus(50, 20);
	rw = rh = SPR;
	for (f = 0; f < SPR_FRAMES; f++) {
		memset(cbuf, 0, SPR * SPR * 2);
		memset(zbuf, 0xff, SPR * SPR * 2);
		render(f * 2 * M_PI / 1.1 / SPR_FRAMES, 0, 0, SPR, SPR);
		memcpy(sprites + (size_t)f * SPR * SPR, cbuf, SPR * SPR * 2);
	}
	rw = save_w;
	rh = save_h;
}

/* blit sprite frame f to the screen at x, y (no scaling) */
static void blit_sprite(int f, int x0, int y0)
{
	const uint16_t *src = sprites + (size_t)f * SPR * SPR;
	int y, x;

	for (y = 0; y < SPR; y++, src += SPR) {
		if (fb_bpp == 16) {
			volatile uint32_t *row = (volatile uint32_t *)(fb + (size_t)(y0 + y) * fb_line + x0 * 2);

			for (x = 0; x < SPR; x += 2)
				row[x / 2] = src[x] | (uint32_t)src[x + 1] << 16;
		} else {
			volatile uint32_t *row = (volatile uint32_t *)(fb + (size_t)(y0 + y) * fb_line + x0 * 4);

			for (x = 0; x < SPR; x++)
				row[x] = rgb565_to_8888(src[x]);
		}
	}
}

static double run_sprites(int count, double seconds)
{
	double start = now();
	int frames = 0, i;

	while (!stop && now() - start < seconds) {
		for (i = 0; i < count; i++)
			blit_sprite((frames + i * 6) % SPR_FRAMES, 40 + (i % 3) * 200, 60 + (i / 3) * 200);
		frames++;
	}
	return frames / (now() - start);
}

/* ------------------------------------------------------------------ main */

int main(int argc, char **argv)
{
	static const int major[] = { 0, 25, 25, 50, 50, 100 }, minor[] = { 0, 5, 10, 10, 20, 20 };
	int quick = argc > 1 && !strcmp(argv[1], "--quick");
	double secs = quick ? 1.2 : 2.5, ms_r, ms_p, fps, t0;
	int bpp_list[2] = { 16, 32 }, b, m, drawn, i, nmodels = quick ? 4 : 6;
	struct fb_var_screeninfo v;

	signal(SIGINT, on_signal);
	signal(SIGTERM, on_signal);
	fbfd = open("/dev/fb0", O_RDWR | O_CLOEXEC);
	if (fbfd < 0 || ioctl(fbfd, FBIOGET_VSCREENINFO, &var0)) {
		perror("x7-bench3d: /dev/fb0");
		return 1;
	}
	orig_bpp = var0.bits_per_pixel;
	report = fopen("/share/x7-bench3d.txt", "w");
	if (!report)
		report = fopen("/tmp/x7-bench3d.txt", "w");
	/* pause the screen console so it doesn't draw over the test */
	ttyfd = open("/dev/tty1", O_RDWR | O_CLOEXEC);
	if (ttyfd >= 0)
		ioctl(ttyfd, KDSETMODE, KD_GRAPHICS);
	if (ioctl(fbfd, FBIOGET_VSCREENINFO, &v) == 0) {
		struct fb_fix_screeninfo f;

		ioctl(fbfd, FBIOGET_FSCREENINFO, &f);
		fb_size = f.smem_len;
	}
	fb = mmap(NULL, fb_size, PROT_READ | PROT_WRITE, MAP_SHARED, fbfd, 0);
	if (fb == MAP_FAILED) {
		perror("x7-bench3d: mmap");
		restore();
		return 1;
	}
	make_texture();
	out("X7 Game 3D benchmark (software rendering: the console has no 3D GPU)\n");
	out("CPU: MIPS 74Kc, 1 core, 900 MHz; screen 640x480; each test %.1f s\n\n", secs);

	out("1. Filling the whole screen (the minimum cost of a full-screen frame)\n");
	for (b = 0; b < 2 && !stop; b++) {
		int n = 0;

		if (set_bpp(bpp_list[b])) {
			out("   %d-bit: mode not available\n", bpp_list[b]);
			continue;
		}
		t0 = now();
		while (!stop && now() - t0 < secs / 2) {
			fb_fill(n & 1 ? 0x00000000u : (fb_bpp == 16 ? 0x18e318e3u : 0xff203040u));
			n++;
		}
		out("   %d-bit: %.1f ms per full frame (max %.0f frames/s with nothing drawn)\n",
		    fb_bpp, (now() - t0) * 1000 / n, n / (now() - t0));
	}

	out("\n2. Spinning textured, lit model (affine texture 64x64, Gouraud, z-buffer)\n");
	out("   %-10s %-7s %-6s %9s %9s %10s %8s\n", "render", "screen", "tris", "drawn", "fps",
	    "3D ms", "copy ms");
	for (b = 0; b < 2 && !stop; b++) {
		if (set_bpp(bpp_list[b]))
			continue;
		rw = 320;
		rh = 240;
		for (m = 0; m < nmodels && !stop; m++) {
			if (m == 0)
				make_cube();
			else
				make_torus(major[m], minor[m]);
			fps = run_3d(secs, &ms_r, &ms_p, &drawn);
			out("   %-10s %-7s %-6d %9d %9.1f %10.1f %8.1f\n", "320x240", bpp_list[b] == 16 ? "16-bit" : "32-bit",
			    ntris, drawn, fps, ms_r, ms_p);
		}
	}
	if (!stop && set_bpp(16) == 0) {
		rw = 640;
		rh = 480;
		for (i = 2; i <= 4 && !stop; i += 2) {
			make_torus(major[i], minor[i]);
			fps = run_3d(secs, &ms_r, &ms_p, &drawn);
			out("   %-10s %-7s %-6d %9d %9.1f %10.1f %8.1f\n", "640x480", "16-bit", ntris, drawn, fps, ms_r, ms_p);
		}
	}

	out("\n3. Pre-rendered 36-frame turntable sprites (160x160 each, no 3D at run time)\n");
	if (!stop) {
		rw = 320;
		rh = 240;
		prerender_sprites();
		for (b = 0; b < 2 && !stop; b++) {
			if (set_bpp(bpp_list[b]))
				continue;
			fb_fill(0);
			for (i = 1; i <= 6 && !stop; i += 5)
				out("   %d-bit: %d sprite%s: %.1f frames/s\n", fb_bpp, i, i > 1 ? "s" : "",
				    run_sprites(i, secs));
		}
	}
	out("\n%s. Saved to %s\n", stop ? "Stopped early" : "Done",
	    access("/share", W_OK) == 0 ? "/share/x7-bench3d.txt (X7DATA)" : "/tmp/x7-bench3d.txt");
	restore();
	if (report)
		fclose(report);
	return 0;
}

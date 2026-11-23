// SPDX-License-Identifier: GPL-3.0-or-later
/*
 * x7-fbspeed - how fast can a program write the screen?
 *
 * Writes full 640x480 16-bit frames into /dev/fb0 for about 2 s, the way the
 * emulators do (sequential 32-bit stores), and prints the time per frame:
 * first with the normal uncached mapping, then write-combined ("uncached
 * accelerated", kernel patch 0018, /sys/module/hc16xx_gma_fb/parameters/
 * mmap_wc) if the kernel has that switch. After each run it reads a few
 * pixels back to check they all arrived. The screen shows colour bars while
 * it runs; the game list redraws itself at the next button press.
 *
 *   x7-fbspeed            both modes
 *   x7-fbspeed uc|wc      one mode
 */
#define _GNU_SOURCE
#include <fcntl.h>
#include <linux/fb.h>
#include <linux/kd.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <time.h>
#include <unistd.h>

#define WC_PARAM	"/sys/module/hc16xx_gma_fb/parameters/mmap_wc"
#define RUN_SECONDS	2.0

static double now(void)
{
	struct timespec ts;

	clock_gettime(CLOCK_MONOTONIC, &ts);
	return ts.tv_sec + ts.tv_nsec / 1e9;
}

static int read_param(void)
{
	char c = 0;
	int fd = open(WC_PARAM, O_RDONLY | O_CLOEXEC);

	if (fd < 0)
		return -1;
	if (read(fd, &c, 1) != 1)
		c = 0;
	close(fd);
	return c == 'Y' || c == '1';
}

static int write_param(int on)
{
	int fd = open(WC_PARAM, O_WRONLY | O_CLOEXEC), ok;

	if (fd < 0)
		return -1;
	ok = write(fd, on ? "1\n" : "0\n", 2) == 2;
	close(fd);
	return ok ? 0 : -1;
}

/* one run: returns ms per frame, -1 on error; *bad = pixels that didn't arrive */
static double run(int fd, size_t map_len, unsigned int pitch32, int *bad)
{
	volatile uint32_t *fb;
	uint32_t row[320];
	double t0, t;
	int frames = 0, x, y;

	fb = mmap(NULL, map_len, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
	if (fb == MAP_FAILED) {
		perror("x7-fbspeed: mmap");
		return -1;
	}
	t0 = now();
	do {
		uint32_t c = (uint32_t)frames * 0x08210821u;

		for (x = 0; x < 320; x++)		/* 8 colour bars that move */
			row[x] = c + (uint32_t)(x / 40) * 0x18e318e3u;
		for (y = 0; y < 480; y++) {
			volatile uint32_t *d = fb + (size_t)y * pitch32;

			for (x = 0; x < 320; x++)
				d[x] = row[x];
		}
		frames++;
		t = now() - t0;
	} while (t < RUN_SECONDS);
	/* every pixel of the last frame must be there (read through the same
	 * mapping: slow, but only a few) */
	*bad = 0;
	for (y = 0; y < 480; y += 37)
		for (x = 0; x < 320; x += 23)
			if (fb[(size_t)y * pitch32 + x] != row[x])
				(*bad)++;
	munmap((void *)fb, map_len);
	return t * 1000.0 / frames;
}

int main(int argc, char **argv)
{
	struct fb_var_screeninfo v, orig;
	struct fb_fix_screeninfo f;
	int fd, tty, was, want_uc = 1, want_wc = 1, bad;
	double ms;

	if (argc > 1) {
		want_uc = !strcmp(argv[1], "uc");
		want_wc = !strcmp(argv[1], "wc");
		if (!want_uc && !want_wc) {
			fprintf(stderr, "usage: x7-fbspeed [uc|wc]\n");
			return 2;
		}
	}
	fd = open("/dev/fb0", O_RDWR | O_CLOEXEC);
	if (fd < 0 || ioctl(fd, FBIOGET_VSCREENINFO, &orig)) {
		perror("x7-fbspeed: /dev/fb0");
		return 1;
	}
	tty = open("/dev/tty0", O_RDWR | O_CLOEXEC);
	if (tty >= 0)
		ioctl(tty, KDSETMODE, KD_GRAPHICS);	/* console off first */
	v = orig;
	v.bits_per_pixel = 16;
	v.activate = FB_ACTIVATE_NOW;
	if (ioctl(fd, FBIOPUT_VSCREENINFO, &v) || ioctl(fd, FBIOGET_VSCREENINFO, &v) ||
	    ioctl(fd, FBIOGET_FSCREENINFO, &f) || v.bits_per_pixel != 16) {
		fprintf(stderr, "x7-fbspeed: could not switch the screen to 16 bits\n");
		goto out;
	}
	was = read_param();
	if (want_uc) {
		if (was > 0)
			write_param(0);
		ms = run(fd, f.smem_len, f.line_length / 4, &bad);
		if (ms > 0)
			printf("uncached:       %6.2f ms per frame (%5.1f MB/s)%s\n", ms,
			       640.0 * 480 * 2 / ms / 1000, bad ? "  PIXELS MISSING" : "");
	}
	if (want_wc) {
		if (was < 0) {
			printf("write-combined: not available (this kernel has no mmap_wc switch)\n");
		} else if (write_param(1)) {
			printf("write-combined: could not switch it on (run as root)\n");
		} else {
			ms = run(fd, f.smem_len, f.line_length / 4, &bad);
			if (ms > 0)
				printf("write-combined: %6.2f ms per frame (%5.1f MB/s)%s\n", ms,
				       640.0 * 480 * 2 / ms / 1000,
				       bad ? "  PIXELS MISSING: don't use it" : "");
		}
	}
	if (was >= 0)
		write_param(was);		/* as it was */
out:
	orig.activate = FB_ACTIVATE_NOW;
	ioctl(fd, FBIOPUT_VSCREENINFO, &orig);
	if (tty >= 0)
		ioctl(tty, KDSETMODE, KD_TEXT);
	close(fd);
	return 0;
}

// SPDX-License-Identifier: GPL-3.0-or-later
/*
 * x7-browser - X7 Game's temporary game list, for testing emulation.
 *
 * Runs on the screen console (tty1, started by init) as a text-mode file
 * browser over /share/roms: pick a system, then a game; x7-launch starts the
 * emulator and the list comes back when it quits. The systems, their names
 * and their emulators come from /usr/share/x7game/systems.txt; a system is
 * listed when at least one of its emulators is installed.
 *
 *   D-pad up/down  move          D-pad left/right, L1/R1  page
 *   A              open / start  B                        back
 *   X              start with another emulator (systems that have several)
 *
 * The real X7 Game frontend replaces this once emulation is done.
 */
#define _GNU_SOURCE
#include <ctype.h>
#include <dirent.h>
#include <errno.h>
#include <fcntl.h>
#include <linux/fb.h>
#include <linux/input.h>
#include <linux/kd.h>
#include <poll.h>
#include <signal.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/stat.h>
#include <sys/statvfs.h>
#include <sys/wait.h>
#include <termios.h>
#include <time.h>
#include <unistd.h>

#define SYSTEMS_FILE	"/usr/share/x7game/systems.txt"
#define ROMS		"/share/roms"
#define LAUNCH		"/usr/bin/x7-launch"
#define EVENT_LOG	"/run/x7-events.log"
#define PAD_NAME	"X7 Game Gamepad"
#define MAX_SYSTEMS	64
#define MAX_EMUS	4
#define MAX_IN		8
/* the depth the screen console boots in (hc16xx-gma-fb starts in ARGB8888);
 * RetroArch's x7fb switches /dev/fb0 to 16 bits while a game runs */
#define CONSOLE_BPP	32
/* free space on X7DATA below which saves may no longer fit */
#define SHARE_LOW	(8ULL << 20)

/* colours (Linux console) */
#define C_HEAD	"\033[0;1;37;44m"
#define C_SUB	"\033[0;36m"
#define C_TEXT	"\033[0;37m"
#define C_DIR	"\033[0;1;33m"
#define C_DIM	"\033[0;1;30m"
#define C_SEL	"\033[0;30;46m"
#define C_FOOT	"\033[0;30;47m"
#define C_MSG	"\033[0;1;31m"

enum { K_UP, K_DOWN, K_LEFT, K_RIGHT, K_A, K_B, K_X, K_Y, K_L1, K_R1,
       K_START, K_SELECT, K_COUNT };

struct system {
	char folder[32];
	char name[64];
	char emu[MAX_EMUS][32];
	int nemu;
};

struct entry {
	char *name;
	int dir;
};

struct list {
	struct entry *e;
	int n, cap;
};

static struct system sys[MAX_SYSTEMS];
static int nsys;
static int rows = 30, cols = 80;
static char msg[160];

/* ----------------------------------------------------------------- input */

static int in_fd[MAX_IN], nin;
static int held[K_COUNT];
static int hat_x, hat_y;
static int queue[16], qhead, qtail;
static int rep_key = -1;
static long long rep_at;

#define LONG_BITS (8 * sizeof(long))
#define TEST(bits, n) ((bits[(n) / LONG_BITS] >> ((n) % LONG_BITS)) & 1)

static long long now_ms(void)
{
	struct timespec ts;

	clock_gettime(CLOCK_MONOTONIC, &ts);
	return ts.tv_sec * 1000LL + ts.tv_nsec / 1000000;
}

static void close_inputs(void)
{
	while (nin > 0)
		close(in_fd[--nin]);
	memset(held, 0, sizeof(held));
	hat_x = hat_y = 0;
	qhead = qtail = 0;
	rep_key = -1;
}

/* want_pad: open only the virtual pad; else every device with buttons */
static int scan_inputs(int want_pad)
{
	DIR *d = opendir("/dev/input");
	struct dirent *e;

	if (!d)
		return 0;
	while ((e = readdir(d)) && nin < MAX_IN) {
		unsigned long keys[(KEY_MAX + LONG_BITS) / LONG_BITS];
		char path[288], name[96] = "";
		int fd, ok;

		if (strncmp(e->d_name, "event", 5))
			continue;
		snprintf(path, sizeof(path), "/dev/input/%s", e->d_name);
		fd = open(path, O_RDONLY | O_NONBLOCK | O_CLOEXEC);
		if (fd < 0)
			continue;
		ioctl(fd, EVIOCGNAME(sizeof(name)), name);
		memset(keys, 0, sizeof(keys));
		ioctl(fd, EVIOCGBIT(EV_KEY, sizeof(keys)), keys);
		if (want_pad)
			ok = !strcmp(name, PAD_NAME);
		else
			ok = strcmp(name, PAD_NAME) &&
			     (TEST(keys, BTN_SOUTH) || TEST(keys, BTN_DPAD_UP));
		if (ok)
			in_fd[nin++] = fd;
		else
			close(fd);
	}
	closedir(d);
	return nin;
}

/* the virtual pad (x7-padd) if it comes up within wait_ms, else the raw
 * button devices */
static void open_inputs(int wait_ms)
{
	long long end = now_ms() + wait_ms;

	close_inputs();
	for (;;) {
		if (scan_inputs(1))
			return;
		if (now_ms() >= end)
			break;
		usleep(100000);
	}
	scan_inputs(0);
}

static void key_change(int k, int down)
{
	if (k < 0 || held[k] == down)
		return;
	held[k] = down;
	if (down) {
		if ((qtail + 1) % 16 != qhead) {
			queue[qtail] = k;
			qtail = (qtail + 1) % 16;
		}
		if (k <= K_RIGHT || k == K_L1 || k == K_R1) {
			rep_key = k;
			rep_at = now_ms() + 350;
		}
	} else if (rep_key == k) {
		rep_key = -1;
	}
}

static int key_of(unsigned int code)
{
	switch (code) {
	case BTN_DPAD_UP:	return K_UP;
	case BTN_DPAD_DOWN:	return K_DOWN;
	case BTN_DPAD_LEFT:	return K_LEFT;
	case BTN_DPAD_RIGHT:	return K_RIGHT;
	case BTN_EAST:		return K_A;
	case BTN_SOUTH:		return K_B;
	case BTN_NORTH:		return K_X;
	case BTN_WEST:		return K_Y;
	case BTN_TL:		return K_L1;
	case BTN_TR:		return K_R1;
	case BTN_START:		return K_START;
	case BTN_SELECT:	return K_SELECT;
	}
	return -1;
}

static void handle(const struct input_event *ev)
{
	if (ev->type == EV_KEY && ev->value != 2) {
		key_change(key_of(ev->code), ev->value != 0);
	} else if (ev->type == EV_ABS && ev->code == ABS_HAT0X) {
		hat_x = ev->value;
		key_change(K_LEFT, hat_x < 0);
		key_change(K_RIGHT, hat_x > 0);
	} else if (ev->type == EV_ABS && ev->code == ABS_HAT0Y) {
		hat_y = ev->value;
		key_change(K_UP, hat_y < 0);
		key_change(K_DOWN, hat_y > 0);
	}
}

/* wait up to wait ms (-1: no limit) for button events and take them in */
static void read_events(int wait)
{
	struct pollfd fds[MAX_IN];
	int i;

	for (i = 0; i < nin; i++) {
		fds[i].fd = in_fd[i];
		fds[i].events = POLLIN;
	}
	if (poll(fds, nin, wait) <= 0)
		return;
	for (i = 0; i < nin; i++) {
		struct input_event ev[32];
		ssize_t r;
		int k;

		if (!(fds[i].revents & (POLLIN | POLLERR | POLLHUP)))
			continue;
		r = read(in_fd[i], ev, sizeof(ev));
		if (r < 0 && errno == ENODEV) {
			open_inputs(0);
			break;
		}
		for (k = 0; r > 0 && k < r / (ssize_t)sizeof(ev[0]); k++)
			handle(&ev[k]);
	}
}

/* the next button press (with auto-repeat), or -1 after timeout_ms */
static int get_key(int timeout_ms)
{
	long long end = timeout_ms < 0 ? -1 : now_ms() + timeout_ms;
	int fresh = 0;

	for (;;) {
		long long t = now_ms();
		int wait;

		if (qhead != qtail) {
			int k = queue[qhead];

			qhead = (qhead + 1) % 16;
			return k;
		}
		if (rep_key >= 0 && t >= rep_at) {
			/* a redraw slower than the repeat leaves the button's
			 * release unread: take in what is pending first, or a
			 * released key keeps moving the selection by itself */
			if (!fresh && nin > 0) {
				fresh = 1;
				read_events(0);
				continue;
			}
			rep_at = t + 70;
			return rep_key;
		}
		if (end >= 0 && t >= end)
			return -1;
		wait = -1;
		if (rep_key >= 0)
			wait = (int)(rep_at - t);
		if (end >= 0 && (wait < 0 || end - t < wait))
			wait = (int)(end - t);
		if (nin == 0) {
			/* no buttons yet: look again now and then */
			usleep(500000);
			if (!scan_inputs(1))
				scan_inputs(0);
			continue;
		}
		read_events(wait);
		fresh = 1;
	}
}

/* --------------------------------------------------------------- drawing */

static char out[32768];
static size_t outlen;

static void put(const char *fmt, ...)
{
	va_list ap;
	int n;

	if (outlen >= sizeof(out) - 1)
		return;
	va_start(ap, fmt);
	n = vsnprintf(out + outlen, sizeof(out) - outlen, fmt, ap);
	va_end(ap);
	if (n > 0)
		outlen += (size_t)n < sizeof(out) - outlen ? (size_t)n : sizeof(out) - outlen - 1;
}

static void flush_out(void)
{
	size_t done = 0;

	while (done < outlen) {
		ssize_t w = write(1, out + done, outlen - done);

		if (w <= 0 && errno != EINTR)
			break;
		if (w > 0)
			done += w;
	}
	outlen = 0;
}

/* one screen row: text cut or padded to the width (UTF-8 aware) */
static void row(int y, const char *attr, const char *text)
{
	int w = 0;
	const char *p = text;

	put("\033[%d;1H%s", y, attr);
	while (*p && w < cols) {
		const char *s = p++;

		while ((*p & 0xc0) == 0x80)
			p++;
		if ((unsigned char)*s >= 0x20 || (*s & 0x80))
			put("%.*s", (int)(p - s), s);
		else
			put("?");
		w++;
	}
	put("%*s", cols - w, "");
}

static void draw(const char *title, const char *sub, char **label,
		 const char **attr, int n, int sel, int top, const char *help)
{
	int lines = rows - 4, i;
	char head[128];

	snprintf(head, sizeof(head), " X7 Game  %s", title);
	row(1, C_HEAD, head);
	row(2, C_SUB, sub);
	for (i = 0; i < lines; i++) {
		int k = top + i;
		char buf[512];

		if (k < n) {
			snprintf(buf, sizeof(buf), " %s", label[k]);
			row(3 + i, k == sel ? C_SEL : attr[k], buf);
		} else {
			row(3 + i, C_TEXT, "");
		}
	}
	row(rows - 1, C_MSG, msg);
	row(rows, C_FOOT, help);
	put("\033[0m");
	flush_out();
}

/* move the selection; returns 1 if the key was a movement key */
static int move(int k, int n, int *sel, int *top)
{
	int page = rows - 4;

	if (n <= 0)
		return k == K_UP || k == K_DOWN || k == K_LEFT || k == K_RIGHT;
	switch (k) {
	case K_UP:	*sel = *sel > 0 ? *sel - 1 : n - 1;	break;
	case K_DOWN:	*sel = *sel < n - 1 ? *sel + 1 : 0;	break;
	case K_LEFT:
	case K_L1:	*sel = *sel > page ? *sel - page : 0;	break;
	case K_RIGHT:
	case K_R1:	*sel = *sel + page < n ? *sel + page : n - 1; break;
	default:	return 0;
	}
	if (*sel < *top)
		*top = *sel;
	if (*sel >= *top + page)
		*top = *sel - page + 1;
	return 1;
}

/* ------------------------------------------------------------- the files */

static int hidden(const char *name)
{
	static const char *const skip[] = {
		"txt", "nfo", "xml", "json", "jpg", "jpeg", "png", "gif", "bmp",
		"pdf", "md", "htm", "html", "srm", "sav", "state", "cfg", "ini",
		"db", "lpl", NULL,
	};
	const char *dot = strrchr(name, '.');
	int i;

	if (name[0] == '.')
		return 1;
	if (!dot)
		return 0;
	for (i = 0; skip[i]; i++)
		if (!strcasecmp(dot + 1, skip[i]))
			return 1;
	return 0;
}

static int by_name(const void *a, const void *b)
{
	const struct entry *x = a, *y = b;

	if (x->dir != y->dir)
		return y->dir - x->dir;		/* folders first */
	return strcasecmp(x->name, y->name);
}

static void free_list(struct list *l)
{
	int i;

	for (i = 0; i < l->n; i++)
		free(l->e[i].name);
	free(l->e);
	memset(l, 0, sizeof(*l));
}

static void load_list(struct list *l, const char *path)
{
	DIR *d = opendir(path);
	struct dirent *e;

	free_list(l);
	if (!d)
		return;
	while ((e = readdir(d))) {
		int dir;

		if (hidden(e->d_name))
			continue;
		/* exFAT and FAT give the type with the name; stat() only
		 * when it is unknown, or to follow a link */
		if (e->d_type == DT_DIR || e->d_type == DT_REG) {
			dir = e->d_type == DT_DIR;
		} else if (e->d_type == DT_UNKNOWN || e->d_type == DT_LNK) {
			char full[1280];
			struct stat st;

			snprintf(full, sizeof(full), "%s/%s", path, e->d_name);
			if (stat(full, &st) || !(S_ISDIR(st.st_mode) || S_ISREG(st.st_mode)))
				continue;
			dir = S_ISDIR(st.st_mode);
		} else {
			continue;
		}
		if (l->n == l->cap) {
			int cap = l->cap ? l->cap * 2 : 64;
			struct entry *ne = realloc(l->e, cap * sizeof(*ne));

			if (!ne)
				break;
			l->e = ne;
			l->cap = cap;
		}
		l->e[l->n].name = strdup(e->d_name);
		l->e[l->n].dir = dir;
		if (l->e[l->n].name)
			l->n++;
	}
	closedir(d);
	qsort(l->e, l->n, sizeof(l->e[0]), by_name);
}

static int count_games(const char *folder)
{
	char path[256];
	DIR *d;
	struct dirent *e;
	int n = 0;

	snprintf(path, sizeof(path), "%s/%s", ROMS, folder);
	d = opendir(path);
	if (!d)
		return 0;
	while ((e = readdir(d)))
		if (strcmp(e->d_name, ".") && strcmp(e->d_name, "..") && !hidden(e->d_name))
			n++;
	closedir(d);
	return n;
}

/* ---------------------------------------------------- systems, emulators */

static int emu_installed(const char *emu)
{
	char path[128];

	if (!strcmp(emu, "pcsx4all"))
		return access("/usr/bin/pcsx4all", X_OK) == 0;
	snprintf(path, sizeof(path), "/usr/lib/libretro/%s_libretro.so", emu);
	return access(path, R_OK) == 0;
}

static const char *emu_label(const char *emu, char *buf, size_t len)
{
	if (!strcmp(emu, "pcsx4all"))
		snprintf(buf, len, "PCSX4All");
	else
		snprintf(buf, len, "RetroArch: %s", emu);
	return buf;
}

/* systems.txt: "folder  emulator[,emulator...]  Name of the system" */
static void load_systems(void)
{
	FILE *f = fopen(SYSTEMS_FILE, "re");
	char line[256];

	nsys = 0;
	if (!f)
		return;
	while (fgets(line, sizeof(line), f) && nsys < MAX_SYSTEMS) {
		char folder[32], emus[160], *name, *tok, *save;
		struct system *s = &sys[nsys];
		int used;

		if (line[0] == '#' || sscanf(line, "%31s %159s %n", folder, emus, &used) < 2)
			continue;
		name = line + used;
		name[strcspn(name, "\r\n")] = 0;
		memset(s, 0, sizeof(*s));
		snprintf(s->folder, sizeof(s->folder), "%s", folder);
		snprintf(s->name, sizeof(s->name), "%s", *name ? name : folder);
		for (tok = strtok_r(emus, ",", &save); tok && s->nemu < MAX_EMUS;
		     tok = strtok_r(NULL, ",", &save))
			if (emu_installed(tok))
				snprintf(s->emu[s->nemu++], sizeof(s->emu[0]), "%s", tok);
		if (s->nemu)
			nsys++;
	}
	fclose(f);
}

/* --------------------------------------------------------------- running */

static void screen_setup(void)
{
	struct termios t;
	struct winsize ws;

	ioctl(0, KDSETMODE, KD_TEXT);
	if (tcgetattr(0, &t) == 0) {
		t.c_lflag &= ~(ECHO | ICANON);
		tcsetattr(0, TCSANOW, &t);
	}
	if (ioctl(1, TIOCGWINSZ, &ws) == 0 && ws.ws_row >= 10 && ws.ws_col >= 40) {
		rows = ws.ws_row;
		cols = ws.ws_col;
	}
	/* no cursor, no line wrap, clear */
	put("\033[0m\033[?25l\033[?7l\033[2J");
	flush_out();
}

/* Put /dev/fb0 back in the console's depth after a game. An emulator that
 * crashed or was killed never restores it, and even after a clean exit fbcon
 * can put back the 16-bit mode it last saw. Call it in KD_TEXT only: in
 * KD_GRAPHICS fbcon doesn't take note of the change and puts its old mode
 * back at the next switch to KD_TEXT. */
static void console_depth(void)
{
	struct fb_var_screeninfo v;
	int fd;

	/* an emulator that crashed may have left the display's hardware
	 * scaling on (kernel patch 0019): the text needs it off */
	fd = open("/sys/bus/platform/devices/1883a000.framebuffer/scale", O_WRONLY | O_CLOEXEC);
	if (fd >= 0) {
		ssize_t r = write(fd, "off", 3);

		(void)r;	/* an old kernel without it: nothing to undo */
		close(fd);
	}
	fd = open("/dev/fb0", O_RDWR | O_CLOEXEC);
	if (fd < 0)
		return;
	if (ioctl(fd, FBIOGET_VSCREENINFO, &v) == 0 && v.bits_per_pixel != CONSOLE_BPP) {
		v.bits_per_pixel = CONSOLE_BPP;
		v.activate = FB_ACTIVATE_NOW;
		ioctl(fd, FBIOPUT_VSCREENINFO, &v);
	}
	close(fd);
}

/* Is an emulator already running (started from the USB shell with
 * x7-launch, which execs it, so it shows under its own name)? */
static int game_running(void)
{
	DIR *d = opendir("/proc");
	struct dirent *e;
	int found = 0;

	if (!d)
		return 0;
	while (!found && (e = readdir(d))) {
		char path[288], comm[32];
		ssize_t r;
		int fd;

		if (!isdigit((unsigned char)e->d_name[0]))
			continue;
		snprintf(path, sizeof(path), "/proc/%s/comm", e->d_name);
		fd = open(path, O_RDONLY | O_CLOEXEC);
		if (fd < 0)
			continue;
		r = read(fd, comm, sizeof(comm) - 1);
		close(fd);
		if (r <= 0)
			continue;
		comm[r] = 0;
		comm[strcspn(comm, "\n")] = 0;
		found = !strcmp(comm, "retroarch") || !strcmp(comm, "pcsx4all");
	}
	closedir(d);
	return found;
}

/* Why games may not save on X7DATA, or NULL. The exFAT driver turns the
 * partition read-only after an error; a full card fails the same way.
 * Only when X7DATA is mounted: the root file system under an empty /share is
 * read-only anyway, and the "not ready" message covers that case. */
static const char *share_problem(void)
{
	struct stat sh, root;
	struct statvfs v;

	if (stat("/share", &sh) || stat("/", &root) || sh.st_dev == root.st_dev)
		return NULL;
	if (statvfs("/share", &v))
		return NULL;
	if (v.f_flag & ST_RDONLY)
		return "X7DATA is read-only: games will not save. Check the card on a PC.";
	if ((unsigned long long)v.f_bavail * v.f_frsize < SHARE_LOW)
		return "X7DATA is almost full: games may not save.";
	return NULL;
}

/*
 * The main pad (D-pad, A, B, X, Y, L1, R1, SELECT, START) is a shift register
 * the kernel samples every 16 ms (device tree); it can't raise interrupts.
 * While a game runs it is sampled every 8 ms: half the input delay for about
 * 0.5 % more CPU. The input poller's "poll" file takes the new interval.
 */
#define PAD_POLL_GAME	8
#define PAD_POLL_IDLE	16

static void pad_poll(int ms)
{
	DIR *d = opendir("/sys/class/input");
	struct dirent *e;

	if (!d)
		return;
	while ((e = readdir(d))) {
		char path[300], name[64] = "";
		FILE *f;

		if (strncmp(e->d_name, "input", 5))
			continue;
		snprintf(path, sizeof(path), "/sys/class/input/%s/name", e->d_name);
		f = fopen(path, "re");
		if (!f)
			continue;
		if (!fgets(name, sizeof(name), f))
			name[0] = 0;
		fclose(f);
		name[strcspn(name, "\n")] = 0;
		if (strcmp(name, "serializer-keys"))
			continue;
		snprintf(path, sizeof(path), "/sys/class/input/%s/poll", e->d_name);
		f = fopen(path, "we");
		if (f) {
			fprintf(f, "%d\n", ms);
			fclose(f);
		}
	}
	closedir(d);
}

static void launch(const char *emu, const char *path, const char *game)
{
	char label[64];
	pid_t pid;
	int status = 0;

	/* A game started from the USB shell owns the screen, and this list
	 * sees the same buttons: a second emulator would fight it for the
	 * screen, the buttons and the sound. Leave all of them alone. */
	if (game_running()) {
		snprintf(msg, sizeof(msg), "A game is already running (started from the USB shell?)");
		return;
	}

	snprintf(msg, sizeof(msg), "Starting %s (%s)...", game, emu_label(emu, label, sizeof(label)));
	row(rows - 1, C_MSG, msg);
	put("\033[0m");
	flush_out();
	msg[0] = 0;

	close_inputs();
	pad_poll(PAD_POLL_GAME);
	pid = fork();
	if (pid == 0) {
		signal(SIGPIPE, SIG_DFL);
		signal(SIGINT, SIG_DFL);
		signal(SIGQUIT, SIG_DFL);
		execl(LAUNCH, LAUNCH, emu, path, (char *)NULL);
		_exit(127);
	}
	if (pid > 0)
		while (waitpid(pid, &status, 0) < 0 && errno == EINTR)
			;
	pad_poll(PAD_POLL_IDLE);
	/* the emulator has just written its saves and its config: get them
	 * onto the card now, not at the next writeback ~30 s later, in case
	 * the console hangs or loses power before that */
	sync();
	/* back from the game: our screen (text mode first, then the depth),
	 * our buttons */
	screen_setup();
	console_depth();
	open_inputs(1000);
	if (pid < 0)
		snprintf(msg, sizeof(msg), "Could not start the emulator.");
	else if (WIFSIGNALED(status))
		snprintf(msg, sizeof(msg), "The emulator crashed (signal %d). Log: /share/system/logs/last-game.log",
			 WTERMSIG(status));
	else if (WIFEXITED(status) && WEXITSTATUS(status))
		snprintf(msg, sizeof(msg), "The emulator stopped with error %d. Log: /share/system/logs/last-game.log",
			 WEXITSTATUS(status));
}

static int choose_emu(const struct system *s, const char *game)
{
	char *label[MAX_EMUS], buf[MAX_EMUS][64];
	const char *attr[MAX_EMUS];
	char sub[256];
	int i, sel = 0, top = 0;

	for (i = 0; i < s->nemu; i++) {
		label[i] = (char *)emu_label(s->emu[i], buf[i], sizeof(buf[i]));
		attr[i] = C_TEXT;
	}
	snprintf(sub, sizeof(sub), " Start %s with:", game);
	for (;;) {
		int k;

		draw(s->name, sub, label, attr, s->nemu, sel, top, " A start   B back");
		k = get_key(-1);
		if (move(k, s->nemu, &sel, &top))
			continue;
		if (k == K_A)
			return sel;
		if (k == K_B)
			return -1;
	}
}

static void browse(const struct system *s, const char *rel)
{
	struct list l = { 0 };
	char path[1024], sub[1024], help[128];
	char **label = NULL;
	const char **attr = NULL;
	int sel = 0, top = 0, reload = 1, i;

	snprintf(path, sizeof(path), "%s/%s%s%s", ROMS, s->folder, *rel ? "/" : "", rel);
	snprintf(help, sizeof(help), " A start   B back   L1/R1 page%s",
		 s->nemu > 1 ? "   X other emulator" : "");
	for (;;) {
		int k;

		if (reload) {
			load_list(&l, path);
			free(label);
			free(attr);
			label = calloc(l.n + 1, sizeof(*label));
			attr = calloc(l.n + 1, sizeof(*attr));
			if (!label || !attr)
				break;
			for (i = 0; i < l.n; i++) {
				label[i] = l.e[i].name;
				attr[i] = l.e[i].dir ? C_DIR : C_TEXT;
			}
			if (sel >= l.n)
				sel = l.n ? l.n - 1 : 0;
			reload = 0;
		}
		snprintf(sub, sizeof(sub), " X7DATA/roms/%s%s%s   (%d)", s->folder,
			 *rel ? "/" : "", rel, l.n);
		if (l.n == 0 && !msg[0])
			snprintf(msg, sizeof(msg), "Nothing here yet: copy games to X7DATA/roms/%s on a PC.",
				 s->folder);
		draw(s->name, sub, label, attr, l.n, sel, top, help);
		k = get_key(-1);
		if (k != K_A && k != K_X)
			msg[0] = 0;
		if (move(k, l.n, &sel, &top))
			continue;
		if (k == K_B)
			break;
		if ((k == K_A || k == K_X) && l.n > 0) {
			struct entry *e = &l.e[sel];
			char file[1280];	/* path + "/" + a name of up to 255 bytes */
			int emu = 0;

			msg[0] = 0;
			if (e->dir) {
				char nrel[512];

				if (k == K_X)
					continue;
				snprintf(nrel, sizeof(nrel), "%s%s%s", rel, *rel ? "/" : "", e->name);
				browse(s, nrel);
				reload = 1;
				continue;
			}
			if (k == K_X) {
				if (s->nemu < 2)
					continue;
				emu = choose_emu(s, e->name);
				if (emu < 0)
					continue;
			}
			snprintf(file, sizeof(file), "%s/%s", path, e->name);
			launch(s->emu[emu], file, e->name);
			reload = 1;
		}
	}
	free(label);
	free(attr);
	free_list(&l);
}

static char *dup_line(const char *s)
{
	static char empty[1];
	char *d = strdup(s);

	return d ? d : empty;
}

static void free_line(char *s)
{
	if (s && s[0])
		free(s);
}

static void info(void)
{
	char *label[400];
	const char *attr[400];
	int n = 0, sel = 0, top = 0, reload = 1, i;

	for (;;) {
		int k;

		if (reload) {
			char line[256];
			FILE *f;

			for (i = 0; i < n; i++)
				free_line(label[i]);
			n = 0;
			f = popen("/usr/bin/x7-hwmon --status 2>&1", "r");
			while (f && n < 200 && fgets(line, sizeof(line), f)) {
				line[strcspn(line, "\n")] = 0;
				attr[n] = C_TEXT;
				label[n++] = dup_line(line);
			}
			if (f)
				pclose(f);
			attr[n] = C_SUB;
			label[n++] = dup_line("--- hardware events (newest last) ---");
			f = fopen(EVENT_LOG, "re");
			if (f) {
				static char ring[150][160];
				int count = 0;

				while (fgets(ring[count % 150], sizeof(ring[0]), f))
					count++;
				fclose(f);
				for (i = count > 150 ? count - 150 : 0; i < count && n < 399; i++) {
					char *r = ring[i % 150];

					r[strcspn(r, "\n")] = 0;
					attr[n] = C_DIM;
					label[n++] = dup_line(r);
				}
			}
			if (sel >= n)
				sel = n - 1;
			reload = 0;
		}
		draw("System information", " State of the console and its latest hardware events",
		     label, attr, n, sel, top, " A refresh   B back");
		k = get_key(-1);
		if (move(k, n, &sel, &top))
			continue;
		if (k == K_A)
			reload = 1;
		if (k == K_B)
			break;
	}
	for (i = 0; i < n; i++)
		free_line(label[i]);
}

/*
 * X7DATA was not closed cleanly (S05x7data leaves /run/x7-data.dirty): ask
 * before showing any games whether to check and repair it. The real
 * frontend will ask the same.
 */
static void repair_prompt(void)
{
	static const char *const text[] = {
		"X7DATA (your games and saves) was not closed cleanly last time,",
		"for example because the battery ran out or the console hung.",
		"It may be damaged, and games may then fail to save.",
		"",
		"Check and repair it now? It takes about a minute on a big card.",
		"",
		"  A   check and repair (recommended)",
		"  B   not now (you will be asked again at the next start)",
	};
	char *label[8];
	const char *attr[8];
	pid_t pid;
	int i, k, status = 0;

	if (access("/run/x7-data.dirty", F_OK))
		return;
	for (i = 0; i < 8; i++) {
		label[i] = (char *)text[i];
		attr[i] = C_TEXT;
	}
	do {
		draw("X7DATA check", "", label, attr, 8, -1, 0, " A repair   B not now");
		k = get_key(-1);
	} while (k != K_A && k != K_B);
	if (k == K_B)
		return;

	/* let x7-datarepair print on the console as it goes */
	put("\033[0m\033[2J\033[H\033[?7h");
	flush_out();
	pid = fork();
	if (pid == 0) {
		signal(SIGPIPE, SIG_DFL);
		signal(SIGINT, SIG_DFL);
		signal(SIGQUIT, SIG_DFL);
		execl("/usr/sbin/x7-datarepair", "x7-datarepair", (char *)NULL);
		_exit(127);
	}
	if (pid > 0)
		while (waitpid(pid, &status, 0) < 0 && errno == EINTR)
			;
	put("\nPress A to continue.\n");
	flush_out();
	/* buttons pressed during the check are stale */
	open_inputs(1000);
	while (get_key(-1) != K_A)
		;
	screen_setup();
	if (pid < 0 || !WIFEXITED(status) || WEXITSTATUS(status) >= 2)
		snprintf(msg, sizeof(msg), "X7DATA still has problems: check the card on a PC.");
}

int main(void)
{
	char *label[MAX_SYSTEMS + 1], buf[MAX_SYSTEMS][128];
	const char *attr[MAX_SYSTEMS + 1];
	int sel = 0, top = 0, n, recount = 1;

	signal(SIGCHLD, SIG_DFL);
	signal(SIGPIPE, SIG_IGN);
	signal(SIGINT, SIG_IGN);
	signal(SIGQUIT, SIG_IGN);
	screen_setup();
	open_inputs(3000);
	repair_prompt();
	load_systems();
	n = nsys + 1;

	for (;;) {
		const char *warn;
		int i, k;

		/* the folders don't change while this list is shown: count the
		 * games only at the start and when coming back from a system
		 * or the information page, not at every key */
		if (recount) {
			for (i = 0; i < nsys; i++) {
				int g = count_games(sys[i].folder);

				if (g)
					snprintf(buf[i], sizeof(buf[i]), "%-44s %5d", sys[i].name, g);
				else
					snprintf(buf[i], sizeof(buf[i]), "%-44s    --", sys[i].name);
				label[i] = buf[i];
				attr[i] = g ? C_TEXT : C_DIM;
			}
			label[nsys] = (char *)"System information";
			attr[nsys] = C_SUB;
			recount = 0;
		}
		if (access(ROMS, F_OK) && !msg[0])
			snprintf(msg, sizeof(msg), "The data partition (X7DATA) is not ready: no games to show.");
		if (!msg[0] && (warn = share_problem()))
			snprintf(msg, sizeof(msg), "%s", warn);
		draw("test game list", " Systems                                       games", label, attr,
		     n, sel, top, " A open   D-pad move   L1/R1 page");
		k = get_key(-1);
		msg[0] = 0;
		if (move(k, n, &sel, &top))
			continue;
		if (k != K_A)
			continue;
		if (sel == nsys)
			info();
		else
			browse(&sys[sel], "");
		recount = 1;
	}
}

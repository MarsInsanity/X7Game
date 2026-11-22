// SPDX-License-Identifier: GPL-3.0-or-later
/*
 * x7-padd - one virtual gamepad for every emulator.
 *
 * The console's buttons come from two kernel input devices: the shift
 * register (D-pad, A, B, X, Y, L1, R1, SELECT, START) and the directly wired
 * keys (L2, R2, FN, VOL+, VOL-). Emulators want ONE gamepad, so this daemon
 * reads both and feeds a uinput device "X7 Game Gamepad":
 *
 *   buttons  BTN_SOUTH (B)  BTN_EAST (A)  BTN_NORTH (X)  BTN_WEST (Y)
 *            BTN_TL (L1)  BTN_TR (R1)  BTN_TL2 (L2)  BTN_TR2 (R2)
 *            BTN_SELECT  BTN_START  BTN_MODE (FN)
 *   D-pad    ABS_HAT0X / ABS_HAT0Y (-1, 0, 1)
 *   sticks   ABS_X / ABS_Y, always centred: with an axis present,
 *            libudev(-zero) and SDL treat the device as a joystick, while
 *            the two raw devices (no axes) are ignored by them.
 *
 * Volume and power keys are not forwarded (x7-hwmon handles them). The raw
 * devices are not grabbed, so x7-hwmon still sees every press.
 */
#define _GNU_SOURCE
#include <dirent.h>
#include <errno.h>
#include <fcntl.h>
#include <linux/input.h>
#include <linux/uinput.h>
#include <poll.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <unistd.h>

#define PAD_NAME	"X7 Game Gamepad"
#define MAX_SRC		8

static const unsigned short buttons[] = {
	BTN_SOUTH, BTN_EAST, BTN_NORTH, BTN_WEST, BTN_TL, BTN_TR, BTN_TL2, BTN_TR2,
	BTN_SELECT, BTN_START, BTN_MODE,
};

static int src_fd[MAX_SRC], nsrc, ufd = -1;
static int dpad_up, dpad_down, dpad_left, dpad_right;

#define LONG_BITS (8 * sizeof(long))
#define TEST(bits, n) ((bits[(n) / LONG_BITS] >> ((n) % LONG_BITS)) & 1)

static int is_forwarded(unsigned int code)
{
	unsigned int i;

	if (code >= BTN_DPAD_UP && code <= BTN_DPAD_RIGHT)
		return 1;
	for (i = 0; i < sizeof(buttons) / sizeof(buttons[0]); i++)
		if (buttons[i] == code)
			return 1;
	return 0;
}

/* open every input device that has at least one of our buttons */
static void open_sources(void)
{
	DIR *d = opendir("/dev/input");
	struct dirent *e;

	if (!d)
		return;
	while ((e = readdir(d)) && nsrc < MAX_SRC) {
		unsigned long keys[(KEY_MAX + LONG_BITS) / LONG_BITS];
		char path[64], name[96] = "";
		unsigned int c;
		int fd, useful = 0;

		if (strncmp(e->d_name, "event", 5))
			continue;
		snprintf(path, sizeof(path), "/dev/input/%s", e->d_name);
		fd = open(path, O_RDONLY | O_NONBLOCK | O_CLOEXEC);
		if (fd < 0)
			continue;
		ioctl(fd, EVIOCGNAME(sizeof(name)), name);
		memset(keys, 0, sizeof(keys));
		if (strcmp(name, PAD_NAME) && ioctl(fd, EVIOCGBIT(EV_KEY, sizeof(keys)), keys) >= 0)
			for (c = BTN_MISC; c <= BTN_DPAD_RIGHT && !useful; c++)
				useful = TEST(keys, c) && is_forwarded(c);
		if (useful) {
			src_fd[nsrc++] = fd;
			fprintf(stderr, "x7-padd: reading %s (%s)\n", path, name);
		} else {
			close(fd);
		}
	}
	closedir(d);
}

static int setup_abs(int code, int min, int max)
{
	struct uinput_abs_setup a;

	memset(&a, 0, sizeof(a));
	a.code = code;
	a.absinfo.minimum = min;
	a.absinfo.maximum = max;
	return ioctl(ufd, UI_ABS_SETUP, &a);
}

static int create_pad(void)
{
	struct uinput_setup s;
	unsigned int i;

	ufd = open("/dev/uinput", O_WRONLY | O_NONBLOCK | O_CLOEXEC);
	if (ufd < 0) {
		perror("x7-padd: /dev/uinput");
		return -1;
	}
	ioctl(ufd, UI_SET_EVBIT, EV_KEY);
	ioctl(ufd, UI_SET_EVBIT, EV_ABS);
	ioctl(ufd, UI_SET_EVBIT, EV_SYN);
	for (i = 0; i < sizeof(buttons) / sizeof(buttons[0]); i++)
		ioctl(ufd, UI_SET_KEYBIT, buttons[i]);
	ioctl(ufd, UI_SET_ABSBIT, ABS_X);
	ioctl(ufd, UI_SET_ABSBIT, ABS_Y);
	ioctl(ufd, UI_SET_ABSBIT, ABS_HAT0X);
	ioctl(ufd, UI_SET_ABSBIT, ABS_HAT0Y);
	if (setup_abs(ABS_X, -32768, 32767) || setup_abs(ABS_Y, -32768, 32767) ||
	    setup_abs(ABS_HAT0X, -1, 1) || setup_abs(ABS_HAT0Y, -1, 1)) {
		perror("x7-padd: UI_ABS_SETUP");
		return -1;
	}
	memset(&s, 0, sizeof(s));
	s.id.bustype = BUS_VIRTUAL;
	s.id.vendor = 0x7767;		/* "wg" */
	s.id.product = 0x0001;
	s.id.version = 1;
	snprintf(s.name, sizeof(s.name), PAD_NAME);
	if (ioctl(ufd, UI_DEV_SETUP, &s) || ioctl(ufd, UI_DEV_CREATE)) {
		perror("x7-padd: UI_DEV_CREATE");
		return -1;
	}
	return 0;
}

static void emit(unsigned short type, unsigned short code, int value)
{
	struct input_event ev;

	memset(&ev, 0, sizeof(ev));
	ev.type = type;
	ev.code = code;
	ev.value = value;
	if (write(ufd, &ev, sizeof(ev)) < 0 && errno != EAGAIN)
		perror("x7-padd: write");
}

static void forward(const struct input_event *ev)
{
	if (ev->type != EV_KEY || ev->value == 2 || !is_forwarded(ev->code))
		return;
	switch (ev->code) {
	case BTN_DPAD_UP:	dpad_up = ev->value;	break;
	case BTN_DPAD_DOWN:	dpad_down = ev->value;	break;
	case BTN_DPAD_LEFT:	dpad_left = ev->value;	break;
	case BTN_DPAD_RIGHT:	dpad_right = ev->value;	break;
	default:
		emit(EV_KEY, ev->code, ev->value);
		emit(EV_SYN, SYN_REPORT, 0);
		return;
	}
	emit(EV_ABS, ABS_HAT0X, dpad_right - dpad_left);
	emit(EV_ABS, ABS_HAT0Y, dpad_down - dpad_up);
	emit(EV_SYN, SYN_REPORT, 0);
}

static void on_term(int sig)
{
	(void)sig;
	if (ufd >= 0)
		ioctl(ufd, UI_DEV_DESTROY);
	_exit(0);
}

int main(void)
{
	struct pollfd fds[MAX_SRC];
	int i, tries;

	signal(SIGTERM, on_term);
	signal(SIGINT, on_term);
	/* the button devices exist from boot; wait a little in case */
	for (tries = 0; tries < 20 && nsrc == 0; tries++) {
		open_sources();
		if (!nsrc)
			sleep(1);
	}
	if (!nsrc) {
		fprintf(stderr, "x7-padd: no button devices found\n");
		return 1;
	}
	if (create_pad())
		return 1;
	fprintf(stderr, "x7-padd: \"%s\" ready\n", PAD_NAME);

	for (i = 0; i < nsrc; i++) {
		fds[i].fd = src_fd[i];
		fds[i].events = POLLIN;
	}
	for (;;) {
		if (poll(fds, nsrc, -1) < 0) {
			if (errno == EINTR)
				continue;
			perror("x7-padd: poll");
			return 1;
		}
		for (i = 0; i < nsrc; i++) {
			struct input_event ev[32];
			ssize_t r;
			int k;

			if (!(fds[i].revents & POLLIN))
				continue;
			r = read(fds[i].fd, ev, sizeof(ev));
			for (k = 0; r > 0 && k < r / (ssize_t)sizeof(ev[0]); k++)
				forward(&ev[k]);
		}
	}
}

// SPDX-License-Identifier: GPL-3.0-or-later
/*
 * x7-hwmon - the X7 Game console's hardware monitor.
 *
 * Runs in the background (started by init, which discards its output). It
 * logs the state of the hardware once, then "Welcome to X7 Game!", then one
 * line for every hardware event to /run/x7-events.log (watch it over the USB
 * shell with "tail -f /run/x7-events.log"; /run is in RAM, so the log is cut
 * to its newest 64 KiB whenever it passes 256 KiB):
 *   - every button press and release (D-pad, A, B, X, Y, L1, L2, R1, R2,
 *     SELECT, START, FN, VOL+, VOL-, POWER);
 *   - headphone jack plugged / unplugged (the kernel switches the audio
 *     between speaker and headphones; we report it);
 *   - the DC port (charger) plugged / unplugged, and the battery percentage
 *     whenever it goes up or down;
 *   - the OTG port connected to / disconnected from a computer;
 *   - USB storage inserted / removed, with its size.
 * POWER pressed turns the console off, and so does a battery that stays at
 * or below battery_off_level (x7game.cfg). VOL+/VOL- change the volume,
 * FN + VOL+/VOL- the screen brightness (with optional idle dimming).
 * Started by hand from a terminal, it prints the lines there too.
 *
 *   x7-hwmon               monitor (what init runs)
 *   x7-hwmon --status      print the state to stdout once and exit (used by
 *                          x7-status, x7-console and the game list)
 */
#define _GNU_SOURCE
#include <ctype.h>
#include <dirent.h>
#include <errno.h>
#include <fcntl.h>
#include <glob.h>
#include <linux/input.h>
#include <poll.h>
#include <signal.h>
#include <stdarg.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/inotify.h>
#include <sys/ioctl.h>
#include <sys/prctl.h>
#include <sys/stat.h>
#include <sys/statvfs.h>
#include <sys/sysinfo.h>
#include <sys/utsname.h>
#include <time.h>
#include <unistd.h>

#define MAX_INPUTS	16
#define EVENT_LOG	"/run/x7-events.log"
#define EVENT_LOG_MAX	(256 * 1024)	/* cut the log when it passes this... */
#define EVENT_LOG_KEEP	(64 * 1024)	/* ...to its newest 64 KiB */
#define CONF		"/run/x7game.conf"

/* battery: stock-scale ADC level (241 * raw / reference), measured by NZEUS
 * Deck: about 128 = empty (the console died at 128-129), 175 = full */
#define LEVEL_EMPTY	128
#define LEVEL_FULL	175
#define BAT_SAMPLES	16
#define BATTERY_OFF_DEFAULT	130	/* battery_off_level without a valid setting */

enum cat { C_SYS, C_BTN, C_AUDIO, C_POWER, C_USB, C_CARDS };
static const char *const cat_name[] = { "SYSTEM", "BUTTON", "AUDIO", "POWER", "USB", "CARDS" };
static const char *const cat_color[] = { "1;37", "1;36", "1;35", "1;33", "1;34", "1;32" };

static FILE *event_log;
static int use_color = 1;
/* print the lines on stdout too: always for --status (x7-browser reads it
 * through a pipe); in monitor mode only on a terminal, or when the event log
 * could not be opened (init sends the monitor's stdout to /dev/null) */
static int to_stdout = 1;

struct input {
	int fd;
	char node[32];
	char name[96];
};
static struct input inputs[MAX_INPUTS];
static int ninputs;

/* ------------------------------------------------------------------ util */

static double uptime(void)
{
	struct timespec ts;

	clock_gettime(CLOCK_BOOTTIME, &ts);
	return ts.tv_sec + ts.tv_nsec / 1e9;
}

/* /run is a small tmpfs in RAM and every button press is logged: once the
 * event log passes EVENT_LOG_MAX, cut it in place to its newest
 * EVENT_LOG_KEEP bytes (from the start of a line). The file is not renamed
 * and stays open in append mode, so "tail -f" (x7-console) keeps following
 * it. On any error the log simply carries on as it is. */
static void cap_event_log(void)
{
	long size = ftell(event_log);
	int fd = fileno(event_log);
	char *keep, *start;
	ssize_t n;

	if (size <= EVENT_LOG_MAX || fd < 0)
		return;
	keep = malloc(EVENT_LOG_KEEP);
	if (!keep)
		return;
	n = pread(fd, keep, EVENT_LOG_KEEP, (off_t)size - EVENT_LOG_KEEP);
	start = n > 0 ? memchr(keep, '\n', n) : NULL;
	if (start && ftruncate(fd, 0) == 0) {
		start++;
		/* O_APPEND: this lands at the start of the now empty file */
		if (write(fd, start, keep + n - start) < 0) {
			/* nothing to do: the log starts again from empty */
		}
		fseek(event_log, 0, SEEK_END);	/* stdio: the file changed under it */
	}
	free(keep);
}

static void say(enum cat c, const char *fmt, ...)
{
	char msg[512];
	double t = uptime();
	va_list ap;

	va_start(ap, fmt);
	vsnprintf(msg, sizeof(msg), fmt, ap);
	va_end(ap);
	if (to_stdout) {
		if (use_color)
			printf("[%7.2f] \033[%sm%-6s\033[0m %s\n", t, cat_color[c], cat_name[c], msg);
		else
			printf("[%7.2f] %-6s %s\n", t, cat_name[c], msg);
		fflush(stdout);
	}
	if (event_log) {
		fprintf(event_log, "[%7.2f] %-6s %s\n", t, cat_name[c], msg);
		fflush(event_log);
		cap_event_log();
	}
}

/* read a small sysfs file into buf (trailing newline removed); 0 = ok */
static int read_file(const char *path, char *buf, size_t len)
{
	ssize_t n;
	int fd = open(path, O_RDONLY | O_CLOEXEC);

	if (fd < 0)
		return -1;
	n = read(fd, buf, len - 1);
	close(fd);
	if (n < 0)
		return -1;
	buf[n] = 0;
	while (n > 0 && (buf[n - 1] == '\n' || buf[n - 1] == ' '))
		buf[--n] = 0;
	return 0;
}

static long read_long(const char *path, long fallback)
{
	char buf[64];

	if (read_file(path, buf, sizeof(buf)))
		return fallback;
	return strtol(buf, NULL, 10);
}

/* first path matching a glob pattern, or "" */
static void find_path(const char *pattern, char *out, size_t len)
{
	glob_t g;

	out[0] = 0;
	if (glob(pattern, 0, NULL, &g) == 0) {
		if (g.gl_pathc > 0)
			snprintf(out, len, "%s", g.gl_pathv[0]);
		globfree(&g);
	}
}

/* value of KEY=... in /run/x7game.conf (the defaults, then x7game.cfg from
 * the SD card, copied at boot: the last line wins); 0 = found */
static int conf_get(const char *key, char *out, size_t len)
{
	char line[256];
	size_t klen = strlen(key);
	int found = -1;
	FILE *f = fopen(CONF, "re");

	if (!f)
		return -1;
	while (fgets(line, sizeof(line), f))
		if (!strncmp(line, key, klen) && line[klen] == '=') {
			line[strcspn(line, "\r\n")] = 0;
			snprintf(out, len, "%s", line + klen + 1);
			found = 0;
		}
	fclose(f);
	return found;
}

static void run_detached(char *const argv[])
{
	pid_t pid = fork();

	if (pid == 0) {
		execv(argv[0], argv);
		_exit(127);
	}
}

static void format_size(unsigned long long bytes, char *out, size_t len)
{
	if (bytes >= 1000000000ULL)
		snprintf(out, len, "%llu.%llu GB", bytes / 1000000000ULL,
			 (bytes % 1000000000ULL) / 100000000ULL);
	else
		snprintf(out, len, "%llu MB", bytes / 1000000ULL);
}

/* --------------------------------------------------------------- buttons */

static const char *key_name(unsigned int code)
{
	switch (code) {
	case BTN_EAST:		return "A";
	case BTN_SOUTH:		return "B";
	case BTN_NORTH:		return "X";
	case BTN_WEST:		return "Y";
	case BTN_TL:		return "L1";
	case BTN_TR:		return "R1";
	case BTN_TL2:		return "L2";
	case BTN_TR2:		return "R2";
	case BTN_SELECT:	return "SELECT";
	case BTN_START:		return "START";
	case BTN_MODE:		return "FN";
	case BTN_DPAD_UP:	return "D-PAD UP";
	case BTN_DPAD_DOWN:	return "D-PAD DOWN";
	case BTN_DPAD_LEFT:	return "D-PAD LEFT";
	case BTN_DPAD_RIGHT:	return "D-PAD RIGHT";
	case KEY_VOLUMEUP:	return "VOL+";
	case KEY_VOLUMEDOWN:	return "VOL-";
	case KEY_POWER:		return "POWER";
	}
	return NULL;
}

static void add_input(const char *node)
{
	struct input *in;
	int i, fd;

	for (i = 0; i < ninputs; i++)
		if (!strcmp(inputs[i].node, node))
			return;
	if (ninputs >= MAX_INPUTS)
		return;
	fd = open(node, O_RDONLY | O_NONBLOCK | O_CLOEXEC);
	if (fd < 0)
		return;
	in = &inputs[ninputs];
	if (ioctl(fd, EVIOCGNAME(sizeof(in->name)), in->name) < 0)
		snprintf(in->name, sizeof(in->name), "?");
	/* x7-padd's virtual pad repeats the real buttons: don't count them twice */
	if (!strcmp(in->name, "X7 Game Gamepad")) {
		close(fd);
		return;
	}
	in->fd = fd;
	snprintf(in->node, sizeof(in->node), "%s", node);
	ninputs++;
}

static void scan_inputs(void)
{
	DIR *d = opendir("/dev/input");
	struct dirent *e;
	char node[32];

	if (!d)
		return;
	while ((e = readdir(d)))
		if (!strncmp(e->d_name, "event", 5)) {
			snprintf(node, sizeof(node), "/dev/input/%.20s", e->d_name);	/* eventN */
			add_input(node);
		}
	closedir(d);
}

static void drop_input(int i)
{
	close(inputs[i].fd);
	inputs[i] = inputs[--ninputs];
}

/* ---------------------------------------------------------------- volume */

static int volume = -1;		/* 0..255, the sound card's "Master Playback Volume" */

static int volume_read(void)
{
	char line[256];
	int v = -1;
	FILE *p = popen("amixer -c 0 cget name='Master Playback Volume' 2>/dev/null", "r");

	if (!p)
		return -1;
	while (fgets(line, sizeof(line), p)) {
		char *s = strstr(line, ": values=");

		if (s)
			v = atoi(s + 9);
	}
	pclose(p);
	return v;
}

static void volume_step(int up)
{
	char value[16];
	char *argv[] = { "/usr/bin/amixer", "-q", "-c", "0", "cset",
			 "name=Master Playback Volume", value, NULL };

	if (volume < 0)
		volume = volume_read();
	if (volume < 0)
		return;
	volume += up ? 16 : -16;
	if (volume > 255)
		volume = 255;
	if (volume < 0)
		volume = 0;
	snprintf(value, sizeof(value), "%d", volume);
	run_detached(argv);
}

/* ------------------------------------------------------------- headphones */

static char audio_sysfs[256];	/* .../1880a000.audio/headphones */

static int headphone_pin(void)
{
	char buf[128];
	char *s;

	if (!audio_sysfs[0] || read_file(audio_sysfs, buf, sizeof(buf)))
		return -1;
	s = strstr(buf, "level=");
	return s ? atoi(s + 6) : -1;
}

static void report_headphones(int in, int initial)
{
	int pin = headphone_pin();

	if (in)
		say(C_AUDIO, "Headphone jack: %s -> sound on the HEADPHONES (speaker off)",
		    initial ? "headphones in" : "PLUGGED IN");
	else
		say(C_AUDIO, "Headphone jack: %s -> sound on the SPEAKER", initial ? "empty" : "UNPLUGGED");
	if (pin >= 0 && !initial)
		say(C_AUDIO, "  (detect pin L15 reads %d; if this is reversed, set headphone_plugged_level=%d in x7game/x7game.cfg)",
		    pin, in ? !pin : pin);
}

static int headphones_now(void)
{
	unsigned long sw[(SW_MAX + 8 * sizeof(long)) / (8 * sizeof(long))];
	int i;

	for (i = 0; i < ninputs; i++) {
		if (strcmp(inputs[i].name, "R36S headphone jack"))
			continue;
		memset(sw, 0, sizeof(sw));
		if (ioctl(inputs[i].fd, EVIOCGSW(sizeof(sw)), sw) < 0)
			return -1;
		return !!(sw[SW_HEADPHONE_INSERT / (8 * sizeof(long))] &
			  (1UL << (SW_HEADPHONE_INSERT % (8 * sizeof(long)))));
	}
	return -1;
}

/* ------------------------------------------------------------- backlight */

/*
 * FN + VOL+ / VOL- change the screen brightness; the level is saved on the
 * SD card and set again at the next start. Optional idle dimming and
 * screen-off (x7game.cfg, off by default): any button brings the level back.
 * The backlight device (nzeus-ram's PWM) appears some 15-20 s after start,
 * when S40x7ram has released the AVP memory; until then the bootloader's
 * level stays.
 */
#define BACKLIGHT	"/sys/class/backlight/r36s-pwm/brightness"
#define BL_SAVED	"/boot/x7game/brightness"
#define BL_MIN		10	/* FN+VOL never goes darker than this (0 = dark) */
#define BL_MAX		255
#define BL_STEP		25	/* about 10 % */

static int bl_level = -1;	/* the user's level; -1 = no backlight device yet */
static int bl_now = -1;		/* what it is set to now (level, dimmed or 0) */
static double bl_save_at;	/* save the level at this uptime; 0 = saved */
static double idle_since;	/* uptime of the last button press */
static int dim_after, off_after, dim_level;	/* seconds, seconds, 0..255 */
static int fn_held;

/* KEY in x7game.cfg as a number in [lo, hi], else def */
static int conf_num(const char *key, int def, int lo, int hi)
{
	char value[32], *end;
	long v;

	if (conf_get(key, value, sizeof(value)) || !value[0])
		return def;
	v = strtol(value, &end, 10);
	return *end || v < lo || v > hi ? def : (int)v;
}

static void bl_write(int v)
{
	FILE *f;

	if (v == bl_now)
		return;
	f = fopen(BACKLIGHT, "we");
	if (!f)
		return;
	fprintf(f, "%d\n", v);
	if (fclose(f) == 0)
		bl_now = v;
}

static void bl_save(void)
{
	FILE *f = fopen(BL_SAVED, "we");

	bl_save_at = 0;
	if (f) {
		fprintf(f, "%d\n", bl_level);
		fclose(f);
	}
}

static int bl_percent(int v)
{
	return (v * 100 + BL_MAX / 2) / BL_MAX;
}

/* once the device is there: the saved level, else the bootloader's */
static void backlight_init(void)
{
	char buf[32];
	int v = -1;

	if (access(BACKLIGHT, W_OK))
		return;
	dim_after = conf_num("dim_after_s", 0, 0, 86400);
	off_after = conf_num("screen_off_after_s", 0, 0, 86400);
	dim_level = conf_num("dim_level", 20, 0, BL_MAX);
	if (!read_file(BL_SAVED, buf, sizeof(buf)))
		v = atoi(buf);
	if (v < BL_MIN || v > BL_MAX) {
		v = read_file(BACKLIGHT, buf, sizeof(buf)) ? -1 : atoi(buf);
		if (v < BL_MIN || v > BL_MAX)
			v = 153;	/* the bootloader's level */
	}
	bl_level = v;
	bl_now = -1;
	bl_write(bl_level);
	say(C_SYS, "Backlight: %d%% (FN + VOL+/VOL- to change)", bl_percent(bl_level));
}

static void brightness_step(int up)
{
	if (bl_level < 0) {
		say(C_BTN, "FN+VOL%c: no brightness control yet (it starts some 20 s after power-on)",
		    up ? '+' : '-');
		return;
	}
	bl_level += up ? BL_STEP : -BL_STEP;
	if (bl_level > BL_MAX)
		bl_level = BL_MAX;
	if (bl_level < BL_MIN)
		bl_level = BL_MIN;
	bl_write(bl_level);
	bl_save_at = uptime() + 3;	/* one SD card write per adjustment */
	say(C_BTN, "FN+VOL%c  (brightness %d%%)", up ? '+' : '-', bl_percent(bl_level));
}

/* a button was pressed: the idle timers start again, a dimmed or dark
 * screen comes back */
static void activity(void)
{
	idle_since = uptime();
	if (bl_level >= 0 && bl_now != bl_level)
		bl_write(bl_level);
}

static void backlight_tick(double now)
{
	double idle = now - idle_since;

	if (bl_level < 0) {
		backlight_init();
		return;
	}
	if (bl_save_at && now >= bl_save_at)
		bl_save();
	if (off_after && idle >= off_after)
		bl_write(0);
	else if (dim_after && idle >= dim_after)
		bl_write(dim_level < bl_level ? dim_level : bl_level);
}

/* ---------------------------------------------------------- power off */

static int powering_off;

static void power_off(const char *why)
{
	char *argv[] = { "/sbin/poweroff", NULL };

	if (powering_off)
		return;
	powering_off = 1;
	if (bl_save_at)
		bl_save();		/* a level changed just before */
	say(C_POWER, "%s: turning off. Goodbye!", why);
	run_detached(argv);
}

static void handle_event(const struct input *in, const struct input_event *ev)
{
	const char *name;

	if (ev->type == EV_SW && ev->code == SW_HEADPHONE_INSERT) {
		report_headphones(ev->value, 0);
		return;
	}
	if (ev->type != EV_KEY || ev->value == 2)	/* 2 = auto-repeat */
		return;
	name = key_name(ev->code);
	if (ev->value == 1)
		activity();
	if (ev->code == BTN_MODE)
		fn_held = ev->value != 0;
	if (ev->code == KEY_POWER) {
		/* Only a press seen while running counts: if the button is still
		 * held from switching on, the first event is its release. */
		if (ev->value == 1) {
			say(C_BTN, "POWER pressed");
			power_off("Power button");
		}
		return;
	}
	if (ev->code == KEY_VOLUMEUP || ev->code == KEY_VOLUMEDOWN) {
		if (ev->value == 1 && fn_held) {
			brightness_step(ev->code == KEY_VOLUMEUP);
		} else if (ev->value == 1) {
			volume_step(ev->code == KEY_VOLUMEUP);
			if (volume >= 0)
				say(C_BTN, "%s pressed  (volume %d%%)", name, (volume * 100 + 127) / 255);
			else
				say(C_BTN, "%s pressed", name);
		} else {
			say(C_BTN, "%s released", name);
		}
		return;
	}
	if (name)
		say(C_BTN, "%s %s", name, ev->value ? "pressed" : "released");
	else
		say(C_BTN, "key %u %s (%s)", ev->code, ev->value ? "pressed" : "released", in->name);
}

/* --------------------------------------------------- battery and DC port */

static char stock_levels[256];	/* .../188184d0.power/stock_levels */
static int bat_samples[BAT_SAMPLES], bat_n, bat_i;
static int bat_shown = -1;	/* last percentage printed */
static int dc_online = -1, dc_candidate = -1;
static int battery_off_level = BATTERY_OFF_DEFAULT;	/* read once at start; 0 = off */
static double critical_seconds = -1;	/* time spent at or below it; -1 = not low */
static double critical_last;		/* uptime of the last critical_tick() */

static int battery_level(void)
{
	char buf[128];
	char *s;

	if (!stock_levels[0] || read_file(stock_levels, buf, sizeof(buf)))
		return -1;
	s = strstr(buf, "battery=");
	return s ? atoi(s + 8) : -1;
}

/* percentage x10 from the averaged ADC level (straight line, like the kernel) */
static int battery_pct10(void)
{
	long sum = 0;
	int i, pct10;

	if (!bat_n)
		return (int)read_long("/sys/class/power_supply/battery/capacity", -1) * 10;
	for (i = 0; i < bat_n; i++)
		sum += bat_samples[i];
	pct10 = (int)((sum * 10 / bat_n - LEVEL_EMPTY * 10) * 100 / (LEVEL_FULL - LEVEL_EMPTY));
	if (pct10 < 0)
		pct10 = 0;
	if (pct10 > 1000)
		pct10 = 1000;
	return pct10;
}

static const char *battery_status(void)
{
	static char status[32];

	if (read_file("/sys/class/power_supply/battery/status", status, sizeof(status)))
		return "unknown";
	for (char *p = status; *p; p++)
		*p = tolower((unsigned char)*p);
	return status;
}

static void battery_tick(int initial)
{
	int level = battery_level(), pct10, shown;

	if (level > 0) {
		bat_samples[bat_i] = level;
		bat_i = (bat_i + 1) % BAT_SAMPLES;
		if (bat_n < BAT_SAMPLES)
			bat_n++;
	}
	pct10 = battery_pct10();
	if (pct10 < 0)
		return;
	shown = (pct10 + 5) / 10;
	if (bat_shown < 0 || initial) {
		bat_shown = shown;
		if (initial)
			say(C_POWER, "Battery: %d%% (%s)", shown, battery_status());
		return;
	}
	/* print only real changes: at least 0.8 % away from what was shown */
	if (shown != bat_shown && abs(pct10 - bat_shown * 10) >= 8) {
		say(C_POWER, "Battery: %d%% (%s %d%%)", shown, shown > bat_shown ? "up from" : "down from",
		    bat_shown);
		bat_shown = shown;
	}
}

static void dc_report(int online, int initial)
{
	if (online)
		say(C_POWER, "DC port: %s -> charging", initial ? "charger connected" : "charger PLUGGED IN");
	else
		say(C_POWER, "DC port: %s -> running on battery", initial ? "empty" : "charger UNPLUGGED");
}

static void dc_tick(int initial)
{
	int online = (int)read_long("/sys/class/power_supply/charger/online", -1);

	if (online < 0)
		return;
	if (initial) {
		dc_online = dc_candidate = online;
		dc_report(online, 1);
		return;
	}
	/* two equal readings in a row (0.5 s apart) before reporting */
	if (online != dc_online) {
		if (online == dc_candidate) {
			dc_online = online;
			dc_report(online, 0);
			/* the charger shifts the level: start averaging again */
			bat_n = 0;
			bat_i = 0;
		}
		dc_candidate = online;
	} else {
		dc_candidate = online;
	}
}

/* battery_off_level from x7game.cfg, read once at start: empty, not a whole
 * number or outside 0..LEVEL_FULL means the default; 0 switches the
 * low-battery power-off off */
static void read_battery_off_level(void)
{
	char value[256], *end;
	long v;

	if (conf_get("battery_off_level", value, sizeof(value)))
		return;
	errno = 0;
	v = strtol(value, &end, 10);
	if (end == value || *end || errno || v < 0 || v > LEVEL_FULL) {
		say(C_POWER, "battery_off_level=%s is not a level from 0 to %d: using %d",
		    value, LEVEL_FULL, BATTERY_OFF_DEFAULT);
		return;
	}
	battery_off_level = (int)v;
}

/* power off cleanly before the battery runs out (not while charging); the
 * hardware itself dies at about level 128. One reading jumps by about
 * +-2 levels, so this uses the average of the stored samples (in tenths of a
 * level, both sides): it counts the time while the average is at or below
 * battery_off_level, and starts again only once the average is more than one
 * level above it. */
static void critical_tick(void)
{
	long sum = 0, avg10;
	int i, n = 0;
	double now = uptime(), elapsed = now - critical_last;

	critical_last = now;
	if (dc_online == 1 || battery_off_level <= 0) {
		critical_seconds = -1;
		return;
	}
	for (i = 0; i < bat_n; i++)
		if (bat_samples[i] > 0) {
			sum += bat_samples[i];
			n++;
		}
	if (!n)
		return;
	avg10 = sum * 10 / n;
	if (avg10 <= battery_off_level * 10L) {
		if (critical_seconds < 0) {
			critical_seconds = 0;
			say(C_POWER, "Battery critically low (level %ld.%ld): turning off in 30 s unless a charger is plugged in",
			    avg10 / 10, avg10 % 10);
		} else {
			critical_seconds += elapsed;
		}
		if (critical_seconds >= 30)
			power_off("Battery critically low");
	} else if (avg10 > (battery_off_level + 1) * 10L) {
		critical_seconds = -1;		/* clearly above it again */
	}
}

/* --------------------------------------------------------------- OTG port */

static int otg_state = -2;	/* -1 no controller, 0 off, 1 setting up, 2 connected, 3 suspended */

static int otg_now(char *raw, size_t len)
{
	char path[256];

	find_path("/sys/class/udc/*/state", path, sizeof(path));
	if (!path[0] || read_file(path, raw, len))
		return -1;
	if (!strcmp(raw, "not attached"))
		return 0;
	if (!strcmp(raw, "configured"))
		return 2;
	if (!strcmp(raw, "suspended"))
		return 3;
	return 1;
}

static void otg_tick(int initial)
{
	char raw[128] = "";
	int s = otg_now(raw, sizeof(raw));

	if (s == otg_state && !initial)
		return;
	otg_state = s;
	switch (s) {
	case -1:
		say(C_USB, "OTG port: no USB device controller found");
		break;
	case 0:
		say(C_USB, "OTG port: %s", initial ? "not connected" : "DISCONNECTED from the computer");
		break;
	case 1:
		say(C_USB, "OTG port: cable detected, the computer is setting it up (%s)", raw);
		break;
	case 2:
		say(C_USB, "OTG port: CONNECTED to a computer");
		say(C_USB, "  shell: PuTTY > Session > Connection type Serial, Serial line COMx, Speed 115200 > Open, press Enter");
		if (!read_file("/run/x7-usb-shell.state", raw, sizeof(raw)))
			say(C_USB, "  (USB shell: %s)", raw);
		break;
	case 3:
		say(C_USB, "OTG port: connected, the computer has suspended the port");
		break;
	}
}

/* -------------------------------------- extra cards (USB storage, SD 2) */

#define MAX_CARDS 8
static char cards[MAX_CARDS][32];
static int ncards = -1;

static int is_extra_card(const char *name)
{
	if (!strncmp(name, "mmcblk", 6))
		return strcmp(name, "mmcblk0") && !strstr(name, "boot") && !strstr(name, "rpmb");
	return name[0] == 's' && name[1] == 'd' && isalpha((unsigned char)name[2]) && !name[3];
}

static void card_report(const char *name, int inserted)
{
	char path[128], size[32];
	unsigned long long sectors;
	const char *slot = name[0] == 's' ? "USB storage" : "SD card 2";

	if (!inserted) {
		say(C_CARDS, "%s: card REMOVED (%s)", slot, name);
		return;
	}
	snprintf(path, sizeof(path), "/sys/block/%.31s/size", name);	/* cards[] names */
	sectors = (unsigned long long)read_long(path, 0);
	format_size(sectors * 512ULL, size, sizeof(size));
	say(C_CARDS, "%s: card INSERTED - %s (%llu bytes, /dev/%s)", slot, size, sectors * 512ULL, name);
}

static void cards_tick(int initial)
{
	char now[MAX_CARDS][32];
	int n = 0, i, j;
	DIR *d = opendir("/sys/block");
	struct dirent *e;

	if (d) {
		while ((e = readdir(d)) && n < MAX_CARDS)
			if (is_extra_card(e->d_name))
				snprintf(now[n++], sizeof(now[0]), "%.31s", e->d_name);
		closedir(d);
	}
	for (i = 0; i < n; i++) {		/* new cards */
		for (j = 0; j < (ncards < 0 ? 0 : ncards); j++)
			if (!strcmp(now[i], cards[j]))
				break;
		if (ncards < 0 || j == ncards)
			card_report(now[i], 1);
	}
	for (j = 0; j < (ncards < 0 ? 0 : ncards); j++) {	/* removed cards */
		for (i = 0; i < n; i++)
			if (!strcmp(now[i], cards[j]))
				break;
		if (i == n)
			card_report(cards[j], 0);
	}
	memcpy(cards, now, sizeof(now));
	ncards = n;
}

/* ---------------------------------------------------------------- status */

/* the data partition (X7DATA at /share, made by /etc/init.d/S05x7data) */
static void data_status(void)
{
	char line[512], fstype[32] = "", state[256], total[32], avail[32];
	struct statvfs st;
	FILE *f = fopen("/proc/mounts", "re");

	if (f) {
		while (fgets(line, sizeof(line), f)) {
			char dev[128], dir[128], type[32];

			if (sscanf(line, "%127s %127s %31s", dev, dir, type) == 3 && !strcmp(dir, "/share")) {
				snprintf(fstype, sizeof(fstype), "%s", type);
				break;
			}
		}
		fclose(f);
	}
	if (fstype[0] && statvfs("/share", &st) == 0) {
		format_size((unsigned long long)st.f_blocks * st.f_frsize, total, sizeof(total));
		format_size((unsigned long long)st.f_bavail * st.f_frsize, avail, sizeof(avail));
		say(C_CARDS, "Data: X7DATA (%s) at /share, %s, %s free - your ROMs, saves and media",
		    fstype, total, avail);
	} else if (!read_file("/run/x7-data.state", state, sizeof(state))) {
		say(C_CARDS, "Data: %s", state);
	} else {
		say(C_CARDS, "Data: no data partition");
	}
}

/* at_boot: 0 = --status, 1 = the monitor's first start, 2 = the monitor
 * started again by init (it had stopped) */
static void status_lines(int at_boot)
{
	char buf[256], release[96] = "X7 Game", path[256];
	struct utsname u;
	struct sysinfo si;
	long xres = 0, yres = 0, bpp;
	int hp;

	if (!read_file("/etc/x7game-release", buf, sizeof(buf))) {
		char *v = strstr(buf, "X7_VERSION=");

		if (v) {
			v += 11;
			v[strcspn(v, "\n")] = 0;
			snprintf(release, sizeof(release), "X7 Game %s", v);
		}
	}
	uname(&u);
	{
		const char *slot = "?";
		char cmdline[1024];	/* the command line is longer than buf */

		if (!read_file("/proc/cmdline", cmdline, sizeof(cmdline)))
			slot = strstr(cmdline, "root=/dev/mmcblk0p2 ") ? "A" :
			       strstr(cmdline, "root=/dev/mmcblk0p3 ") ? "B" : "?";
		say(C_SYS, "%s - Linux %s (%s), system slot %s", release, u.release, u.machine, slot);
	}
	if (at_boot == 1)
		say(C_SYS, "Started in %.1f s (kernel + system; the bootloader's logo time is extra)", uptime());
	else if (at_boot == 2)
		say(C_SYS, "Hardware monitor restarted (up for %.0f s)", uptime());
	else
		say(C_SYS, "Up for %.0f s", uptime());
	if (!read_file("/sys/class/graphics/fb0/virtual_size", buf, sizeof(buf)))
		sscanf(buf, "%ld,%ld", &xres, &yres);
	bpp = read_long("/sys/class/graphics/fb0/bits_per_pixel", 0);
	if (xres)
		say(C_SYS, "Display: %ldx%ld, %ld-bit colour (%s), panel timing from the bootloader",
		    xres, yres, bpp, bpp == 32 ? "16.7 million colours" : "65,536 colours");
	else
		say(C_SYS, "Display: no framebuffer found");
	if (sysinfo(&si) == 0)
		say(C_SYS, "Memory: %lu MiB total, %lu MiB free", si.totalram * si.mem_unit >> 20,
		    si.freeram * si.mem_unit >> 20);
	snprintf(path, sizeof(path), "/sys/block/mmcblk0/size");
	if (read_long(path, 0) > 0) {
		format_size((unsigned long long)read_long(path, 0) * 512ULL, buf, sizeof(buf));
		say(C_CARDS, "TF1: X7 Game system card, %s", buf);
	}
	data_status();
	cards_tick(1);
	battery_tick(1);
	dc_tick(1);
	otg_tick(1);
	hp = headphones_now();
	if (hp >= 0)
		report_headphones(hp, 1);
	else
		say(C_AUDIO, "Headphone jack: detection not available");
	volume = volume_read();
	if (volume >= 0)
		say(C_AUDIO, "Volume: %d%%", (volume * 100 + 127) / 255);
	{
		char buf[32];

		if (!read_file(BACKLIGHT, buf, sizeof(buf)))
			say(C_SYS, "Backlight: %d%%", bl_percent(atoi(buf)));
	}
}

/* ------------------------------------------------------------------ main */

int main(int argc, char **argv)
{
	int ino, restarted, status_only = argc > 1 && !strcmp(argv[1], "--status");
	double next_battery, next_fast;
	struct sigaction sa = { .sa_handler = SIG_IGN, .sa_flags = SA_NOCLDWAIT };

	sigaction(SIGCHLD, &sa, NULL);
	signal(SIGPIPE, SIG_IGN);
	setvbuf(stdout, NULL, _IOLBF, 0);
	use_color = isatty(1) && !getenv("NO_COLOR");
	find_path("/sys/bus/platform/devices/*.power/stock_levels", stock_levels, sizeof(stock_levels));
	find_path("/sys/bus/platform/devices/*.audio/headphones", audio_sysfs, sizeof(audio_sysfs));
	scan_inputs();
	if (status_only) {
		status_lines(0);
		return 0;
	}
	/* nothing below is urgent: let the kernel run our timeouts up to 50 ms
	 * late, together with its own wakeups (input events still wake us at
	 * once) */
	prctl(PR_SET_TIMERSLACK, 50000000UL);
	/* the log is already there when init starts us again after a crash */
	restarted = access(EVENT_LOG, F_OK) == 0;
	event_log = fopen(EVENT_LOG, "a+e");	/* +: cap_event_log() reads it back */
	to_stdout = isatty(1) || !event_log;
	status_lines(restarted ? 2 : 1);
	read_battery_off_level();
	if (isatty(1))
		printf("\n%sWelcome to X7 Game!%s\n\n", use_color ? "\033[1;32m" : "", use_color ? "\033[0m" : "");
	if (event_log) {
		fprintf(event_log, "Welcome to X7 Game!\n");
		fflush(event_log);
	}

	ino = inotify_init1(IN_NONBLOCK | IN_CLOEXEC);
	if (ino >= 0)
		inotify_add_watch(ino, "/dev/input", IN_CREATE);
	/* status_lines() did the first round: the ticks start from now on */
	idle_since = uptime();
	next_fast = uptime() + 0.5;
	next_battery = next_fast + 0.5;
	for (;;) {
		struct pollfd fds[MAX_INPUTS + 1];
		int i, n = 0, timeout;
		double now, next;

		for (i = 0; i < ninputs; i++) {
			fds[n].fd = inputs[i].fd;
			fds[n++].events = POLLIN;
		}
		if (ino >= 0) {
			fds[n].fd = ino;
			fds[n++].events = POLLIN;
		}
		/* sleep until the next tick is due (rounded up to whole ms) */
		now = uptime();
		next = next_fast < next_battery ? next_fast : next_battery;
		timeout = next > now ? (int)((next - now) * 1000) + 1 : 0;
		poll(fds, n, timeout);
		/* inputs first (their slots match the inputs array) */
		for (i = ninputs - 1; i >= 0; i--) {
			struct input_event ev[32];
			ssize_t r;

			if (!(fds[i].revents & (POLLIN | POLLERR | POLLHUP)))
				continue;
			r = read(inputs[i].fd, ev, sizeof(ev));
			if (r < 0 && errno != EAGAIN && errno != EINTR) {
				drop_input(i);
				continue;
			}
			for (ssize_t k = 0; r > 0 && k < r / (ssize_t)sizeof(ev[0]); k++)
				handle_event(&inputs[i], &ev[k]);
		}
		if (ino >= 0 && (fds[n - 1].revents & POLLIN)) {
			char buf[512];

			while (read(ino, buf, sizeof(buf)) > 0)
				;
			usleep(100000);		/* let the device node settle */
			scan_inputs();
		}
		/* both ticks keep a fixed rhythm, so the 1 s tick shares a wakeup
		 * with every second 0.5 s tick; after a long stall they start
		 * again from now instead of catching up */
		now = uptime();
		if (now >= next_fast) {		/* every 0.5 s */
			next_fast += 0.5;
			if (next_fast <= now)
				next_fast = now + 0.5;
			dc_tick(0);
			otg_tick(0);
			cards_tick(0);
			backlight_tick(now);
		}
		if (now >= next_battery) {	/* every second */
			next_battery += 1.0;
			if (next_battery <= now)
				next_battery = now + 1.0;
			battery_tick(0);
			critical_tick();
		}
	}
}

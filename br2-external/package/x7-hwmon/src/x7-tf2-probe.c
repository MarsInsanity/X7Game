// SPDX-License-Identifier: GPL-3.0-or-later
/*
 * x7-tf2-probe - find out how the second card slot (TF2) is wired.
 *
 * Nobody has found TF2 in software yet: the SoC has one SD controller, the
 * stock system never saw a second card, and it is not a USB card reader
 * (TreeFrogUI docs/dev/sd2-investigation.md). This tool only READS: it maps
 * the GPIO registers (0x18800000) and the SD controller (0x1884c000) from
 * /dev/mem read-only and prints every change of
 *   - the input level of all 128 GPIO pins (banks L, B, R, T), and
 *   - the SD controller's card-detect register (CDETECT, one bit per slot),
 * while you insert and remove a card in TF2. A pin that follows the card is
 * TF2's card-detect line - a first step to driving the slot.
 *
 *   x7-tf2-probe [SECONDS]      (default 60)
 *
 * L08/L09 (the button shift register's clock and data) change all the time
 * and are left out. Buttons you press also show up, so don't touch them.
 */
#define _GNU_SOURCE
#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/mman.h>
#include <time.h>
#include <unistd.h>

static const unsigned int bank_offset[4] = { 0x044, 0x0c4, 0x0e4, 0x344 };	/* +0x0c = IN */
static const char bank_name[4] = { 'L', 'B', 'R', 'T' };

static double now(void)
{
	struct timespec ts;

	clock_gettime(CLOCK_MONOTONIC, &ts);
	return ts.tv_sec + ts.tv_nsec / 1e9;
}

static volatile uint32_t *map(int fd, off_t base)
{
	void *p = mmap(NULL, 4096, PROT_READ, MAP_SHARED, fd, base);

	return p == MAP_FAILED ? NULL : p;
}

int main(int argc, char **argv)
{
	int seconds = argc > 1 ? atoi(argv[1]) : 60, fd, b, changes = 0;
	volatile uint32_t *gpio, *mshc;
	uint32_t last[4], cd, v;
	double start, end;

	fd = open("/dev/mem", O_RDONLY | O_SYNC);
	if (fd < 0) {
		perror("/dev/mem (run as root)");
		return 1;
	}
	gpio = map(fd, 0x18800000);
	mshc = map(fd, 0x1884c000);
	if (!gpio || !mshc) {
		perror("mmap");
		return 1;
	}
	for (b = 0; b < 4; b++)
		last[b] = gpio[(bank_offset[b] + 0x0c) / 4];
	cd = mshc[0x50 / 4];
	printf("x7-tf2-probe: read-only, %d s. Insert and remove a card in TF2 a few times\n"
	       "(wait ~2 s between). Don't press buttons.\n", seconds);
	printf("start: IN L=%08x B=%08x R=%08x T=%08x  CDETECT=%08x\n", last[0], last[1], last[2],
	       last[3], cd);
	fflush(stdout);
	start = now();
	end = start + seconds;
	while (now() < end) {
		for (b = 0; b < 4; b++) {
			uint32_t d;
			int pin;

			v = gpio[(bank_offset[b] + 0x0c) / 4];
			d = v ^ last[b];
			if (b == 0)
				d &= ~((1u << 8) | (1u << 9));	/* button shift register */
			for (pin = 0; d && pin < 32; pin++)
				if (d & (1u << pin)) {
					printf("t=%7.3f  GPIO %c%02d  %u -> %u\n", now() - start, bank_name[b],
					       pin, (last[b] >> pin) & 1, (v >> pin) & 1);
					changes++;
				}
			last[b] = v;
		}
		v = mshc[0x50 / 4];
		if (v != cd) {
			printf("t=%7.3f  CDETECT %08x -> %08x (bit 0 = slot 0, bit 1 = slot 1; 0 = card present)\n",
			       now() - start, cd, v);
			cd = v;
			changes++;
		}
		fflush(stdout);
		usleep(5000);
	}
	printf("done: %d change(s). Please send this output to the X7 Game developers.\n", changes);
	return 0;
}

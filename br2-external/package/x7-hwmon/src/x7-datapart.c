// SPDX-License-Identifier: GPL-3.0-or-later
/*
 * x7-datapart - the X7 Game data partition's entry in the SD card's
 * partition table (MBR).
 *
 *   x7-datapart probe       DEVICE START_LBA
 *   x7-datapart write-entry DEVICE START_LBA TYPE      (TYPE: 07 exFAT, 0c FAT32)
 *
 * The card: partition 1 = the FAT32 boot partition at LBA 2048 (in the
 * image), then the two hidden system slots, then from START_LBA (1 GiB) to
 * the end of the card the data partition, which X7 Game creates at its first
 * start. Linux finds all three through blkdevparts= (the data area is
 * /dev/mmcblk0p4 whatever the MBR says); the MBR entry 2 written here is for
 * PCs, which then show the data partition as a second drive.
 *
 * "probe" prints shell assignments:
 *   card_sectors=  start=  data_sectors=  too_small=0|1
 *   entry1=ok|bad              partition 1 is the FAT32 boot partition at 2048
 *   entry2=absent|ours|other   partition 2: empty, at START_LBA, or something else
 *   fs=exfat|fat32|ntfs|none   a file system at START_LBA (a re-flashed card
 *                              keeps its data partition: it is adopted, never
 *                              formatted again; ntfs is left alone)
 *   fs_sectors=                its size in 512-byte sectors
 * "write-entry" sets entry 2 = START_LBA .. end of card (whole MiB), only if
 * entry 1 is ok and entry 2 is empty or already ours; it reads the sector
 * back to check. Only sector 0 is ever written.
 */
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <linux/fs.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <unistd.h>

#define SECTOR		512
#define MIB_SECTORS	2048ULL
#define MIN_DATA	(64 * MIB_SECTORS)	/* at least 64 MiB, or no data partition */

static uint32_t le32(const uint8_t *p)
{
	return p[0] | p[1] << 8 | p[2] << 16 | (uint32_t)p[3] << 24;
}

static uint64_t le64(const uint8_t *p)
{
	return le32(p) | (uint64_t)le32(p + 4) << 32;
}

static void put32(uint8_t *p, uint32_t v)
{
	p[0] = v;
	p[1] = v >> 8;
	p[2] = v >> 16;
	p[3] = v >> 24;
}

/* CHS address for an MBR entry (255 heads, 63 sectors; capped like PCs do) */
static void chs(uint8_t *p, uint64_t lba)
{
	uint64_t c = lba / (255 * 63), rest = lba % (255 * 63);
	unsigned int h = rest / 63, s = rest % 63 + 1;

	if (c > 1023) {
		p[0] = 254;
		p[1] = 255;
		p[2] = 255;
		return;
	}
	p[0] = h;
	p[1] = ((c >> 2) & 0xC0) | s;
	p[2] = c & 0xFF;
}

struct card {
	uint8_t mbr[SECTOR], boot[SECTOR];
	uint64_t sectors, start, data;
	int entry1_ok, entry2;		/* entry2: 0 absent, 1 ours, 2 other */
	const char *fs;
	uint64_t fs_sectors;
};

static int load(const char *dev, uint64_t start, struct card *c, int flags)
{
	uint64_t bytes;
	const uint8_t *e1, *e2;
	int fd = open(dev, flags | O_CLOEXEC);

	if (fd < 0) {
		fprintf(stderr, "x7-datapart: %s: %s\n", dev, strerror(errno));
		return -1;
	}
	if (ioctl(fd, BLKGETSIZE64, &bytes) < 0 ||
	    pread(fd, c->mbr, SECTOR, 0) != SECTOR) {
		fprintf(stderr, "x7-datapart: cannot read %s: %s\n", dev, strerror(errno));
		close(fd);
		return -1;
	}
	c->sectors = bytes / SECTOR;
	c->start = start;
	c->data = c->sectors > start ? (c->sectors - start) / MIB_SECTORS * MIB_SECTORS : 0;
	memset(c->boot, 0, SECTOR);
	if (start < c->sectors && pread(fd, c->boot, SECTOR, (off_t)start * SECTOR) != SECTOR)
		memset(c->boot, 0, SECTOR);

	e1 = c->mbr + 446;
	e2 = c->mbr + 462;
	c->entry1_ok = c->mbr[510] == 0x55 && c->mbr[511] == 0xAA &&
		       (e1[4] == 0x0B || e1[4] == 0x0C) && le32(e1 + 8) == 2048;
	if (!e2[4] && !le32(e2 + 8) && !le32(e2 + 12))
		c->entry2 = 0;
	else if (le32(e2 + 8) == start)
		c->entry2 = 1;
	else
		c->entry2 = 2;

	/* a file system at the data partition's start? (structural checks) */
	c->fs = "none";
	c->fs_sectors = 0;
	if (c->boot[510] == 0x55 && c->boot[511] == 0xAA && c->data) {
		const uint8_t *b = c->boot;

		if (!memcmp(b + 3, "EXFAT   ", 8) && b[108] >= 9 && b[108] <= 12) {
			uint64_t len = le64(b + 72) << (b[108] - 9);	/* in 512-byte sectors */

			if (len > 0 && len <= c->sectors - start) {
				c->fs = "exfat";
				c->fs_sectors = len;
			}
		} else if (!memcmp(b + 3, "NTFS    ", 8)) {
			/* not usable by X7 Game, but someone's data: never format it */
			c->fs = "ntfs";
			c->fs_sectors = le64(b + 40);
		} else if (!memcmp(b + 82, "FAT32   ", 8)) {
			unsigned int bps = b[11] | b[12] << 8;
			uint64_t len = (uint64_t)le32(b + 32) * (bps / SECTOR);

			if ((bps == 512 || bps == 1024 || bps == 2048 || bps == 4096) &&
			    len > 0 && len <= c->sectors - start) {
				c->fs = "fat32";
				c->fs_sectors = len;
			}
		}
	}
	return fd;
}

int main(int argc, char **argv)
{
	struct card c;
	uint8_t check[SECTOR], *e2;
	unsigned long type;
	uint64_t start;
	int fd;

	if (argc < 4 || (strcmp(argv[1], "probe") && strcmp(argv[1], "write-entry")) ||
	    (!strcmp(argv[1], "write-entry") && argc != 5)) {
		fprintf(stderr, "usage: x7-datapart probe DEVICE START_LBA\n"
				"       x7-datapart write-entry DEVICE START_LBA TYPE\n");
		return 2;
	}
	start = strtoull(argv[3], NULL, 0);
	if (start < MIB_SECTORS) {
		fprintf(stderr, "x7-datapart: START_LBA %llu is too small\n", (unsigned long long)start);
		return 2;
	}

	if (!strcmp(argv[1], "probe")) {
		fd = load(argv[2], start, &c, O_RDONLY);
		if (fd < 0)
			return 1;
		close(fd);
		printf("card_sectors=%llu\nstart=%llu\ndata_sectors=%llu\ntoo_small=%d\n"
		       "entry1=%s\nentry2=%s\nfs=%s\nfs_sectors=%llu\n",
		       (unsigned long long)c.sectors, (unsigned long long)start,
		       (unsigned long long)c.data, c.data < MIN_DATA,
		       c.entry1_ok ? "ok" : "bad",
		       c.entry2 == 0 ? "absent" : c.entry2 == 1 ? "ours" : "other",
		       c.fs, (unsigned long long)c.fs_sectors);
		return 0;
	}

	type = strtoul(argv[4], NULL, 16);
	if (type != 0x07 && type != 0x0C) {
		fprintf(stderr, "x7-datapart: TYPE must be 07 (exFAT) or 0c (FAT32)\n");
		return 2;
	}
	fd = load(argv[2], start, &c, O_RDWR | O_SYNC);
	if (fd < 0)
		return 1;
	if (!c.entry1_ok || c.entry2 == 2 || c.data < MIN_DATA) {
		fprintf(stderr, "x7-datapart: refusing: %s\n",
			!c.entry1_ok ? "partition 1 is not the X7 Game boot partition" :
			c.entry2 == 2 ? "partition 2 is already something else" : "the card is too small");
		close(fd);
		return 1;
	}
	if (start + c.data > 0xFFFFFFFFULL)
		c.data = (0xFFFFFFFFULL - start) / MIB_SECTORS * MIB_SECTORS;	/* MBR limit: 2 TiB */
	e2 = c.mbr + 462;
	memset(e2, 0, 16);
	chs(e2 + 1, start);
	e2[4] = (uint8_t)type;
	chs(e2 + 5, start + c.data - 1);
	put32(e2 + 8, (uint32_t)start);
	put32(e2 + 12, (uint32_t)c.data);
	if (pwrite(fd, c.mbr, SECTOR, 0) != SECTOR || fsync(fd) ||
	    pread(fd, check, SECTOR, 0) != SECTOR || memcmp(check, c.mbr, SECTOR)) {
		fprintf(stderr, "x7-datapart: writing the partition table failed: %s\n", strerror(errno));
		close(fd);
		return 1;
	}
	close(fd);
	printf("partition 2: type %02lx, LBA %llu, %llu sectors (%llu MiB)\n", type,
	       (unsigned long long)start, (unsigned long long)c.data,
	       (unsigned long long)(c.data / MIB_SECTORS));
	return 0;
}

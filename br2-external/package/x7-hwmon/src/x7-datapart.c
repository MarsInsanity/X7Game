// SPDX-License-Identifier: GPL-3.0-or-later
/*
 * x7-datapart - the X7 Game data partition's entry in the SD card's
 * partition table (MBR).
 *
 *   x7-datapart probe       DEVICE START_LBA
 *   x7-datapart write-entry DEVICE START_LBA TYPE      (TYPE: 07 exFAT, 0c FAT32)
 *   x7-datapart fix-length  DEVICE START_LBA
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
 *   entry2_sectors=            partition 2's length in the MBR
 *   fs=exfat|fat32|ntfs|unknown|none
 *                              a file system at START_LBA (a re-flashed card
 *                              keeps its data partition: it is adopted, never
 *                              formatted again). ntfs is left alone, and so is
 *                              unknown: a known signature that fails the
 *                              checks, or a damaged exFAT boot sector whose
 *                              backup is good - somebody's data all the same
 *   fs_sectors=                its size in 512-byte sectors
 * "write-entry" sets entry 2 = START_LBA .. the exact end of the card (mkfs
 * formats all of /dev/mmcblk0p4, and the file system must not be larger than
 * the partition PCs see), only if entry 1 is ok and entry 2 is empty or
 * already ours.
 * "fix-length" extends an entry 2 of ours that is shorter than its exFAT or
 * FAT32 file system to the file system's size: earlier builds rounded the
 * length down to whole MiB. It never shrinks the entry or changes anything
 * else in it, and refuses when partition 3 or 4 exists.
 * Both read the sector back from the card to check. Only sector 0 is ever
 * written.
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
#include <sys/stat.h>
#include <unistd.h>

#define SECTOR		512
#define MIB_SECTORS	2048ULL
#define MIN_DATA	(64 * MIB_SECTORS)	/* at least 64 MiB, or no data partition */
#define MBR_LIMIT	0xFFFFFFFFULL		/* start + length must fit in 32 bits: 2 TiB */
#define EXFAT_BACKUP	12			/* exFAT's backup boot sector, from its start */

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

/*
 * Make the next read come from the card. The whole-card device's page cache
 * keeps a sector as it was read or written through /dev/mmcblk0, also after
 * mkfs or the exfat driver changed it through /dev/mmcblk0p4, and right after
 * a write it holds the written data itself. BLKFLSBUF needs root (it only
 * touches /dev/mmcblk0's own cache, not the mounted partitions');
 * posix_fadvise also works without it, and on an image file.
 */
static void drop_cache(int fd)
{
	if (ioctl(fd, BLKFLSBUF, 0) < 0)
		posix_fadvise(fd, 0, 0, POSIX_FADV_DONTNEED);
}

/* the size of an image file standing in for the card (tests on a PC) */
static int file_size(int fd, uint64_t *bytes)
{
	struct stat st;

	if (fstat(fd, &st) || !S_ISREG(st.st_mode))
		return -1;
	*bytes = st.st_size;
	return 0;
}

/*
 * The size of the exFAT volume a boot sector describes, in 512-byte sectors,
 * or 0 if it fails the structural checks or doesn't fit in room.
 */
static uint64_t exfat_sectors(const uint8_t *b, uint64_t room)
{
	unsigned int shift;
	uint64_t len;

	if (b[510] != 0x55 || b[511] != 0xAA || memcmp(b + 3, "EXFAT   ", 8) ||
	    b[108] < 9 || b[108] > 12)
		return 0;
	shift = b[108] - 9;
	len = le64(b + 72);
	/* compared before shifting, so that a huge length can't wrap around */
	if (!len || len > room >> shift)
		return 0;
	return len << shift;
}

struct card {
	uint8_t mbr[SECTOR], boot[SECTOR];
	uint64_t sectors, start, data;
	int entry1_ok, entry2;		/* entry2: 0 absent, 1 ours, 2 other */
	uint64_t entry2_sectors;
	const char *fs;
	uint64_t fs_sectors;
};

static int load(const char *dev, uint64_t start, struct card *c, int flags)
{
	uint64_t bytes;
	const uint8_t *e1, *e2, *b = c->boot;
	int fd = open(dev, flags | O_CLOEXEC);

	if (fd < 0) {
		fprintf(stderr, "x7-datapart: %s: %s\n", dev, strerror(errno));
		return -1;
	}
	drop_cache(fd);
	if ((ioctl(fd, BLKGETSIZE64, &bytes) < 0 && file_size(fd, &bytes)) ||
	    pread(fd, c->mbr, SECTOR, 0) != SECTOR) {
		fprintf(stderr, "x7-datapart: cannot read %s: %s\n", dev, strerror(errno));
		close(fd);
		return -1;
	}
	c->sectors = bytes / SECTOR;
	c->start = start;
	/* exact, not whole MiB: mkfs formats all of p4, which runs to the card's end */
	c->data = c->sectors > start ? c->sectors - start : 0;
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
	c->entry2_sectors = le32(e2 + 12);

	/*
	 * A file system at the data partition's start? (structural checks) A
	 * known signature that fails them is "unknown", and so is a damaged
	 * exFAT boot sector with a good backup (Linux rewrites the main one on
	 * every mount, so a power cut can tear it): somebody's data either way,
	 * never formatted. Anything else - zeros, or leftovers of old files on
	 * a reused card - is "none".
	 */
	c->fs = "none";
	c->fs_sectors = 0;
	if (c->data) {
		int marker = b[510] == 0x55 && b[511] == 0xAA;

		if (!memcmp(b + 3, "EXFAT   ", 8)) {
			c->fs_sectors = exfat_sectors(b, c->data);
			c->fs = c->fs_sectors ? "exfat" : "unknown";
		} else if (!memcmp(b + 3, "NTFS    ", 8)) {
			/* not usable by X7 Game, but someone's data: never format it */
			if (marker) {
				c->fs = "ntfs";
				c->fs_sectors = le64(b + 40);
			} else {
				c->fs = "unknown";
			}
		} else if (!memcmp(b + 82, "FAT32   ", 8)) {
			unsigned int bps = b[11] | b[12] << 8;
			uint64_t len = (uint64_t)le32(b + 32) * (bps / SECTOR);

			if (marker && (bps == 512 || bps == 1024 || bps == 2048 || bps == 4096) &&
			    len > 0 && len <= c->data) {
				c->fs = "fat32";
				c->fs_sectors = len;
			} else {
				c->fs = "unknown";
			}
		} else if (!memcmp(b + 54, "FAT16   ", 8) || !memcmp(b + 54, "FAT12   ", 8)) {
			c->fs = "unknown";	/* X7 Game makes neither */
		} else {
			uint8_t backup[SECTOR];

			if (start + EXFAT_BACKUP < c->sectors &&
			    pread(fd, backup, SECTOR, (off_t)(start + EXFAT_BACKUP) * SECTOR) == SECTOR &&
			    exfat_sectors(backup, c->data))
				c->fs = "unknown";
		}
	}
	return fd;
}

/*
 * Write sector 0 and read it back from the card. After fsync the page cache
 * still holds the sector just written; without dropping it the check would
 * only compare the buffer with itself.
 */
static int write_mbr(int fd, const struct card *c)
{
	uint8_t check[SECTOR];

	if (pwrite(fd, c->mbr, SECTOR, 0) != SECTOR || fsync(fd))
		return -1;
	drop_cache(fd);
	if (pread(fd, check, SECTOR, 0) != SECTOR)
		return -1;
	if (memcmp(check, c->mbr, SECTOR)) {
		errno = EIO;	/* the card didn't keep what was written */
		return -1;
	}
	return 0;
}

/* one line for the kernel log (x7-report shows it); skipped if not allowed */
static void log_kmsg(const char *line)
{
	int fd = open("/dev/kmsg", O_WRONLY | O_CLOEXEC);

	if (fd >= 0) {
		if (write(fd, line, strlen(line)) < 0) {
			/* nothing else to tell it to */
		}
		close(fd);
	}
}

/* an MBR entry (16 bytes) that is in use: a type, a start or a length */
static int entry_used(const uint8_t *e)
{
	return e[4] || le32(e + 8) || le32(e + 12);
}

/*
 * Earlier builds wrote entry 2's length rounded down to whole MiB while mkfs
 * formatted all of /dev/mmcblk0p4, so on cards whose size isn't a whole MiB
 * the file system runs up to 1 MiB past the partition PCs see, and they may
 * refuse it. Extend the entry to the file system's size: only its length
 * and the CHS end that follows from it change, and only to grow it.
 */
static int fix_length(const char *dev, uint64_t start)
{
	struct card c;
	char line[128];
	const char *why = NULL;
	uint64_t len;
	uint8_t *e2;
	int fd = load(dev, start, &c, O_RDWR | O_SYNC);

	if (fd < 0)
		return 1;
	len = c.fs_sectors;
	if (start + len > MBR_LIMIT)
		len = MBR_LIMIT - start;
	if (!c.entry1_ok)
		why = "partition 1 is not the X7 Game boot partition";
	else if (c.entry2 != 1)
		why = "partition 2 is not the data partition";
	else if (entry_used(c.mbr + 478) || entry_used(c.mbr + 494))
		/* X7 Game never makes them: someone partitioned this card on a
		 * PC, and the longer entry 2 could overlap them */
		why = "partition 3 or 4 exists";
	else if (strcmp(c.fs, "exfat") && strcmp(c.fs, "fat32"))
		why = "the data partition holds no exFAT or FAT32 file system";
	else if (c.fs_sectors > c.data)
		why = "the file system is larger than the rest of the card";
	else if (len <= c.entry2_sectors)
		why = "partition 2 already covers the file system";
	if (why) {
		fprintf(stderr, "x7-datapart: refusing: %s\n", why);
		close(fd);
		return 1;
	}
	e2 = c.mbr + 462;
	chs(e2 + 5, start + len - 1);
	put32(e2 + 12, (uint32_t)len);
	if (write_mbr(fd, &c)) {
		fprintf(stderr, "x7-datapart: writing the partition table failed: %s\n", strerror(errno));
		close(fd);
		return 1;
	}
	close(fd);
	printf("partition 2: extended from %llu to %llu sectors\n",
	       (unsigned long long)c.entry2_sectors, (unsigned long long)len);
	snprintf(line, sizeof(line), "<5>x7game: X7DATA partition entry extended from %llu to %llu sectors\n",
		 (unsigned long long)c.entry2_sectors, (unsigned long long)len);
	log_kmsg(line);
	return 0;
}

int main(int argc, char **argv)
{
	struct card c;
	uint8_t *e2;
	unsigned long type;
	uint64_t start;
	int fd;

	if (argc < 4 || (strcmp(argv[1], "probe") && strcmp(argv[1], "write-entry") &&
			 strcmp(argv[1], "fix-length")) ||
	    (!strcmp(argv[1], "write-entry") && argc != 5)) {
		fprintf(stderr, "usage: x7-datapart probe DEVICE START_LBA\n"
				"       x7-datapart write-entry DEVICE START_LBA TYPE\n"
				"       x7-datapart fix-length DEVICE START_LBA\n");
		return 2;
	}
	start = strtoull(argv[3], NULL, 0);
	if (start < MIB_SECTORS) {
		fprintf(stderr, "x7-datapart: START_LBA %llu is too small\n", (unsigned long long)start);
		return 2;
	}
	if (start >= MBR_LIMIT) {
		fprintf(stderr, "x7-datapart: START_LBA %llu is past the MBR's 2 TiB limit\n",
			(unsigned long long)start);
		return 2;
	}

	if (!strcmp(argv[1], "probe")) {
		fd = load(argv[2], start, &c, O_RDONLY);
		if (fd < 0)
			return 1;
		close(fd);
		printf("card_sectors=%llu\nstart=%llu\ndata_sectors=%llu\ntoo_small=%d\n"
		       "entry1=%s\nentry2=%s\nentry2_sectors=%llu\nfs=%s\nfs_sectors=%llu\n",
		       (unsigned long long)c.sectors, (unsigned long long)start,
		       (unsigned long long)c.data, c.data < MIN_DATA,
		       c.entry1_ok ? "ok" : "bad",
		       c.entry2 == 0 ? "absent" : c.entry2 == 1 ? "ours" : "other",
		       (unsigned long long)c.entry2_sectors,
		       c.fs, (unsigned long long)c.fs_sectors);
		return 0;
	}
	if (!strcmp(argv[1], "fix-length"))
		return fix_length(argv[2], start);

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
	/*
	 * The exact rest of the card. Not the file system's size as read back
	 * here: right after mkfs that read could still come from the cache
	 * (if dropping it failed), as the sector was before mkfs. mkfs always
	 * formats all of p4, so the two are the same.
	 */
	if (start + c.data > MBR_LIMIT)
		c.data = MBR_LIMIT - start;
	e2 = c.mbr + 462;
	memset(e2, 0, 16);
	chs(e2 + 1, start);
	e2[4] = (uint8_t)type;
	chs(e2 + 5, start + c.data - 1);
	put32(e2 + 8, (uint32_t)start);
	put32(e2 + 12, (uint32_t)c.data);
	if (write_mbr(fd, &c)) {
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

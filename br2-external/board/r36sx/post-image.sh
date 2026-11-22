#!/bin/bash
# Buildroot post-image: build the boot files, the SD card image(s) and the
# update file(s).
#
# Always:   x7game-r36sx-<version>.img        flash this onto a card
#           x7game-r36sx-<version>.x7update   copy this into X7DATA to update
#           for consoles whose bootloader loads unencrypted boot files - the
#           R36SX / R36S V2.6 firmware stack (also on V2.7 hardware running
#           it). Boot files are plain uImages, like the stock V2.6 card's.
# Optional: x7game-r36sx-v27protected-<version>.img / .x7update
#           for "bootloader protected" V2.7 consoles; only built when the
#           wrapper key is given in X7_V27_KEY (64 hex digits, e.g. a GitHub
#           Actions secret). The key is never printed or stored.
set -euo pipefail

BOARD=$(cd "$(dirname "$0")" && pwd)
OUT=$BINARIES_DIR
VERSION=${X7_VERSION:-dev}

# ---- SD card layout (MiB); layout 2. The kernel command line, x7-update and
# S05x7data must match. ----
#   0 ..    1  partition table
#   1 ..   49  partition 1: FAT32 "X7GAME" (boot files, settings, logs)
#  49 ..  536  system slot A (squashfs root, hidden)    /dev/mmcblk0p2
# 536 .. 1024  system slot B (squashfs root, hidden)    /dev/mmcblk0p3
# 1024 .. end  the data partition "X7DATA", made at the first start
#              (S05x7data, x7-datapart)                  /dev/mmcblk0p4
# The card image starts on slot A. An update (x7-update) writes the other
# slot and switches the kernel files to the kernel built for that slot. The
# data partition's start must never move: re-flashed cards keep it.
LAYOUT=2
FAT_MIB=48
SLOT_A_MIB=487
SLOT_B_MIB=488
DATA_START_MIB=1024
[ $((1 + FAT_MIB + SLOT_A_MIB + SLOT_B_MIB)) = "$DATA_START_MIB" ] || { echo "layout does not add up"; exit 1; }
PARTS="blkdevparts=mmcblk0:${FAT_MIB}M@1M(x7boot),${SLOT_A_MIB}M(x7rootA),${SLOT_B_MIB}M(x7rootB),-(x7data)"
# bootargs for a kernel that starts system slot $1 (A or B)
bootargs() {
	local root=/dev/mmcblk0p2
	[ "$1" = B ] && root=/dev/mmcblk0p3
	echo "console=tty0 root=$root rootfstype=squashfs ro rootwait $PARTS" \
		"panic=0 clk_ignore_unused nzclk=900 consoleblank=0 loglevel=5 vt.global_cursor_default=0"
}

# first existing file of a list (no pipelines: pipefail + a missing file
# would stop the script silently)
first() {
	local f
	for f in "$@"; do
		[ -e "$f" ] && { echo "$f"; return 0; }
	done
	return 0
}
gcc=$(first "$HOST_DIR"/bin/mipsel-*-linux-gnu-gcc)
[ -n "$gcc" ] || { echo "no mipsel cross gcc in $HOST_DIR/bin"; exit 1; }
CROSS=${gcc%gcc}
MKFS=$(first "$HOST_DIR"/sbin/mkfs.fat "$HOST_DIR"/bin/mkfs.fat "$HOST_DIR"/sbin/mkfs.vfat \
	"$HOST_DIR"/bin/mkfs.vfat)
[ -n "$MKFS" ] || { echo "mkfs.fat not found in $HOST_DIR (host-dosfstools)"; exit 1; }
MCOPY=$HOST_DIR/bin/mcopy
export MTOOLS_SKIP_CHECK=1

key_args=()
if [ -n "${X7_V27_KEY:-}" ]; then
	key_args=(--v27-key "$X7_V27_KEY")
fi
SYSMAP=$(first "$BUILD_DIR"/linux-custom/System.map)
for slot in A B; do
	echo ">>> X7 Game: boot files for system slot $slot"
	python3 "$BOARD/mkx7boot.py" --vmlinux "$OUT/vmlinux" ${SYSMAP:+--system-map "$SYSMAP"} \
		--dts "$BOARD/x7game-r36sx.dts" \
		--bootargs "$(bootargs $slot)" --cross "$CROSS" --dtc "$HOST_DIR/bin/dtc" \
		--out "$OUT/boot-files-$slot" "${key_args[@]}"
done
rm -rf "$OUT/boot-files"
cp -r "$OUT/boot-files-A" "$OUT/boot-files"	# what the card image uses

root_bytes=$(stat -c %s "$OUT/rootfs.squashfs")
echo ">>> X7 Game: root file system $root_bytes bytes (room for $((SLOT_A_MIB * 1024 * 1024)) per slot)"
[ "$root_bytes" -le $((SLOT_A_MIB * 1024 * 1024)) ] || { echo "rootfs.squashfs is too big for a $SLOT_A_MIB MiB slot"; exit 1; }

python3 "$BOARD/mklogo.py" "$OUT/boot-files/xgame-logo.bmp"
sed "s/@VERSION@/$VERSION/" "$BOARD/sdcard/VERSION.txt" > "$OUT/boot-files/VERSION.txt"

# make_card NAME KERNEL AVP STOCK_DIR
make_card() {
	local name=$1 kernel=$2 avp=$3 stock=$4
	local fs=$OUT/fat-$name img=$OUT/$name.img fat=$OUT/$name.vfat
	echo ">>> X7 Game: $name.img"
	rm -rf "$fs" "$fat"
	mkdir -p "$fs/cubegm" "$fs/x7game/logs"
	# The bootloader looks for these names (both sets exist on stock cards):
	# kernel, AVP firmware (here a stand-in), board file, power-on picture.
	cp "$kernel" "$fs/cubegm/advapi32.dll"
	cp "$kernel" "$fs/cubegm/vmlinux.uImage"
	cp "$avp" "$fs/cubegm/ApplicationFrame.dll"
	cp "$avp" "$fs/cubegm/avp.uImage"
	cp "$stock/Bubbles.scr" "$fs/cubegm/Bubbles.scr"
	cp "$stock/dtb.bin" "$fs/cubegm/dtb.bin"
	cp "$OUT/boot-files/xgame-logo.bmp" "$fs/cubegm/xgame-logo.bmp"
	cp "$BOARD/sdcard/x7game.cfg" "$fs/x7game/x7game.cfg"
	cp "$BOARD/sdcard/README.txt" "$fs/x7game/README.txt"
	cp "$OUT/boot-files/VERSION.txt" "$fs/x7game/VERSION.txt"
	touch "$fs/x7game/logs/.keep"
	# FAT32 like a PC formats it: hidden sectors = partition start (LBA 2048)
	"$MKFS" -F 32 -s 1 -S 512 -h 2048 -n X7GAME -i 58374741 -C "$fat" $((FAT_MIB * 1024)) > /dev/null
	"$MCOPY" -i "$fat" -s -p -m "$fs/cubegm" "$fs/x7game" ::/
	python3 "$BOARD/mkdisk.py" --fat "$fat" --root "$OUT/rootfs.squashfs" \
		--fat-mib "$FAT_MIB" --root-mib "$SLOT_A_MIB" --out "$img"
	rm -f "$fat"
}

# make_update NAME VARIANT KERNEL_A KERNEL_B AVP STOCK_DIR
make_update() {
	echo ">>> X7 Game: $1.x7update"
	python3 "$BOARD/mkupdate.py" --out "$OUT/$1.x7update" --version "$VERSION" \
		--commit "${X7_COMMIT:-unknown}" --variant "$2" --layout "$LAYOUT" \
		--kernel-a "$3" --kernel-b "$4" --avp "$5" --stock "$6" \
		--logo "$OUT/boot-files/xgame-logo.bmp" --readme "$BOARD/sdcard/README.txt" \
		--version-txt "$OUT/boot-files/VERSION.txt" --root "$OUT/rootfs.squashfs"
}

make_card "x7game-r36sx-$VERSION" "$OUT/boot-files-A/kernel.uImage" "$OUT/boot-files-A/avp.uImage" \
	"$BOARD/stock/v2.6"
make_update "x7game-r36sx-$VERSION" plain "$OUT/boot-files-A/kernel.uImage" \
	"$OUT/boot-files-B/kernel.uImage" "$OUT/boot-files-A/avp.uImage" "$BOARD/stock/v2.6"
if [ -f "$OUT/boot-files-A/kernel-v27.dll" ]; then
	make_card "x7game-r36sx-v27protected-$VERSION" "$OUT/boot-files-A/kernel-v27.dll" \
		"$OUT/boot-files-A/avp-v27.dll" "$BOARD/stock/v2.7"
	make_update "x7game-r36sx-v27protected-$VERSION" v27protected "$OUT/boot-files-A/kernel-v27.dll" \
		"$OUT/boot-files-B/kernel-v27.dll" "$OUT/boot-files-A/avp-v27.dll" "$BOARD/stock/v2.7"
fi
echo ">>> X7 Game: images and updates in $OUT:"
ls -l "$OUT"/x7game-*.img "$OUT"/x7game-*.x7update

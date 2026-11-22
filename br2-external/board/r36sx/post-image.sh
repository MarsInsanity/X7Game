#!/bin/bash
# Buildroot post-image: build the boot files and the SD card image(s).
#
# Always:   x7game-r36sx-<version>.img
#           for consoles whose bootloader loads unencrypted boot files - the
#           R36SX / R36S V2.6 firmware stack (also on V2.7 hardware running
#           it). Boot files are plain uImages, like the stock V2.6 card's.
# Optional: x7game-r36sx-v27protected-<version>.img
#           for "bootloader protected" V2.7 consoles; only built when the
#           wrapper key is given in X7_V27_KEY (64 hex digits, e.g. a GitHub
#           Actions secret). The key is never printed or stored.
set -euo pipefail

BOARD=$(cd "$(dirname "$0")" && pwd)
OUT=$BINARIES_DIR
VERSION=${X7_VERSION:-dev}

# ---- SD card layout (MiB); the kernel command line must match ----
FAT_MIB=48
ROOT_MIB=24
BOOTARGS="console=tty0 root=/dev/mmcblk0p2 rootfstype=squashfs ro rootwait"
BOOTARGS+=" blkdevparts=mmcblk0:${FAT_MIB}M@1M(x7boot),${ROOT_MIB}M(x7root)"
BOOTARGS+=" panic=0 clk_ignore_unused nzclk=900 consoleblank=0 loglevel=5"
BOOTARGS+=" vt.global_cursor_default=0"

gcc=$(ls "$HOST_DIR"/bin/mipsel-*-linux-gnu-gcc | head -n 1)
CROSS=${gcc%gcc}
MKFS=$(ls "$HOST_DIR"/sbin/mkfs.fat "$HOST_DIR"/bin/mkfs.fat "$HOST_DIR"/sbin/mkfs.vfat \
	"$HOST_DIR"/bin/mkfs.vfat 2>/dev/null | head -n 1)
[ -n "$MKFS" ] || { echo "mkfs.fat not found in $HOST_DIR (host-dosfstools)"; exit 1; }
MCOPY=$HOST_DIR/bin/mcopy
export MTOOLS_SKIP_CHECK=1

echo ">>> X7 Game: boot files"
key_args=()
if [ -n "${X7_V27_KEY:-}" ]; then
	key_args=(--v27-key "$X7_V27_KEY")
fi
SYSMAP=$(ls "$BUILD_DIR"/linux-custom/System.map 2>/dev/null | head -n 1)
python3 "$BOARD/mkx7boot.py" --vmlinux "$OUT/vmlinux" ${SYSMAP:+--system-map "$SYSMAP"} \
	--dts "$BOARD/x7game-r36sx.dts" \
	--bootargs "$BOOTARGS" --cross "$CROSS" --dtc "$HOST_DIR/bin/dtc" \
	--out "$OUT/boot-files" "${key_args[@]}"

root_bytes=$(stat -c %s "$OUT/rootfs.squashfs")
echo ">>> X7 Game: root file system $root_bytes bytes (room for $((ROOT_MIB * 1024 * 1024)))"
[ "$root_bytes" -le $((ROOT_MIB * 1024 * 1024)) ] || { echo "rootfs.squashfs is too big for the $ROOT_MIB MiB area"; exit 1; }

python3 "$BOARD/mklogo.py" "$OUT/boot-files/xgame-logo.bmp"

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
	sed "s/@VERSION@/$VERSION/" "$BOARD/sdcard/VERSION.txt" > "$fs/x7game/VERSION.txt"
	touch "$fs/x7game/logs/.keep"
	# FAT32 like a PC formats it: hidden sectors = partition start (LBA 2048)
	"$MKFS" -F 32 -s 1 -S 512 -h 2048 -n X7GAME -i 58374741 -C "$fat" $((FAT_MIB * 1024)) > /dev/null
	"$MCOPY" -i "$fat" -s -p -m "$fs/cubegm" "$fs/x7game" ::/
	python3 "$BOARD/mkdisk.py" --fat "$fat" --root "$OUT/rootfs.squashfs" \
		--fat-mib "$FAT_MIB" --root-mib "$ROOT_MIB" --out "$img"
	rm -f "$fat"
}

make_card "x7game-r36sx-$VERSION" "$OUT/boot-files/kernel.uImage" "$OUT/boot-files/avp.uImage" \
	"$BOARD/stock/v2.6"
if [ -f "$OUT/boot-files/kernel-v27.dll" ]; then
	make_card "x7game-r36sx-v27protected-$VERSION" "$OUT/boot-files/kernel-v27.dll" \
		"$OUT/boot-files/avp-v27.dll" "$BOARD/stock/v2.7"
fi
echo ">>> X7 Game: images in $OUT:"
ls -l "$OUT"/x7game-*.img

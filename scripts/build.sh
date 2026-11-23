#!/bin/bash
# Build X7 Game (what the GitHub workflow runs; also works on a Linux PC with
# Buildroot's usual host packages).
#
# On WSL: clone X7 Game into the Linux home directory, not under /mnt/c (the
# Windows drives are case-insensitive, and the kernel has files whose names
# differ only in case), run with a PATH without the Windows entries
# (Buildroot refuses a PATH with spaces; e.g. set appendWindowsPath=false in
# /etc/wsl.conf), and keep OUTPUT_DIR on the Linux file system too.
#
#   scripts/build.sh [OUTPUT_DIR]          default: output/ in this checkout
#
# Environment (all optional):
#   X7_VERSION   version shown on the console and in file names (default: dev)
#   X7_COMMIT    commit shown on the console (default: short hash of HEAD)
#   X7_V27_KEY   64 hex digits: also build the image for "bootloader
#                protected" V2.7 consoles (never printed)
#   BR_DIR       an existing Buildroot checkout (default: buildroot/ in this
#                checkout; cloned when missing)
#   BR_VERSION   the Buildroot release to clone, and that BR_DIR must be
#                (default: 2026.02.3; the GitHub workflow sets it)
#   JOBS         parallel jobs (default: number of CPUs)
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
# made absolute: Buildroot (make -C) would resolve a relative O= against its
# own directory, while this script reads $OUT/.config from here
OUT=${1:-$ROOT/output}
mkdir -p "$OUT"
OUT=$(cd "$OUT" && pwd)
BR_VERSION=${BR_VERSION:-2026.02.3}
BR_DIR=${BR_DIR:-$ROOT/buildroot}
EXT=$ROOT/br2-external
DEFCONFIG=x7game_r36sx_defconfig
export X7_VERSION=${X7_VERSION:-dev}
export X7_COMMIT=${X7_COMMIT:-$(git -C "$ROOT" rev-parse --short HEAD 2>/dev/null || echo unknown)}
# both end up in file names and in post-image.sh's sed program: check them
# now (the same rule as the GitHub workflow), not after hours of building
case "$X7_VERSION$X7_COMMIT" in *[!A-Za-z0-9._-]*) echo "bad X7_VERSION/X7_COMMIT" >&2; exit 1 ;; esac

if [ ! -d "$BR_DIR/.git" ] && [ ! -f "$BR_DIR/Makefile" ]; then
	# git clone refuses a non-empty directory; say why instead
	if [ -e "$BR_DIR" ] && [ -n "$(ls -A "$BR_DIR" 2>/dev/null)" ]; then
		echo "BR_DIR $BR_DIR exists but is neither a git checkout nor a Buildroot tree" >&2
		exit 1
	fi
	git clone --depth 1 -b "$BR_VERSION" https://gitlab.com/buildroot.org/buildroot.git "$BR_DIR"
fi
# a reused checkout may be an older pin or another release: the defconfig
# check below would not notice, but the toolchain and packages would differ
have=$(sed -n 's/^export BR2_VERSION := //p' "$BR_DIR/Makefile" 2>/dev/null || true)
if [ -z "$have" ]; then
	echo "BR_DIR $BR_DIR is not a Buildroot tree (no BR2_VERSION in its Makefile)" >&2
	exit 1
elif [ "$have" != "$BR_VERSION" ]; then
	echo "BR_DIR $BR_DIR is Buildroot $have, not $BR_VERSION: remove it or point BR_DIR at a $BR_VERSION checkout" >&2
	exit 1
fi
echo ">>> Buildroot $have, X7 Game $X7_VERSION ($X7_COMMIT)"

make -C "$BR_DIR" BR2_EXTERNAL="$EXT" O="$OUT" "$DEFCONFIG"
# every line of our defconfig must have survived (a typo would vanish silently)
missing=0
while IFS= read -r line; do
	case "$line" in
	BR2_*=*) grep -qxF "$line" "$OUT/.config" || { echo "MISSING from .config: $line"; missing=1; } ;;
	esac
done < "$EXT/configs/$DEFCONFIG"
[ "$missing" = 0 ] || exit 1

# toolchain + kernel configuration first, then check the kernel options
make -C "$OUT" -j"${JOBS:-$(nproc)}" linux-configure
"$ROOT/scripts/check-kernel-config.sh" "$OUT"
make -C "$OUT" -j"${JOBS:-$(nproc)}"
echo ">>> done:"
ls -l "$OUT"/images/x7game-*.img

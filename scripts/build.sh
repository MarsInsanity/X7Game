#!/bin/bash
# Build X7 Game (what the GitHub workflow runs; also works on any Linux PC
# or WSL with Buildroot's usual host packages).
#
#   scripts/build.sh [OUTPUT_DIR]          default: ./output
#
# Environment (all optional):
#   X7_VERSION   version shown on the console and in file names (default: dev)
#   X7_V27_KEY   64 hex digits: also build the image for "bootloader
#                protected" V2.7 consoles (never printed)
#   BR_DIR       an existing Buildroot checkout (default: ./buildroot)
#   JOBS         parallel jobs (default: number of CPUs)
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
OUT=${1:-$ROOT/output}
BR_VERSION=2026.02.3
BR_DIR=${BR_DIR:-$ROOT/buildroot}
EXT=$ROOT/br2-external
DEFCONFIG=x7game_r36sx_defconfig
export X7_VERSION=${X7_VERSION:-dev}
export X7_COMMIT=${X7_COMMIT:-$(git -C "$ROOT" rev-parse --short HEAD 2>/dev/null || echo unknown)}

if [ ! -d "$BR_DIR/.git" ]; then
	git clone --depth 1 -b "$BR_VERSION" https://gitlab.com/buildroot.org/buildroot.git "$BR_DIR"
fi
echo ">>> Buildroot $(git -C "$BR_DIR" describe --tags 2>/dev/null || echo '?'), X7 Game $X7_VERSION ($X7_COMMIT)"

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

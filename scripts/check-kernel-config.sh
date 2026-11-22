#!/bin/bash
# Fail if olddefconfig dropped any option of our kernel fragment (an unmet
# dependency silently removes it).   check-kernel-config.sh OUTPUT_DIR
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
FRAGMENT=$ROOT/br2-external/board/r36sx/linux-x7.fragment
config=$(ls -d "$1"/build/linux-*/.config 2>/dev/null | grep -v headers | head -n 1)
[ -f "$config" ] || { echo "no kernel .config under $1/build"; exit 1; }
bad=0
while IFS= read -r line; do
	case "$line" in
	CONFIG_*=*)
		grep -qxF "$line" "$config" || { echo "kernel option lost: $line (now: $(grep "^${line%%=*}=" "$config" || echo unset))"; bad=1; } ;;
	"# CONFIG_"*" is not set")
		opt=${line#\# }; opt=${opt%% *}
		if grep -q "^$opt=" "$config"; then echo "kernel option should be off: $opt"; bad=1; fi ;;
	esac
done < "$FRAGMENT"
[ "$bad" = 0 ] && echo "kernel config: all X7 Game options present ($config)"
exit $bad

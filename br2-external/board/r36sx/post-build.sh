#!/bin/sh
# Buildroot post-build: $1 = the target directory.
set -e
TARGET=$1

mkdir -p "$TARGET/boot" "$TARGET/root"
chmod 0755 "$TARGET"/etc/init.d/S*x7* "$TARGET"/usr/bin/x7-* \
	"$TARGET/usr/sbin/x7-usb-gadget" "$TARGET/usr/sbin/x7-report" "$TARGET/usr/libexec/x7-usb-shell"

cat > "$TARGET/etc/x7game-release" <<EOF
X7_VERSION=${X7_VERSION:-dev}
X7_BOARD=r36sx
X7_COMMIT=${X7_COMMIT:-unknown}
BUILDROOT=${BR2_VERSION:-unknown}
EOF

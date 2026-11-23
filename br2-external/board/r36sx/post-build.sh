#!/bin/sh
# Buildroot post-build: $1 = the target directory.
set -e
TARGET=$1

mkdir -p "$TARGET/boot" "$TARGET/root" "$TARGET/share" "$TARGET/usr/share/x7game"
# the legacy uImage magic, for x7-update (plain or V2.7-wrapped boot files)
printf '\047\005\031\126' > "$TARGET/usr/share/x7game/uimage-magic"
chmod 0755 "$TARGET"/etc/init.d/S*x7* "$TARGET"/usr/bin/x7-* \
	"$TARGET/usr/sbin/x7-usb-gadget" "$TARGET/usr/sbin/x7-report" "$TARGET/usr/sbin/x7-update" "$TARGET/usr/sbin/x7-datarepair" "$TARGET/usr/libexec/x7-usb-shell"

# Start scripts with nothing to do: there is no /etc/sysctl.conf or
# /etc/sysctl.d (S02sysctl would still run find, xargs and logger at every
# boot), and the kernel has no module support (S11modules). The sysctl
# applet stays for the USB shell. Bring S02sysctl back if a sysctl file is
# ever added.
rm -f "$TARGET/etc/init.d/S02sysctl" "$TARGET/etc/init.d/S11modules"

# Audio files nothing uses: the speaker-test voice samples and data
# (x7-soundtest only plays sine tones) and alsa-lib's shared-memory sound
# server. alsa.conf, cards/ and pcm/ in /usr/share/alsa must stay.
rm -rf "$TARGET/usr/share/sounds/alsa" "$TARGET/usr/share/alsa/speaker-test"
rm -f "$TARGET/usr/bin/aserver"

# exfatprogs: only mkfs.exfat (S05x7data) and fsck.exfat (x7-datarepair) are
# used; the other tools are for PCs and the shell.
rm -f "$TARGET"/usr/sbin/tune.exfat "$TARGET"/usr/sbin/exfatlabel \
	"$TARGET"/usr/sbin/dump.exfat "$TARGET"/usr/sbin/exfat2img

cat > "$TARGET/etc/x7game-release" <<EOF
X7_VERSION=${X7_VERSION:-dev}
X7_BOARD=r36sx
X7_COMMIT=${X7_COMMIT:-unknown}
BUILDROOT=${BR2_VERSION:-unknown}
EOF

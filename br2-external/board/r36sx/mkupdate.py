#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Build an X7 Game update file (.x7update) - a plain tar archive.

The user copies it into X7DATA; at the next start x7-update checks it,
writes the new system into the system slot that is not running, switches
the boot files and restarts. Contents (all under x7update/):

  manifest              X7U_FORMAT, X7U_BOARD, X7U_VARIANT, X7U_LAYOUT,
                        X7U_VERSION, X7U_COMMIT, X7U_ROOT_BYTES
  SHA256SUMS            "sha256  path" for every file below
  boot/kernel-a.uImage  kernel that starts system slot A (root=/dev/mmcblk0p2)
  boot/kernel-b.uImage  kernel that starts system slot B (root=/dev/mmcblk0p3)
  boot/avp.uImage       AVP stand-in
  boot/Bubbles.scr, boot/dtb.bin   stock board files
  boot/xgame-logo.bmp   power-on picture
  boot/README.txt, boot/VERSION.txt   for x7game/ on X7GAME
  root/rootfs.squashfs  the system

For "v27protected" the kernel and AVP files are in the V2.7 wrapper.
"""
import argparse
import hashlib
import io
import tarfile
from pathlib import Path


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for name in ('out', 'kernel-a', 'kernel-b', 'avp', 'stock', 'logo', 'readme', 'version-txt', 'root'):
        ap.add_argument('--' + name, type=Path, required=True)
    ap.add_argument('--version', required=True)
    ap.add_argument('--commit', default='unknown')
    ap.add_argument('--variant', choices=('plain', 'v27protected'), required=True)
    ap.add_argument('--layout', type=int, required=True)
    a = ap.parse_args()

    files = {
        'boot/kernel-a.uImage': a.kernel_a,
        'boot/kernel-b.uImage': a.kernel_b,
        'boot/avp.uImage': a.avp,
        'boot/Bubbles.scr': a.stock / 'Bubbles.scr',
        'boot/dtb.bin': a.stock / 'dtb.bin',
        'boot/xgame-logo.bmp': a.logo,
        'boot/README.txt': a.readme,
        'boot/VERSION.txt': a.version_txt,
        'root/rootfs.squashfs': a.root,
    }
    data = {path: src.read_bytes() for path, src in files.items()}
    assert data['boot/kernel-a.uImage'] != data['boot/kernel-b.uImage'], 'slot kernels are identical'
    assert data['root/rootfs.squashfs'][:4] == b'hsqs', 'root is not a squashfs'
    for v in (a.version, a.commit):
        assert all(c.isalnum() or c in '._-' for c in v), f'bad characters in {v!r}'
    manifest = (f'X7U_FORMAT=1\nX7U_BOARD=r36sx\nX7U_VARIANT={a.variant}\nX7U_LAYOUT={a.layout}\n'
                f'X7U_VERSION={a.version}\nX7U_COMMIT={a.commit}\n'
                f'X7U_ROOT_BYTES={len(data["root/rootfs.squashfs"])}\n').encode()
    sums = ''.join(f'{hashlib.sha256(b).hexdigest()}  {p}\n' for p, b in data.items()).encode()

    with tarfile.open(a.out, 'w', format=tarfile.USTAR_FORMAT) as tar:
        def add(name, blob, mode=0o644):
            info = tarfile.TarInfo('x7update/' + name)
            info.size, info.mode, info.mtime, info.uname, info.gname = len(blob), mode, 0, 'root', 'root'
            tar.addfile(info, io.BytesIO(blob))
        add('manifest', manifest)
        add('SHA256SUMS', sums)
        for path, blob in data.items():
            add(path, blob)
    total = a.out.stat().st_size
    print(f'{a.out.name}: {total} bytes, {a.variant}, X7 Game {a.version}, '
          f'sha256 {hashlib.sha256(a.out.read_bytes()).hexdigest()}')


if __name__ == '__main__':
    main()

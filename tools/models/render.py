# SPDX-License-Identifier: GPL-3.0-or-later
"""
render.py - preview an X7 Game model the way the frontend will show it:
320x240, 16-bit colour (RGB565), flat-shaded triangles, back faces culled,
then doubled to 640x480 for viewing (nearest neighbour, like the console's
hardware scaler). Pure Python, no extra packages.

    python tools/models/render.py MODEL.obj [-o OUT.png] [--yaw 35] [--pitch 22]
                                  [--views "35,22;-145,22"] [--nocull] [--scale 2]

--views renders several angles side by side (yaw,pitch;yaw,pitch...).
--nocull draws back faces too, in magenta: any magenta in a normal render
         means a triangle is wound the wrong way (it would vanish on the
         console).
The camera looks at the model's bounding box from the front-right-above
(yaw 35 = turned 35 degrees to the right, pitch 22 = looking down).
"""
import argparse
import math
import os
import struct
import sys
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from x7model import load_obj, rgb565  # noqa: E402

W, H = 320, 240
BG_TOP, BG_BOTTOM = (52, 58, 74), (22, 24, 32)
LIGHT = (-0.45, 0.80, 0.55)        # key light: up, left, towards the viewer
FILL = (0.6, 0.2, -0.4)            # weak fill from behind right


def _norm(a):
    l = math.sqrt(a[0] * a[0] + a[1] * a[1] + a[2] * a[2])
    return (a[0] / l, a[1] / l, a[2] / l) if l else (0, 0, 0)


def render(verts, tris, yaw, pitch, nocull=False, w=W, h=H):
    # model centre and size
    xs = [v[0] for v in verts]
    ys = [v[1] for v in verts]
    zs = [v[2] for v in verts]
    cx, cy, cz = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, (min(zs) + max(zs)) / 2
    rad = max(1e-3, math.sqrt((max(xs) - min(xs)) ** 2 + (max(ys) - min(ys)) ** 2 + (max(zs) - min(zs)) ** 2) / 2)
    ya, pa = math.radians(yaw), math.radians(pitch)
    cyw, syw, cp, sp = math.cos(ya), math.sin(ya), math.cos(pa), math.sin(pa)
    fov = math.radians(30)
    dist = rad / math.sin(fov / 2) * 1.05

    def view(p):
        x, y, z = p[0] - cx, p[1] - cy, p[2] - cz
        # turn the model by -yaw around Y (camera moves right), then tilt
        x, z = x * cyw - z * syw, x * syw + z * cyw
        y, z = y * cp - z * sp, y * sp + z * cp
        return (x, y, z - dist)                 # camera at origin looking -Z

    vv = [view(v) for v in verts]
    f = 1.0 / math.tan(fov / 2)
    proj = [(f * x / -z, f * y / -z, -z) for x, y, z in vv]
    # fit the projected model into 86% of the frame
    px = [p[0] for p in proj]
    py = [p[1] for p in proj]
    sx = (max(px) - min(px)) or 1e-3
    sy = (max(py) - min(py)) or 1e-3
    s = 0.86 * min(w / sx, h / sy)
    ox = w / 2 - s * (max(px) + min(px)) / 2
    oy = h / 2 + s * (max(py) + min(py)) / 2
    scr = [(ox + s * p[0], oy - s * p[1], p[2]) for p in proj]

    # background
    img = []
    for j in range(h):
        t = j / (h - 1)
        c = rgb565(*[BG_TOP[k] * (1 - t) + BG_BOTTOM[k] * t for k in range(3)])
        img.append([c] * w)
    zbuf = [[1e30] * w for _ in range(h)]
    L, F = _norm(LIGHT), _norm(FILL)
    # light in view space follows the model turn, so the shading stays the
    # same from every angle: transform the world-space normal instead
    for ia, ib, ic, col in tris:
        a, b, c = scr[ia], scr[ib], scr[ic]
        area = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
        back = area >= 0                         # screen y points down: CCW -> negative
        if back and not nocull:
            continue
        # world normal for lighting
        A, B, C = verts[ia], verts[ib], verts[ic]
        n = _norm((
            (B[1] - A[1]) * (C[2] - A[2]) - (B[2] - A[2]) * (C[1] - A[1]),
            (B[2] - A[2]) * (C[0] - A[0]) - (B[0] - A[0]) * (C[2] - A[2]),
            (B[0] - A[0]) * (C[1] - A[1]) - (B[1] - A[1]) * (C[0] - A[0])))
        if back:
            shade_col = rgb565(255, 0, 255)
        else:
            d = max(0.0, n[0] * L[0] + n[1] * L[1] + n[2] * L[2])
            d2 = max(0.0, n[0] * F[0] + n[1] * F[1] + n[2] * F[2])
            k = 0.42 + 0.58 * d + 0.18 * d2
            shade_col = rgb565(min(255, col[0] * k), min(255, col[1] * k), min(255, col[2] * k))
        if area == 0:
            continue
        x0 = max(0, int(math.floor(min(a[0], b[0], c[0]))))
        x1 = min(w - 1, int(math.ceil(max(a[0], b[0], c[0]))))
        y0 = max(0, int(math.floor(min(a[1], b[1], c[1]))))
        y1 = min(h - 1, int(math.ceil(max(a[1], b[1], c[1]))))
        inv = 1.0 / area
        for y in range(y0, y1 + 1):
            py_ = y + 0.5
            row, zrow = img[y], zbuf[y]
            for x in range(x0, x1 + 1):
                px_ = x + 0.5
                w0 = ((b[0] - px_) * (c[1] - py_) - (b[1] - py_) * (c[0] - px_)) * inv
                w1 = ((c[0] - px_) * (a[1] - py_) - (c[1] - py_) * (a[0] - px_)) * inv
                w2 = 1.0 - w0 - w1
                if w0 < -1e-9 or w1 < -1e-9 or w2 < -1e-9:
                    continue
                z = w0 * a[2] + w1 * b[2] + w2 * c[2]
                if z < zrow[x]:
                    zrow[x] = z
                    row[x] = shade_col
    return img


def write_png(path, img, scale=1):
    h, w = len(img), len(img[0])
    raw = bytearray()
    for row in img:
        line = bytearray()
        for c in row:
            line += bytes(c) * scale
        for _ in range(scale):
            raw.append(0)
            raw += line
    def chunk(t, d):
        return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    png = b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w * scale, h * scale, 8, 2, 0, 0, 0))
    png += chunk(b'IDAT', zlib.compress(bytes(raw), 9)) + chunk(b'IEND', b'')
    with open(path, 'wb') as f:
        f.write(png)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('obj')
    ap.add_argument('-o', '--out')
    ap.add_argument('--yaw', type=float, default=35)
    ap.add_argument('--pitch', type=float, default=22)
    ap.add_argument('--views')
    ap.add_argument('--nocull', action='store_true')
    ap.add_argument('--scale', type=int, default=2)
    a = ap.parse_args()
    verts, tris = load_obj(a.obj)
    if not tris:
        sys.exit('no triangles in ' + a.obj)
    views = [(a.yaw, a.pitch)]
    if a.views:
        views = [tuple(float(x) for x in v.split(',')) for v in a.views.split(';')]
    parts = [render(verts, tris, yw, pt, a.nocull) for yw, pt in views]
    img = [sum((p[j] for p in parts), []) for j in range(H)]
    out = a.out or os.path.splitext(a.obj)[0] + '.png'
    write_png(out, img, a.scale)
    print('%s: %d triangles -> %s' % (os.path.basename(a.obj), len(tris), out))


if __name__ == '__main__':
    main()

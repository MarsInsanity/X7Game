# SPDX-License-Identifier: GPL-3.0-or-later
"""
render.py - preview X7 Game models the way the frontend will show them:
320x240, 16-bit colour (RGB565), flat-shaded triangles, back faces culled,
perspective-correct depth and picture, then doubled to 640x480 for viewing
(nearest neighbour, like the console's hardware scaler). Pure Python.

One model:
    python tools/models/render.py MODEL.obj [-o OUT.png] [--yaw 35] [--pitch 22]
           [--views "35,22;-145,22"] [--nocull] [--image PIC.png] [--scale 2]
A console with its game going in (a system file, see scene.py):
    python tools/models/render.py --system assets/models/systems/psx.json
           [--frames "0,0.4,0.7,1"] [--cols 4] [--yaw .. --pitch ..] [--cut "x>0"]

--views   several angles side by side (yaw,pitch;yaw,pitch...)
--frames  moments of the insertion (0 = start, 1 = seated) side by side;
          the camera stays put over all of them (default: the system's view)
--nocull  draws back faces too, in magenta: any magenta in a normal render
          means a triangle is wound the wrong way (it would vanish)
--cut     cuts the scene open, e.g. "x>0" hides everything with world x > 0,
          to look inside a slot (inside faces show dark red)
--image   the picture for image areas (default: a test card: red top left,
          green top right, blue bottom left, yellow bottom right, a white
          arrow pointing up, so a wrongly turned picture is obvious)
The camera looks at the scene from the front-right-above (yaw 35 = turned
35 degrees to the right, pitch 22 = looking down).
"""
import argparse
import math
import os
import struct
import sys
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from x7model import load_model, rgb565  # noqa: E402

W, H = 320, 240
BG_TOP, BG_BOTTOM = (52, 58, 74), (22, 24, 32)
LIGHT = (-0.45, 0.80, 0.55)        # key light: up, left, towards the viewer
FILL = (0.6, 0.2, -0.4)            # weak fill from behind right


def _norm(a):
    l = math.sqrt(a[0] * a[0] + a[1] * a[1] + a[2] * a[2])
    return (a[0] / l, a[1] / l, a[2] / l) if l else (0, 0, 0)


def test_card(u, v):
    u -= math.floor(u)
    v -= math.floor(v)
    if u < 0.05 or u > 0.95 or v < 0.05 or v > 0.95:
        return (240, 240, 240)
    if 0.55 <= v <= 0.82 and abs(u - 0.5) < (0.82 - v) * 0.9:
        return (250, 250, 250)
    if 0.22 <= v < 0.55 and abs(u - 0.5) < 0.07:
        return (250, 250, 250)
    if v >= 0.5:
        return (220, 50, 50) if u < 0.5 else (50, 180, 70)
    return (50, 90, 220) if u < 0.5 else (240, 200, 40)


def read_png(path):
    """8-bit RGB or RGBA PNG -> rows of (r, g, b)."""
    data = open(path, 'rb').read()
    pos, idat, w, h, ct = 8, b'', 0, 0, 2
    while pos < len(data):
        n, = struct.unpack('>I', data[pos:pos + 4])
        t = data[pos + 4:pos + 8]
        d = data[pos + 8:pos + 8 + n]
        if t == b'IHDR':
            w, h = struct.unpack('>II', d[:8])
            if d[8] != 8 or d[9] not in (2, 6) or d[12] != 0:
                sys.exit('%s: only 8-bit RGB/RGBA non-interlaced PNG' % path)
            ct = d[9]
        elif t == b'IDAT':
            idat += d
        pos += 12 + n
    bpp = 3 if ct == 2 else 4
    raw = zlib.decompress(idat)
    stride = w * bpp
    img, prev = [], bytearray(stride)
    for y in range(h):
        f = raw[y * (stride + 1)]
        line = bytearray(raw[y * (stride + 1) + 1:(y + 1) * (stride + 1)])
        for i in range(stride):
            a = line[i - bpp] if i >= bpp else 0
            b = prev[i]
            c = prev[i - bpp] if i >= bpp else 0
            if f == 1:
                line[i] = (line[i] + a) & 255
            elif f == 2:
                line[i] = (line[i] + b) & 255
            elif f == 3:
                line[i] = (line[i] + (a + b) // 2) & 255
            elif f == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                line[i] = (line[i] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        img.append([tuple(line[x * bpp:x * bpp + 3]) for x in range(w)])
        prev = line
    return img


def image_sampler(img):
    h, w = len(img), len(img[0])

    def s(u, v):
        x = min(w - 1, max(0, int(u * w)))
        y = min(h - 1, max(0, int((1 - v) * h)))
        return img[y][x]
    return s


class Camera:
    def __init__(self, yaw, pitch, scenes, w=W, h=H):
        """Fits every vertex of `scenes` (lists of (x,y,z)) into 86% of the frame."""
        allv = [p for s in scenes for p in s]
        xs, ys, zs = [v[0] for v in allv], [v[1] for v in allv], [v[2] for v in allv]
        self.c = ((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, (min(zs) + max(zs)) / 2)
        rad = max(1e-3, math.sqrt((max(xs) - min(xs)) ** 2 + (max(ys) - min(ys)) ** 2 + (max(zs) - min(zs)) ** 2) / 2)
        ya, pa = math.radians(yaw), math.radians(pitch)
        self.cyw, self.syw, self.cp, self.sp = math.cos(ya), math.sin(ya), math.cos(pa), math.sin(pa)
        fov = math.radians(30)
        self.dist = rad / math.sin(fov / 2) * 1.05
        self.f = 1.0 / math.tan(fov / 2)
        self.w, self.h = w, h
        self.s, self.ox, self.oy = 1.0, 0.0, 0.0
        pr = [self._proj(p) for p in allv]
        px, py = [p[0] for p in pr], [p[1] for p in pr]
        sx, sy = (max(px) - min(px)) or 1e-3, (max(py) - min(py)) or 1e-3
        self.s = 0.86 * min(w / sx, h / sy)
        self.ox = w / 2 - self.s * (max(px) + min(px)) / 2
        self.oy = h / 2 + self.s * (max(py) + min(py)) / 2

    def _proj(self, p):
        x, y, z = p[0] - self.c[0], p[1] - self.c[1], p[2] - self.c[2]
        x, z = x * self.cyw - z * self.syw, x * self.syw + z * self.cyw
        y, z = y * self.cp - z * self.sp, y * self.sp + z * self.cp
        d = self.dist - z                      # distance in front of the camera
        return (self.f * x / d, self.f * y / d, d)

    def screen(self, p):
        x, y, d = self._proj(p)
        return (self.ox + self.s * x, self.oy - self.s * y, d)


def render(model, cam, nocull=False, cut=None, sampler=test_card):
    w, h = cam.w, cam.h
    verts, uvs, tris = model['verts'], model['uvs'], model['tris']
    scr = [cam.screen(v) for v in verts]
    img = []
    for j in range(h):
        t = j / (h - 1)
        c = rgb565(*[BG_TOP[k] * (1 - t) + BG_BOTTOM[k] * t for k in range(3)])
        img.append([c] * w)
    zbuf = [[0.0] * w for _ in range(h)]          # 1/distance, bigger = nearer
    L, F = _norm(LIGHT), _norm(FILL)
    cax = cop = cval = None
    if cut:
        cax, cop, cval = 'xyz'.index(cut[0]), cut[1], float(cut[2:])
    for ia, ib, ic, col, part, uv in tris:
        a, b, c = scr[ia], scr[ib], scr[ic]
        if a[2] <= 0 or b[2] <= 0 or c[2] <= 0:
            continue
        area = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
        if area == 0:
            continue
        back = area >= 0                         # screen y points down: CCW -> negative
        if back and not nocull and not cut:
            continue
        A, B, C = verts[ia], verts[ib], verts[ic]
        n = _norm((
            (B[1] - A[1]) * (C[2] - A[2]) - (B[2] - A[2]) * (C[1] - A[1]),
            (B[2] - A[2]) * (C[0] - A[0]) - (B[0] - A[0]) * (C[2] - A[2]),
            (B[0] - A[0]) * (C[1] - A[1]) - (B[1] - A[1]) * (C[0] - A[0])))
        d = max(0.0, n[0] * L[0] + n[1] * L[1] + n[2] * L[2])
        d2 = max(0.0, n[0] * F[0] + n[1] * F[1] + n[2] * F[2])
        k = 0.42 + 0.58 * d + 0.18 * d2
        flat = None
        if back:
            flat = rgb565(255, 0, 255) if nocull else rgb565(110, 30, 30)
        elif uv is None:
            flat = rgb565(min(255, col[0] * k), min(255, col[1] * k), min(255, col[2] * k))
        iw = (1.0 / a[2], 1.0 / b[2], 1.0 / c[2])
        if uv is not None and flat is None:
            ta, tb, tc = uvs[uv[0]], uvs[uv[1]], uvs[uv[2]]
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
                q = w0 * iw[0] + w1 * iw[1] + w2 * iw[2]
                if q <= zrow[x]:
                    continue
                if cut or flat is None:
                    # perspective-correct weights
                    p0, p1, p2 = w0 * iw[0] / q, w1 * iw[1] / q, w2 * iw[2] / q
                    if cut:
                        wc = p0 * A[cax] + p1 * B[cax] + p2 * C[cax]
                        if (wc > cval) if cop == '>' else (wc < cval):
                            continue
                    if flat is None:
                        u = p0 * ta[0] + p1 * tb[0] + p2 * tc[0]
                        v = p0 * ta[1] + p1 * tb[1] + p2 * tc[1]
                        t = sampler(u, v)
                        pix = rgb565(min(255, t[0] * k), min(255, t[1] * k), min(255, t[2] * k))
                    else:
                        pix = flat
                else:
                    pix = flat
                zrow[x] = q
                row[x] = pix
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


def tile(parts, cols):
    rows = [parts[i:i + cols] for i in range(0, len(parts), cols)]
    out = []
    blank = [[(16, 18, 24)] * W for _ in range(H)]
    for r in rows:
        r = r + [blank] * (cols - len(r)) if len(rows) > 1 else r
        out += [sum((p[j] for p in r), []) for j in range(H)]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('obj', nargs='?')
    ap.add_argument('-o', '--out')
    ap.add_argument('--system')
    ap.add_argument('--frames')
    ap.add_argument('--cols', type=int)
    ap.add_argument('--yaw', type=float)
    ap.add_argument('--pitch', type=float)
    ap.add_argument('--views')
    ap.add_argument('--nocull', action='store_true')
    ap.add_argument('--cut')
    ap.add_argument('--image')
    ap.add_argument('--scale', type=int, default=2)
    a = ap.parse_args()
    sampler = image_sampler(read_png(a.image)) if a.image else test_card
    if a.cut and (len(a.cut) < 3 or a.cut[0] not in 'xyz' or a.cut[1] not in '<>'):
        sys.exit('--cut looks like "x>0" or "z<-2.5"')
    parts = []
    if a.system:
        from scene import System
        sysm = System(a.system)
        times = [float(x) for x in (a.frames or '0,0.35,0.7,1').split(',')]
        yaw = a.yaw if a.yaw is not None else sysm.view[0]
        pitch = a.pitch if a.pitch is not None else sysm.view[1]
        scenes = [sysm.scene(t) for t in times]
        if a.views:
            vs = [tuple(float(x) for x in v.split(',')) for v in a.views.split(';')]
        else:
            vs = [(yaw, pitch)]
        for yw, pt in vs:
            cam = Camera(yw, pt, [s['verts'] for s in scenes])
            parts += [render(s, cam, a.nocull, a.cut, sampler) for s in scenes]
        out = a.out or os.path.splitext(a.system)[0] + '.png'
        label = '%s: %d frames' % (os.path.basename(a.system), len(times))
        cols = a.cols or len(times)
    else:
        if not a.obj:
            sys.exit('give a model .obj or --system file.json')
        m = load_model(a.obj)
        if not m['tris']:
            sys.exit('no triangles in ' + a.obj)
        views = [(a.yaw if a.yaw is not None else 35, a.pitch if a.pitch is not None else 22)]
        if a.views:
            views = [tuple(float(x) for x in v.split(',')) for v in a.views.split(';')]
        for yw, pt in views:
            parts.append(render(m, Camera(yw, pt, [m['verts']]), a.nocull, a.cut, sampler))
        out = a.out or os.path.splitext(a.obj)[0] + '.png'
        label = '%s: %d triangles' % (os.path.basename(a.obj), len(m['tris']))
        cols = a.cols or len(parts)
    write_png(out, tile(parts, cols), a.scale)
    print('%s -> %s' % (label, out))


if __name__ == '__main__':
    main()

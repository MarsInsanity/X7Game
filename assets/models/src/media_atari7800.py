# SPDX-License-Identifier: GPL-3.0-or-later
"""Atari 7800 cartridge: black, 2600-sized shell (8.1 x 8.7 x 1.9 cm) standing
upright, label to +Z, connector edge at y = 0. Signature details: the sloped
top-front bevel with an end label, the big framed front label with the
console's red / orange stripes, grip ribs on the upper sides and the ribbed
lower front and back."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model

SHELL = (36, 36, 40)        # black plastic, front / back
SIDE = (60, 60, 66)         # side walls, top
RIB = (92, 92, 100)         # grip ribs
SLOT = (12, 12, 14)         # connector opening
SILVER = (188, 192, 200)    # label frame / end label
BAND = (18, 18, 20)         # black title band
RED = (208, 40, 32)
ORANGE = (240, 148, 32)
BLUE = (56, 100, 208)       # picture area
GREEN = (48, 150, 72)       # picture ground
YELLOW = (240, 208, 64)     # picture accent

W, H = 8.1, 8.7
hw = W / 2
ZF, ZB = 0.95, -0.95        # front / back
YB = 7.55                   # where the top-front bevel starts
ZT = 0.30                   # front edge of the flat top
lx, ly0, ly1 = 3.4, 1.75, 7.25    # label on the front
ZL = ZF + 0.07              # label surface

m = Model('atari7800', 'media')
polys = []                  # (points, colour, normal): T-junctions fixed at the end


def rect_xy(x0, y0, x1, y1, z, color, nz=1):
    polys.append(([(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)], color, (0, 0, nz)))


# ---------------------------------------------------------------- shell
# side walls (profile in z, y)
prof = [(ZB, 0), (ZF, 0), (ZF, YB), (ZT, H), (ZB, H)]
polys.append(([(hw, y, z) for z, y in prof], SIDE, (1, 0, 0)))
polys.append(([(-hw, y, z) for z, y in prof], SIDE, (-1, 0, 0)))
# back, top, bottom
rect_xy(-hw, 0, hw, H, ZB, SHELL, -1)
polys.append(([(-hw, H, ZB), (hw, H, ZB), (hw, H, ZT), (-hw, H, ZT)], SIDE, (0, 1, 0)))
sx = 3.0
for x0, x1, c in ((-hw, -sx, SHELL), (-sx, sx, SLOT), (sx, hw, SHELL)):
    polys.append(([(x0, 0, ZB), (x1, 0, ZB), (x1, 0, ZF), (x0, 0, ZF)], c, (0, -1, 0)))
# front, tiled around the label
rect_xy(-hw, 0, hw, ly0, ZF, SHELL)
rect_xy(-hw, ly1, hw, YB, ZF, SHELL)
rect_xy(-hw, ly0, -lx, ly1, ZF, SHELL)
rect_xy(lx, ly0, hw, ly1, ZF, SHELL)
# bevel with the end label (silver with a red / orange stripe)
bn = (0, ZF - ZT, H - YB)   # bevel normal, pointing up and forward


def bevel(x0, t0, x1, t1, color):
    def p(x, t):
        return (x, YB + (H - YB) * t, ZF + (ZT - ZF) * t)
    polys.append(([p(x0, t0), p(x1, t0), p(x1, t1), p(x0, t1)], color, bn))


ex = lx
bevel(-hw, 0, -ex, 1, SHELL)
bevel(ex, 0, hw, 1, SHELL)
bevel(-ex, 0.0, ex, 0.12, SHELL)
bevel(-ex, 0.12, ex, 0.45, SILVER)
bevel(-ex, 0.45, ex, 0.60, RED)
bevel(-ex, 0.60, ex, 0.88, SILVER)
bevel(-ex, 0.88, ex, 1.0, SHELL)

# ---------------------------------------------------------------- label
# raised slab sides
lab = [(-lx, ly0), (lx, ly0), (lx, ly1), (-lx, ly1)]
m.extrude_xy(lab, ZF, ZL, SILVER, front=False, back=False, side=SIDE)
ax = lx - 0.3
sx0, sx1 = 1.4, 2.3
rows = [
    (ly0, 2.05, [(-lx, lx, SILVER)]),
    (2.05, 2.85, [(-lx, -ax, SILVER), (-ax, ax, GREEN), (ax, lx, SILVER)]),
    (2.85, 4.45, [(-lx, -ax, SILVER), (-ax, ax, BLUE), (ax, lx, SILVER)]),
    (4.45, 5.25, [(-lx, -ax, SILVER), (-ax, sx0, BLUE), (sx0, sx1, YELLOW), (sx1, ax, BLUE), (ax, lx, SILVER)]),
    (5.25, 5.55, [(-lx, -ax, SILVER), (-ax, ax, BLUE), (ax, lx, SILVER)]),
    (5.55, 5.85, [(-lx, lx, SILVER)]),
    (5.85, 6.15, [(-lx, -ax, SILVER), (-ax, ax, BAND), (ax, lx, SILVER)]),
    (6.15, 6.35, [(-lx, -ax, SILVER), (-ax, ax, ORANGE), (ax, lx, SILVER)]),
    (6.35, 6.55, [(-lx, -ax, SILVER), (-ax, ax, RED), (ax, lx, SILVER)]),
    (6.55, 6.95, [(-lx, -ax, SILVER), (-ax, ax, BAND), (ax, lx, SILVER)]),
    (6.95, ly1, [(-lx, lx, SILVER)]),
]
for y0, y1, cells in rows:
    for x0, x1, c in cells:
        rect_xy(x0, y0, x1, y1, ZL, c)

# ---------------------------------------------------------------- emit panels
# insert every panel corner that lies on another panel's edge, so the
# software renderer shows no hairline cracks at T-junctions
allpts = {p for pts, _, _ in polys for p in pts}


def on_seg(p, a, b):
    ab = (b[0] - a[0], b[1] - a[1], b[2] - a[2])
    ap = (p[0] - a[0], p[1] - a[1], p[2] - a[2])
    l2 = ab[0] ** 2 + ab[1] ** 2 + ab[2] ** 2
    t = (ap[0] * ab[0] + ap[1] * ab[1] + ap[2] * ab[2]) / l2
    if t <= 1e-6 or t >= 1 - 1e-6:
        return None
    d = [ap[i] - ab[i] * t for i in range(3)]
    return t if d[0] ** 2 + d[1] ** 2 + d[2] ** 2 < 1e-8 else None


for pts, c, n in polys:
    out = []
    for i, a in enumerate(pts):
        b = pts[(i + 1) % len(pts)]
        out.append(a)
        mids = []
        for p in allpts:
            t = on_seg(p, a, b)
            if t is not None:
                mids.append((t, p))
        out += [p for _, p in sorted(mids)]
    m.polygon(out, c, normal=n)

# ---------------------------------------------------------------- ribs
# grip ribs across the upper sides
for i in range(3):
    y = 4.9 + i * 0.75
    for s in (-1, 1):
        x0, x1 = (hw, hw + 0.12) if s > 0 else (-hw - 0.12, -hw)
        f = {'bottom': None, ('left' if s > 0 else 'right'): None}
        m.box(x0, y, -0.7, x1, y + 0.28, 0.7, RIB, faces=f)
# ribbed lower front, under the label
for i in range(3):
    y = 0.35 + i * 0.42
    m.box(-lx, y, ZF, lx, y + 0.2, ZF + 0.1, SIDE, faces={'back': None, 'bottom': None})
    m.box(-lx, y, ZB - 0.1, lx, y + 0.2, ZB, SIDE, faces={'front': None, 'bottom': None})

print(m.stats())
print(m.save())

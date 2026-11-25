# SPDX-License-Identifier: GPL-3.0-or-later
"""Atari Lynx (first model, 1989): a long, flat, dark charcoal handheld,
27.3 x 11.1 x 4.35 cm, standing upright with the screen to +Z.

Measured from Commons photos (Atari-Lynx-Flat-Front, -Front-Top,
-Front-Bottom, -Back-Top, -Back-Botton, -Casing-Bottom), x from the centre,
y from the table:
  * silhouette: a long rounded slab; the grips are the full height (11.1)
    and reach the table, the middle section is a little lower at the top
    (10.64) and lifted off the table (0.58); big rounded ends
  * front: a raised middle panel (x -7.0 .. 8.2, slightly off centre: the
    left grip is wider); on it a square raised plate (x -5.2 .. 6.5) with
    the black screen bezel (x -3.6 .. 4.75, y 2.2 .. 9.3) and the LCD;
    ON / OFF buttons left of the screen, the three Option / Pause buttons
    right of it
  * left grip: the D-pad in a round raised well (centre -8.8, 5.75, r 2.2)
  * right grip: two pairs of round A / B buttons (top and bottom, so the
    console can be turned over for left-handers) with the speaker grille
    between them
  * back: thick rounded humps behind both grips (to z -2.9), a flat middle
    with the battery cover and stickers; the game card slot is a slit in
    the inner wall of the LEFT hump (behind the D-pad), facing the middle:
    the card lies flat against the back, label outwards, and slides
    sideways (towards the left end) until only its curled lip shows
  * top edge: volume wheel, headphone, ComLynx and power sockets
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model  # noqa: E402

BODY = (64, 64, 70)          # charcoal shell
PANEL = (70, 70, 76)         # raised middle panel
PLATE = (78, 78, 84)         # square screen plate
BEZEL = (14, 14, 16)         # black screen surround
LCD = (60, 74, 72)           # the (off) LCD
RIM = (46, 46, 50)           # D-pad well
DPAD = (24, 24, 26)          # D-pad, buttons
BUTTON = (30, 30, 33)
GRILLE = (16, 16, 18)        # speaker holes, sockets
SLOT = (10, 10, 12)          # inside the card slot
STICKER = (112, 112, 118)    # silver stickers on the back
COVER = (54, 54, 60)         # battery cover

ZF = 1.1        # front face of the grips
ZP = 1.3        # front of the raised middle panel
ZS = 1.45       # front of the screen plate
ZB = -1.6       # back face (middle)
ZH = -2.5       # humps: straight sides to here ...
ZHB = -2.9      # ... then chamfered to the back

# card slot (left hump, inner wall facing +X)
SLOT_X = -9.0                      # the hump's inner wall
SLOT_Y0, SLOT_Y1 = 2.6, 8.2        # card 5.4 wide (centre y 5.4) + 0.1 each side
SLOT_Z0, SLOT_Z1 = -2.42, -1.90    # card 0.32 thick (centre z -2.15) + 0.1 each side
SLOT_END = -12.95                  # card reaches -12.75 (3.75 deep)

# half silhouette (x >= 0), from the top centre round the right end to the bottom centre
HALF = [(5.5, 10.64), (10.5, 11.08), (12.3, 10.5), (13.2, 8.6), (13.65, 5.5),
        (13.2, 2.4), (12.3, 0.8), (10.5, 0.0), (5.5, 0.58)]


def silhouette():
    right = HALF                                         # clockwise on the right side
    left = [(-x, y) for x, y in reversed(HALF)]          # bottom centre round the left end to the top
    return right + left


def y_on(pts, x, top):
    """y of the silhouette edge (top or bottom) at x."""
    best = None
    n = len(pts)
    for i in range(n):
        (xa, ya), (xb, yb) = pts[i], pts[(i + 1) % n]
        if xa == xb or not (min(xa, xb) <= x <= max(xa, xb)):
            continue
        y = ya + (yb - ya) * (x - xa) / (xb - xa)
        if best is None or (top and y > best) or (not top and y < best):
            best = y
    return best


def offset(poly, d):
    """Inset a counter-clockwise 2D polygon by d."""
    n = len(poly)
    out = []
    for i in range(n):
        p0, p1, p2 = poly[i - 1], poly[i], poly[(i + 1) % n]

        def nrm(a, b):
            ex, ey = b[0] - a[0], b[1] - a[1]
            l = math.hypot(ex, ey)
            return (-ey / l, ex / l)               # left normal = inwards for CCW
        n0, n1 = nrm(p0, p1), nrm(p1, p2)
        bx, by = n0[0] + n1[0], n0[1] + n1[1]
        bl = math.hypot(bx, by)
        bx, by = bx / bl, by / bl
        k = d / max(0.3, bx * n1[0] + by * n1[1])
        out.append((p1[0] + bx * k, p1[1] + by * k))
    return out


def ccw(poly):
    s = sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1]
            for i in range(len(poly)))
    return poly if s > 0 else list(reversed(poly))


def hump(m, sil, side, slot=False):
    """The thick rounded hump behind a grip: straight sides from the back
    face ZB to ZH, then a chamfer to the back ZHB. side = -1 left, +1 right.
    Its inner wall is the straight edge at x = wall."""
    wall = SLOT_X if side < 0 else 9.25
    pts = [p for p in sil if p[0] * side > abs(wall) + 0.3 and abs(p[0]) < 13.6]   # end point dropped: budget
    yb = y_on(sil, wall, False) + 0.1
    yt = y_on(sil, wall, True) - 0.1
    # pull the outer points in a little so the hump sits inside the shell edge
    cx, cy = side * 11.5, 5.5
    outer = [(x - 0.1 * (x - cx) / math.hypot(x - cx, y - cy), y - 0.1 * (y - cy) / math.hypot(x - cx, y - cy))
             for x, y in pts]
    outer = ccw([(wall, yt)] + outer + [(wall, yb)] if side > 0 else [(wall, yb)] + outer + [(wall, yt)])
    inner = offset(outer, 0.5)
    n = len(outer)
    wall_seg = None
    for i in range(n):
        a, b = outer[i], outer[(i + 1) % n]
        if abs(a[0] - wall) < 1e-6 and abs(b[0] - wall) < 1e-6:
            wall_seg = i
            continue
        # straight side (outward normal), CCW seen from outside
        m.quad((a[0], a[1], ZB), (a[0], a[1], ZH), (b[0], b[1], ZH), (b[0], b[1], ZB), BODY)
    for i in range(n):
        a, b = outer[i], outer[(i + 1) % n]
        ai, bi = inner[i], inner[(i + 1) % n]
        m.quad((a[0], a[1], ZH), (ai[0], ai[1], ZHB), (bi[0], bi[1], ZHB), (b[0], b[1], ZH), BODY)
    m.polygon([(x, y, ZHB) for x, y in inner], BODY, normal=(0, 0, -1))
    # the inner wall, facing the middle of the console
    a, b = outer[wall_seg], outer[(wall_seg + 1) % n]
    y0, y1 = min(a[1], b[1]), max(a[1], b[1])
    nx = (-side, 0, 0)
    if not slot:
        m.polygon([(wall, y0, ZB), (wall, y1, ZB), (wall, y1, ZH), (wall, y0, ZH)], BODY, normal=nx)
        return
    # a frame round the card slot
    W = wall

    def wq(ya, yb_, za, zb):
        m.polygon([(W, ya, za), (W, yb_, za), (W, yb_, zb), (W, ya, zb)], BODY, normal=nx)
    wq(y0, SLOT_Y0, ZH, ZB)
    wq(SLOT_Y1, y1, ZH, ZB)
    wq(SLOT_Y0, SLOT_Y1, ZH, SLOT_Z0)
    wq(SLOT_Y0, SLOT_Y1, SLOT_Z1, ZB)
    # the cavity: faces looking inwards, dark
    E = SLOT_END
    m.polygon([(E, SLOT_Y0, SLOT_Z0), (E, SLOT_Y1, SLOT_Z0), (E, SLOT_Y1, SLOT_Z1), (E, SLOT_Y0, SLOT_Z1)],
              SLOT, normal=(1, 0, 0))
    m.polygon([(E, SLOT_Y0, SLOT_Z0), (W, SLOT_Y0, SLOT_Z0), (W, SLOT_Y0, SLOT_Z1), (E, SLOT_Y0, SLOT_Z1)],
              SLOT, normal=(0, 1, 0))
    m.polygon([(E, SLOT_Y1, SLOT_Z0), (W, SLOT_Y1, SLOT_Z0), (W, SLOT_Y1, SLOT_Z1), (E, SLOT_Y1, SLOT_Z1)],
              SLOT, normal=(0, -1, 0))
    m.polygon([(E, SLOT_Y0, SLOT_Z0), (W, SLOT_Y0, SLOT_Z0), (W, SLOT_Y1, SLOT_Z0), (E, SLOT_Y1, SLOT_Z0)],
              SLOT, normal=(0, 0, 1))
    m.polygon([(E, SLOT_Y0, SLOT_Z1), (W, SLOT_Y0, SLOT_Z1), (W, SLOT_Y1, SLOT_Z1), (E, SLOT_Y1, SLOT_Z1)],
              SLOT, normal=(0, 0, -1))


def build():
    m = Model('lynx', 'console')
    sil = silhouette()

    # ---- the shell
    m.extrude_xy(sil, ZB, ZF, BODY)

    # ---- raised middle panel (follows the top and bottom edges)
    xl, xr = -7.0, 8.2
    panel = [(xl, y_on(sil, xl, False)), (-5.5, 0.58), (5.5, 0.58), (xr, y_on(sil, xr, False)),
             (xr, y_on(sil, xr, True)), (5.5, 10.64), (-5.5, 10.64), (xl, y_on(sil, xl, True))]
    m.extrude_xy(panel, ZF, ZP, PANEL, back=False)

    # ---- square screen plate, bezel, LCD
    m.box(-5.2, 1.1, ZP, 6.5, 10.0, ZS, PLATE, faces={'back': None})
    m.decal_xy([(-3.6, 2.2), (4.75, 2.2), (4.75, 9.3), (-3.6, 9.3)], ZS, BEZEL)
    m.decal_xy([(-3.15, 3.3), (4.3, 3.3), (4.3, 8.15), (-3.15, 8.15)], ZS, LCD, lift=0.04)

    # ON / OFF (left of the screen) and Option 1 / Pause / Option 2 (right)
    for y in (6.6, 5.0):
        m.box(-5.0, y - 0.26, ZS, -3.9, y + 0.26, ZS + 0.18, BUTTON, faces={'back': None})
    for y in (7.2, 5.75, 4.2):
        m.box(6.75, y - 0.24, ZP, 7.85, y + 0.24, ZP + 0.2, BUTTON, faces={'back': None})

    # ---- D-pad in its round well (left grip)
    cx, cy = -8.8, 5.75
    m.cylinder_z(cx, cy, 2.15, ZF, ZF + 0.12, RIM, segments=10, back=False, side=PANEL)
    a, b = 1.35, 0.42
    cross = [(b, -a), (b, -b), (a, -b), (a, b), (b, b), (b, a), (-b, a), (-b, b), (-a, b), (-a, -b), (-b, -b), (-b, -a)]
    m.extrude_xy([(cx + x, cy + y) for x, y in cross], ZF + 0.12, ZF + 0.4, BEZEL, back=False, side=DPAD)

    # ---- A / B buttons (two pairs, right grip) and the speaker grille
    for bx, by in ((9.65, 9.2), (11.5, 9.4), (9.65, 2.2), (11.5, 2.0)):
        m.cylinder_z(bx, by, 0.78, ZF, ZF + 0.3, BUTTON, segments=8, back=False, side=DPAD)
    for i in range(4):
        for j in range(5):
            x = 9.6 + i * 0.85
            y = 3.65 + j * 0.95
            m.decal_xy([(x - 0.2, y - 0.2), (x + 0.2, y - 0.2), (x + 0.2, y + 0.2), (x - 0.2, y + 0.2)],
                       ZF, GRILLE)

    # ---- humps behind the grips; the card slot in the left one
    hump(m, sil, -1, slot=True)
    hump(m, sil, +1)

    # ---- back: battery cover, the Atari sticker, the card pictogram sticker
    def back_decal(x0, y0, x1, y1, col):
        m.polygon([(x1, y0, ZB - 0.02), (x0, y0, ZB - 0.02), (x0, y1, ZB - 0.02), (x1, y1, ZB - 0.02)],
                  col, normal=(0, 0, -1))
    back_decal(-5.1, 1.3, 0.9, 9.6, COVER)
    back_decal(1.8, 4.6, 8.6, 9.1, STICKER)
    back_decal(-8.7, 4.3, -5.9, 8.6, STICKER)

    # ---- top edge: volume wheel, headphones, ComLynx, power
    yt = 10.64 + 0.02
    for x, w, d, col in ((-6.4, 0.9, 0.6, DPAD), (-3.6, 0.45, 0.45, GRILLE), (-1.15, 0.45, 0.45, GRILLE),
                         (0.7, 0.5, 0.5, GRILLE)):
        m.decal_xz([(x - w / 2, -0.4 + d / 2), (x + w / 2, -0.4 + d / 2), (x + w / 2, -0.4 - d / 2),
                    (x - w / 2, -0.4 - d / 2)], 10.64, col)
    _ = yt
    return m


if __name__ == '__main__':
    m = build()
    print(m.stats())
    print(m.save())

# SPDX-License-Identifier: GPL-3.0-or-later
"""Low-poly Nintendo Game Boy Color ("Atomic Purple") for the X7 Game frontend.

Real size 7.5 wide x 13.3 tall x 2.74 deep (cm). Portrait handheld standing
upright on its bottom edge, screen facing +Z, origin at the bottom centre.

Measured from Wikimedia Commons photos (front, front three-quarter, back
three-quarter, back with a cartridge in):
  * big dark lens over the top 43 %: 6.25 wide, 0.5 below the top, its
    bottom edge 7.1 above the bottom; the screen inside it sits in the
    upper part (4.1 x 3.7), a wide plain strip below it, the power lamp
    to the left of the screen
  * D-pad in a round well on the left (centre 2.2 cm left of the middle,
    5.1 up), B and A on a rising diagonal on the right, Select / Start as
    two small pills low in the middle, round speaker in the bottom-right
    corner; flat top, big rounded bottom corners
  * back: the cartridge bay at the top is open to the back (the inserted
    game's label shows) down to 2.7 cm below the top; there a raised
    back plate starts that covers the rest of the cartridge and holds the
    battery cover (two AA, lower back) and the grey model sticker
  * top: power switch on the left, infrared window left of the middle

Depth layers (z): front face +1.37 .. cartridge-bay floor +0.01 (the front
half: screen, buttons) .. main back -0.96 (the bay is 0.97 deep, for a
0.80 cartridge) .. raised back plate -1.37.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model  # noqa: E402

BODY = (178, 160, 208)      # atomic purple, the see-through shell read as a flat colour
BODY_MID = (150, 130, 190)  # battery cover, A/B and Select/Start wells
BODY_DARK = (100, 76, 140)  # D-pad well, A/B well, speaker ring
LENS = (46, 46, 54)         # dark screen lens
SCREEN = (176, 186, 172)    # unlit LCD
BUTTON = (40, 40, 48)       # D-pad, A, B, Select, Start, power switch
LED = (220, 40, 50)         # power lamp
CAVITY = (22, 18, 30)       # inside the cartridge bay, speaker holes, ports
STICKER = (150, 152, 164)   # silver-grey model sticker on the back

W2 = 3.75        # half width
H = 13.3         # height
SAG = 0.2        # the bottom edge bows down this much in the middle
RT = 0.45        # top corner radius
RB = 1.3         # bottom corner radius
BEV = 0.14       # front edge bevel

ZF = 1.37        # front face
ZM = 0.01        # cartridge bay floor (back of the front half)
ZB = -0.96       # main back face
ZP = -1.37       # raised back plate

# the cartridge bay: open at the top, and at the back above PLATE_TOP
SX = 2.98        # half width (cartridge 2.85, its grip ribs 2.89)
SLOT_BOTTOM = 8.25
PLATE_TOP = 10.6
PLATE_IN = 0.35  # the back plate is inset this much from the sides


def outline(d):
    """Front silhouette inset by d, counter-clockwise seen from +Z: flat top
    with small rounded corners, big rounded bottom corners, the bottom edge
    bowing down slightly in the middle."""
    w, top = W2 - d, H - d
    rt, rb = RT - d * 0.5, RB - d * 0.5
    pts = [(0.0, d)]                                   # bottom middle
    cy = SAG + d + rb
    for a in (-90, -60, -30, 0):                       # bottom-right corner
        r = math.radians(a)
        pts.append((w - rb + rb * math.cos(r), cy + rb * math.sin(r)))
    for a in (0, 45, 90):                              # top-right corner
        r = math.radians(a)
        pts.append((w - rt + rt * math.cos(r), top - rt + rt * math.sin(r)))
    for a in (90, 135, 180):                           # top-left corner
        r = math.radians(a)
        pts.append((-w + rt + rt * math.cos(r), top - rt + rt * math.sin(r)))
    for a in (180, 210, 240, 270):                     # bottom-left corner
        r = math.radians(a)
        pts.append((-w + rb + rb * math.cos(r), cy + rb * math.sin(r)))
    return pts


def loft(m, outer, zo, inner, zi, color):
    """Bevel ring facing +Z between `outer` at depth zo and `inner` at zi."""
    n = len(outer)
    for i in range(n):
        j = (i + 1) % n
        m.quad((outer[i][0], outer[i][1], zo), (outer[j][0], outer[j][1], zo),
               (inner[j][0], inner[j][1], zi), (inner[i][0], inner[i][1], zi), color)


def side_quad(m, a, b, z0, z1, color):
    """Wall along the 2D edge a -> b (polygon counter-clockwise from +Z),
    from z0 (back) to z1 (front), facing outwards."""
    m.quad((a[0], a[1], z1), (a[0], a[1], z0), (b[0], b[1], z0), (b[0], b[1], z1), color)


def rot2(pts, deg, cx, cy):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return [(cx + x * c - y * s, cy + x * s + y * c) for x, y in pts]


def circle(cx, cy, r, n):
    return [(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


def build():
    m = Model('gbc', 'console')
    out0 = outline(0.0)
    out1 = outline(BEV)

    # ---- front half (ZM .. ZF): straight sides, bevelled front edge
    n = len(out0)
    for i in range(n):
        side_quad(m, out0[i], out0[(i + 1) % n], ZM, ZF - BEV, BODY)
    loft(m, out0, ZF - BEV, out1, ZF, BODY)
    m.polygon([(x, y, ZF) for x, y in out1], BODY, normal=(0, 0, 1))
    # its back face is the floor of the cartridge bay (only seen in there)
    m.polygon([(x, y, ZM) for x, y in out0], CAVITY, normal=(0, 0, -1))

    # ---- back half (ZB .. ZM): the outline with the cartridge bay cut out
    # of the top. out0 runs: bottom middle, bottom-right corner (1..4),
    # top-right corner (5..7), top-left corner (8..10), bottom-left (11..14)
    back = out0[:8] + [(SX, H), (SX, SLOT_BOTTOM), (-SX, SLOT_BOTTOM), (-SX, H)] + out0[8:]
    m.polygon([(x, y, ZB) for x, y in back], BODY, normal=(0, 0, -1))
    nb = len(back)
    for i in range(nb):
        a, b = back[i], back[(i + 1) % nb]
        if i == 8:                 # right bay wall: shell colour above the back plate, dark below
            side_quad(m, a, (SX, PLATE_TOP), ZB, ZM, BODY)
            side_quad(m, (SX, PLATE_TOP), b, ZB, ZM, CAVITY)
        elif i == 9:               # bay bottom
            side_quad(m, a, b, ZB, ZM, CAVITY)
        elif i == 10:              # left bay wall
            side_quad(m, a, (-SX, PLATE_TOP), ZB, ZM, CAVITY)
            side_quad(m, (-SX, PLATE_TOP), b, ZB, ZM, BODY)
        else:
            side_quad(m, a, b, ZB, ZM, BODY)

    # ---- raised back plate (ZP .. ZB) over the lower bay and the batteries
    inset = outline(PLATE_IN)
    # inset runs: bottom middle, bottom-right corner (1..4), ..., bottom-left corner (11..14)
    right = inset[:5]
    left = inset[11:]
    plate = right + [(W2 - PLATE_IN, PLATE_TOP), (-(W2 - PLATE_IN), PLATE_TOP)] + left
    m.polygon([(x, y, ZP) for x, y in plate], BODY, normal=(0, 0, -1))
    npl = len(plate)
    for i in range(npl):
        side_quad(m, plate[i], plate[(i + 1) % npl], ZP, ZB, BODY)
    # its front face closes the bay from behind (dark, inside)
    m.polygon([(-SX, SLOT_BOTTOM, ZB), (SX, SLOT_BOTTOM, ZB), (SX, PLATE_TOP, ZB), (-SX, PLATE_TOP, ZB)],
              CAVITY, normal=(0, 0, 1))

    # battery cover (two AA, lower back) with its catch, grey sticker above
    bat = Model.rounded_rect(-2.75, 1.3, 2.75, 6.1, 0.35, segments=1)
    m.polygon([(x, y, ZP - 0.02) for x, y in bat], BODY_MID, normal=(0, 0, -1))
    m.polygon([(-0.5, 1.45, ZP - 0.04), (0.5, 1.45, ZP - 0.04), (0.5, 1.85, ZP - 0.04), (-0.5, 1.85, ZP - 0.04)],
              BODY_DARK, normal=(0, 0, -1))
    m.polygon([(-2.55, 6.6, ZP - 0.02), (2.55, 6.6, ZP - 0.02), (2.55, 9.5, ZP - 0.02), (-2.55, 9.5, ZP - 0.02)],
              STICKER, normal=(0, 0, -1))

    # ---- front: lens, screen, power lamp
    lens = Model.rounded_rect(-3.12, 7.1, 3.12, 12.8, 0.4, segments=2)
    m.decal_xy(lens, ZF, LENS, lift=0.02)
    m.decal_xy([(-2.05, 8.45), (2.05, 8.45), (2.05, 12.15), (-2.05, 12.15)], ZF, SCREEN, lift=0.04)
    m.decal_xy(circle(-2.6, 11.2, 0.11, 6), ZF, LED, lift=0.04)

    # ---- D-pad in its round well
    m.decal_xy(circle(-2.2, 5.1, 1.12, 12), ZF, BODY_DARK, lift=0.02)
    a, b = 0.29, 0.86
    cross = [(a, -b), (a, -a), (b, -a), (b, a), (a, a), (a, b),
             (-a, b), (-a, a), (-b, a), (-b, -a), (-a, -a), (-a, -b)]
    m.extrude_xy([(x - 2.2, y + 5.1) for x, y in cross], ZF, ZF + 0.28, BUTTON, back=False)

    # ---- B and A on a rising diagonal, in one slanted well
    bx, by, ax, ay = 1.17, 4.85, 2.66, 5.36
    ang = math.degrees(math.atan2(ay - by, ax - bx))
    half = math.hypot(ax - bx, ay - by) / 2
    well = Model.rounded_rect(-half - 0.62, -0.62, half + 0.62, 0.62, 0.6, segments=2)
    m.decal_xy(rot2(well, ang, (ax + bx) / 2, (ay + by) / 2), ZF, BODY_MID, lift=0.02)
    for cx, cy in ((bx, by), (ax, ay)):
        m.cylinder_z(cx, cy, 0.45, ZF, ZF + 0.25, BUTTON, segments=8, back=False)

    # ---- Select / Start: small dark pills in a shared well
    m.decal_xy(Model.rounded_rect(-1.15, 2.33, 1.31, 2.93, 0.28, segments=1), ZF, BODY_MID, lift=0.02)
    pill = Model.rounded_rect(-0.45, -0.13, 0.45, 0.13, 0.12, segments=1)
    for cx in (-0.47, 0.63):
        m.extrude_xy([(x + cx, y + 2.63) for x, y in pill], ZF, ZF + 0.12, BUTTON, back=False)

    # ---- speaker grille in the bottom-right corner
    sc = (2.4, 1.68)
    m.decal_xy(circle(sc[0], sc[1], 0.92, 10), ZF, BODY_DARK, lift=0.02)
    sq = [(-0.11, -0.11), (0.11, -0.11), (0.11, 0.11), (-0.11, 0.11)]
    for hx, hy in [(0, 0)] + [(0.5 * math.cos(math.radians(t)), 0.5 * math.sin(math.radians(t)))
                             for t in range(0, 360, 60)]:
        m.decal_xy([(sc[0] + hx + x, sc[1] + hy + y) for x, y in sq], ZF, CAVITY, lift=0.04)

    # ---- top: power switch (left), infrared window
    m.box(-3.05, H, 0.25, -2.4, H + 0.14, 0.85, BUTTON, faces={'bottom': None})
    m.decal_xz([(-1.95, 0.2), (-0.75, 0.2), (-0.75, 0.95), (-1.95, 0.95)], H, CAVITY, lift=0.02)

    # ---- left side: power jack and volume wheel; right side: link port
    def side_decal(x, nx, y0, y1, z0, z1, color):
        q = [(x, y0, z0), (x, y0, z1), (x, y1, z1), (x, y1, z0)]
        m.polygon(q, color, normal=(nx, 0, 0))
    side_decal(-W2 - 0.02, -1, 9.0, 10.0, -0.35, 0.45, CAVITY)
    m.box(-W2 - 0.12, 7.4, -0.2, -W2, 8.6, 0.3, BUTTON, faces={'right': None})
    side_decal(W2 + 0.02, 1, 9.3, 10.7, -0.5, 0.5, CAVITY)
    return m


if __name__ == '__main__':
    model = build()
    print(model.stats())
    print(model.save())

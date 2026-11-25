# SPDX-License-Identifier: GPL-3.0-or-later
"""Sega CD / Mega-CD model 1 (the front-loading unit that sits under a
Genesis / Mega Drive): low-poly console model, modelled on its own.

Measured from photos (Wikimedia Commons: Sega-CD-Model1-Set.jpg,
Sega-Genesis-CD-Model-1-Bare.jpg) and the published size (about
30 x 12.4 x 21.5 cm with the side tower):
  * a low, wide, matt black box (28 x 7 cm body) on a recessed ribbed
    plinth with four broad feet; flat top where the console sits, with the
    small locating holes and an oval centre mark
  * the tall side TOWER on the right (2.5 cm wide, up to 12.4 cm, set back 1.5 cm
    from the front) that reaches up to the console's expansion port
  * front: the motorised CD tray on the left half (a glossy black panel,
    x 9 % .. 52 % of the width, with the plain silver outline box where the
    badge sits), the dark indicator panel to its right with two grey
    light windows (upper left, lower right), a stepped top lip
  * back: power / audio ports
Moving part: "tray" (slides 14.5 cm forward along +Z; the disc lies label
side up in its round recess).
"""
import math
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model

BODY = (54, 54, 57)        # matt black plastic (lifted so it shades)
LIP = (68, 68, 71)         # the top lip / seat, a touch lighter
DARK = (14, 14, 16)        # gaps, slot cavity, holes, grooves
PANEL = (30, 30, 32)       # indicator panel and plinth
TRAYF = (36, 36, 39)       # glossy tray face
BADGE = (168, 170, 178)    # silver outline box on the tray (no text)
WINDOW = (150, 152, 160)   # grey light windows
TRAYTOP = (84, 84, 88)     # tray deck (seen when open)
RECESS = (40, 40, 44)      # disc recess floor
FOOT = (22, 22, 24)
PORT = (120, 120, 130)
INSET = (42, 42, 45)       # shallow inset panel on the tower

# ------------------------------------------------------------ dimensions
XL, XR = -15.25, 12.75     # main body (the tower is x 12.75 .. 15.25)
ZB, ZF = -10.7, 10.7       # back, front
Y0, Y1, Y2 = 1.0, 5.9, 7.0 # body bottom, step to the top lip, top
RC = 1.2                   # rounded front corners (plan)

# tray opening / tunnel in the front
OX0, OX1, OY0, OY1 = -13.7, 0.3, 2.05, 5.15
OZB = ZF - 15.4            # back of the tunnel
# the tray (closed)
TX0, TX1 = -13.5, 0.1
TY0, TFY1, TDY = 2.25, 4.95, 3.0     # bottom, face top, deck top
TZF, TZFB, TZB = ZF + 0.15, ZF - 0.7, ZF - 15.2
RX, RZ = -6.7, ZF - 7.2              # recess centre
RR = 6.05 / math.cos(math.pi / 16)  # 16-gon, flats at 6.05 cm (disc r 6.0)
RY = 2.7                             # recess floor
SLIDE = 14.5

m = Model('segacd', 'console')


def plan_outline(zf):
    """Body outline in plan (x, z), front corners rounded, CCW from above."""
    pts = [(XL, ZB), (XR, ZB)]
    for cx, a0 in ((XR - RC, 0), (XL + RC, 90)):
        for s in range(3):
            a = math.radians(a0 + 45 * s)
            pts.append((cx + RC * math.cos(a), zf - RC + RC * math.sin(a)))
    return pts   # (XR, ZB) ... front right arc ... front left arc, back to (XL, ZB)


def slab(zf, y0, y1, color, top=None, skip_front=False, bottom=True):
    pts = plan_outline(zf)
    # make it CCW seen from above: x right, -z up
    m.polygon([(x, y1, z) for x, z in pts], top or color, normal=(0, 1, 0))
    if bottom:
        m.polygon([(x, y0, z) for x, z in pts], color, normal=(0, -1, 0))
    n = len(pts)
    for i in range(n):
        (xa, za), (xb, zb) = pts[i], pts[(i + 1) % n]
        if skip_front and abs(za - zf) < 1e-6 and abs(zb - zf) < 1e-6:
            continue
        nx, nz = zb - za, -(xb - xa)          # outward normal of the edge
        q = [(xa, y0, za), (xb, y0, zb), (xb, y1, zb), (xa, y1, za)]
        m.polygon(q, color, normal=(nx, 0, nz))


def front_rect(x0, y0, x1, y1, z, color, lift=0.0):
    zz = z + lift
    return m.polygon([(x0, y0, zz), (x1, y0, zz), (x1, y1, zz), (x0, y1, zz)], color, normal=(0, 0, 1))


# ---------------------------------------------------------------- body
slab(ZF, Y0, Y1, BODY, skip_front=True)
# front face around the tray opening (straight part between the arcs)
FX0, FX1 = XL + RC, XR - RC
front_rect(FX0, Y0, OX0, Y1, ZF, BODY)
front_rect(OX1, Y0, FX1, Y1, ZF, BODY)
front_rect(OX0, Y0, OX1, OY0, ZF, BODY)
front_rect(OX0, OY1, OX1, Y1, ZF, BODY)
# the top lip, stepped back 0.35 cm (where the console sits on top)
slab(ZF - 0.35, Y1, Y2, BODY, top=LIP, bottom=False)

# tray tunnel: dark faces looking inwards
m.polygon([(OX0, OY1, ZF), (OX1, OY1, ZF), (OX1, OY1, OZB), (OX0, OY1, OZB)], DARK, normal=(0, -1, 0))
m.polygon([(OX0, OY0, ZF), (OX1, OY0, ZF), (OX1, OY0, OZB), (OX0, OY0, OZB)], DARK, normal=(0, 1, 0))
m.polygon([(OX0, OY0, ZF), (OX0, OY1, ZF), (OX0, OY1, OZB), (OX0, OY0, OZB)], DARK, normal=(1, 0, 0))
m.polygon([(OX1, OY0, ZF), (OX1, OY1, ZF), (OX1, OY1, OZB), (OX1, OY0, OZB)], DARK, normal=(-1, 0, 0))
front_rect(OX0, OY0, OX1, OY1, OZB, DARK)

# plinth (recessed, ribbed) and the four broad feet
m.box(XL + 0.6, 0.3, ZB + 0.6, XR - 0.6, Y0, ZF - 1.0, PANEL, faces={'top': None})
for y in (0.55, 0.78):
    front_rect(XL + 0.8, y - 0.06, XR - 0.8, y + 0.06, ZF - 1.0, DARK, lift=0.03)
for x0, x1 in ((XL + 0.9, XL + 5.9), (XR - 5.4, XR - 0.7)):
    for z0, z1 in ((ZF - 4.5, ZF - 0.5), (ZB + 0.5, ZB + 4.0)):
        m.box(x0, 0.0, z0, x1, Y0, z1, FOOT, faces={'top': None})

# ---------------------------------------------------------------- front details
# indicator panel (rounded, dark) with the two grey light windows
panel = Model.rounded_rect(0.9, 1.3, 8.2, 3.15, 0.6, segments=2)
m.decal_xy(panel, ZF, PANEL, lift=0.03)
front_rect(1.3, 2.1, 3.7, 2.65, ZF, WINDOW, lift=0.06)
front_rect(5.4, 1.6, 7.7, 2.15, ZF, WINDOW, lift=0.06)
# dark frame around the tray opening
for r in ((OX0 - 0.3, OY0 - 0.4, OX1 + 0.4, OY0), (OX0 - 0.3, OY1, OX1 + 0.4, OY1 + 0.3),
          (OX0 - 0.3, OY0, OX0, OY1), (OX1, OY0, OX1 + 0.4, OY1)):
    front_rect(r[0], r[1], r[2], r[3], ZF, DARK, lift=0.02)
# thin groove under the top lip, across the front
front_rect(FX0 + 0.2, Y1 - 0.25, FX1 - 0.2, Y1 - 0.12, ZF, DARK, lift=0.02)

# ---------------------------------------------------------------- top
# locating holes and the oval centre mark where the console's feet sit
for x, z, w, d in ((-12.6, -7.4, 0.9, 1.4), (-12.6, 5.0, 0.9, 1.4), (8.2, -7.4, 0.9, 1.4),
                   (8.2, 5.0, 0.9, 1.4), (-1.5, 8.4, 1.6, 0.7), (-1.5, -9.2, 1.6, 0.7)):
    m.decal_xz([(x - w / 2, z + d / 2), (x + w / 2, z + d / 2), (x + w / 2, z - d / 2), (x - w / 2, z - d / 2)],
               Y2, DARK, lift=0.03)
oval = [(-1.5 + 1.3 * math.cos(2 * math.pi * i / 8), -1.0 + 0.55 * math.sin(2 * math.pi * i / 8)) for i in range(8)]
m.decal_xz(oval, Y2, PANEL, lift=0.03)
# shallow grooves outlining the console's seat along the left and back
m.decal_xz([(XL + 0.8, ZF - 1.4), (XL + 1.05, ZF - 1.4), (XL + 1.05, ZB + 1.2), (XL + 0.8, ZB + 1.2)], Y2, DARK, lift=0.03)
m.decal_xz([(XL + 0.8, ZB + 1.45), (XR - 0.8, ZB + 1.45), (XR - 0.8, ZB + 1.2), (XL + 0.8, ZB + 1.2)], Y2, DARK, lift=0.03)

# ---------------------------------------------------------------- side tower (right)
TWX0, TWX1 = XR, 15.25
TZ0, TZ1, TY1 = -1.8, ZF - 1.5, 12.4
prof = [(TZ0, Y0), (TZ1, Y0), (TZ1, TY1 - 1.0), (TZ1 - 1.0, TY1), (TZ0, TY1)]
m.extrude_yz(prof, TWX0, TWX1, BODY, left=False)
# its inner face above the body top, with the dark connector housing
m.polygon([(TWX0, y, z) for z, y in [(TZ0, Y2), (TZ1, Y2), (TZ1, TY1 - 1.0), (TZ1 - 1.0, TY1), (TZ0, TY1)]],
          BODY, normal=(-1, 0, 0))
m.polygon([(TWX0 - 0.03, 7.4, 6.4), (TWX0 - 0.03, 7.4, 0.6), (TWX0 - 0.03, 9.8, 0.6), (TWX0 - 0.03, 9.8, 6.4)],
          DARK, normal=(-1, 0, 0))
# a shallow inset panel on its outer face
m.polygon([(TWX1 + 0.03, 2.2, -0.8), (TWX1 + 0.03, 2.2, 8.2), (TWX1 + 0.03, 9.4, 8.2), (TWX1 + 0.03, 9.4, -0.8)],
          INSET, normal=(1, 0, 0))

# ---------------------------------------------------------------- left side vents
for k in range(5):
    z = 0.5 + k * 1.5
    m.polygon([(XL - 0.03, 2.0, z), (XL - 0.03, 2.0, z + 0.6), (XL - 0.03, 4.8, z + 0.6), (XL - 0.03, 4.8, z)],
              DARK, normal=(-1, 0, 0))

# ---------------------------------------------------------------- back
for x0, x1, y0, y1, col in ((-12.5, -8.5, 2.2, 4.4, PORT), (-6.5, -4.5, 2.6, 3.8, PORT),
                            (-3.5, -1.5, 2.6, 3.8, PORT), (6.0, 10.0, 2.0, 4.6, PANEL)):
    m.polygon([(x1, y0, ZB - 0.03), (x0, y0, ZB - 0.03), (x0, y1, ZB - 0.03), (x1, y1, ZB - 0.03)],
              col, normal=(0, 0, -1))

# ---------------------------------------------------------------- the tray (moving part)
with m.part('tray'):
    # face: a glossy panel sitting in the opening, slightly proud
    m.box(TX0, TY0, TZFB, TX1, TFY1, TZF, TRAYF, faces={'back': None})
    # silver outline box (where the badge sits) on the face, no text
    bx0, bx1, by0, by1, t = TX0 + 2.1, TX0 + 11.4, 2.55, 3.35, 0.18
    for r in ((bx0, by0, bx1, by0 + t), (bx0, by1 - t, bx1, by1), (bx0, by0, bx0 + t, by1), (bx1 - t, by0, bx1, by1)):
        front_rect(r[0], r[1], r[2], r[3], TZF, BADGE, lift=0.03)
    # finger notch line along the face's top edge
    front_rect(TX0 + 0.4, TFY1 - 0.35, TX1 - 0.4, TFY1 - 0.25, TZF, DARK, lift=0.03)
    # the deck behind the face: a slab with a round recess for the disc
    m.box(TX0, TY0, TZB, TX1, TDY, TZFB, TRAYTOP, faces={'top': None, 'front': None})
    N = 16
    ring = [(RX + RR * math.cos(math.pi / 2 + 2 * math.pi * i / N), RZ + RR * math.sin(math.pi / 2 + 2 * math.pi * i / N))
            for i in range(N)]
    # deck top = rectangle minus the round hole, as one sector per hole edge

    def hit(px, pz):
        """where the ray from the recess centre through (px, pz) meets the deck edge"""
        dx, dz = px - RX, pz - RZ
        ts = []
        if dx > 0:
            ts.append((TX1 - RX) / dx)
        if dx < 0:
            ts.append((TX0 - RX) / dx)
        if dz > 0:
            ts.append((TZFB - RZ) / dz)
        if dz < 0:
            ts.append((TZB - RZ) / dz)
        t_ = min(ts)
        return (RX + dx * t_, RZ + dz * t_)

    corners = [(TX1, TZFB), (TX0, TZFB), (TX0, TZB), (TX1, TZB)]

    def ang(p):
        return math.atan2(p[1] - RZ, p[0] - RX) % (2 * math.pi)

    for i in range(N):
        a, b = ring[i], ring[(i + 1) % N]
        ha, hb = hit(*a), hit(*b)
        a0, a1 = ang(a), ang(b)
        if a1 < a0:
            a1 += 2 * math.pi
        cs = []
        for c in corners:
            ac = ang(c)
            if ac < a0:
                ac += 2 * math.pi
            if a0 < ac < a1:
                cs.append((ac, c))
        outer = [ha] + [c for _, c in sorted(cs)] + [hb]
        poly = [a] + outer + [b]
        # angles increase CCW in (x, z); seen from above (+y) that is clockwise -> give the normal
        m.polygon([(x, TDY, z) for x, z in poly], TRAYTOP, normal=(0, 1, 0))
    # recess wall and floor
    for i in range(N):
        (xa, za), (xb, zb) = ring[i], ring[(i + 1) % N]
        mx, mz = (xa + xb) / 2 - RX, (za + zb) / 2 - RZ
        m.polygon([(xa, RY, za), (xb, RY, zb), (xb, TDY, zb), (xa, TDY, za)], PANEL, normal=(-mx, 0, -mz))
    m.polygon([(x, RY, z) for x, z in ring], RECESS, normal=(0, 1, 0))

if __name__ == '__main__':
    print(m.stats())
    print(m.save())

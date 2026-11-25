# SPDX-License-Identifier: GPL-3.0-or-later
"""Sega 32X plugged into a Genesis / Mega Drive, as it is always used: the
black "mushroom" add-on standing in the Genesis cartridge slot. A wide, rounded cap (about 20.8 x 11.8 cm) whose
glossy upper hood dips down in a wave at the front centre over a darker
lower skirt; on top a raised island at the back with the cartridge slot
(two spring dust flaps), a glossy black badge plate in front of it, vent
grilles at both side ends, A/V jacks at the back. Under the cap a dark neck
block and the plug that goes into the Genesis. ~20.8 x 10.1 x 11.8 cm.

The cartridge goes straight down into the top slot, label to the front;
the two dust flaps swing down into the slot (parts flap_f, flap_b).

The Genesis underneath is the megadrive console model (consoles/
megadrive.obj, so build that first). The 32X is built around its own
origin, then moved onto the Genesis slot: its neck stands on the Genesis
top and its cap clears the Genesis disc by 0.35 cm. The Genesis faces it
hides (its slot, its closed dust flaps, the disc top under the cap) are left
out, and it takes this model's colours. The combined unit has a raised
triangle limit of 850 (the user's decision; other consoles 600)."""
import math
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model, load_model

HOOD = (88, 88, 98)        # glossy upper shell + top
SKIRT = (38, 38, 42)       # lower band of the cap
DARK = (10, 10, 12)        # seam under the hood lip, vent slits
ISIDE = (40, 40, 46)       # slot island walls
ITOP = (84, 84, 94)        # slot island top
BADGE = (16, 16, 22)       # glossy black badge plate
HOLE = (4, 4, 6)           # slot cavity, jack holes
FLAP = (64, 64, 72)     # dust flaps
NECK = (26, 26, 30)        # neck block under the cap
SILVER = (160, 160, 168)   # jack rings
RING = (99, 97, 107)       # Genesis: the bright rim of its disc
TONGUE = (49, 44, 49)      # Genesis: the raised tongue on the disc
RED = (186, 36, 40)        # Genesis: power strip and light

# where the 32X sits on the Genesis (megadrive coordinates)
GEN_SLOT_X, GEN_SLOT_Z = 2.9, -5.6     # Genesis slot centre
GEN_TOP, GEN_DISC = 5.5, 6.85          # Genesis body top, flat disc top
Y_BOT = 4.6                            # underside of the 32X cap (own coordinates)
DX, DY, DZ = GEN_SLOT_X, GEN_DISC + 0.35 - Y_BOT, GEN_SLOT_Z

m = Model('sega32x', 'console')


def _sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def face(pts, col, ref):
    """triangle or quad (may be non-planar) wound so it faces direction ref"""
    n = _cross(_sub(pts[1], pts[0]), _sub(pts[2], pts[0]))
    if len(pts) == 4:
        n2 = _cross(_sub(pts[2], pts[0]), _sub(pts[3], pts[0]))
        n = (n[0] + n2[0], n[1] + n2[1], n[2] + n2[2])
    if n[0] * ref[0] + n[1] * ref[1] + n[2] * ref[2] < 0:
        pts = pts[::-1]
    if len(pts) == 3:
        return m.tri(pts[0], pts[1], pts[2], col)
    return m.tri(pts[0], pts[1], pts[2], col) + m.tri(pts[0], pts[2], pts[3], col)


def ring(cx, cz, hx, hz, r, fx, sz, seg=3):
    """rounded-rectangle outline in XZ with extra points at the side
    (z = sz) and at x = +-fx on front and back, so every ring has the same
    structure (index k on one ring matches index k on the next)."""
    pts = [(cx + hx, sz)]
    corners = [(cx + hx - r, cz + hz - r, 0), (cx - hx + r, cz + hz - r, 90),
               (cx - hx + r, cz - hz + r, 180), (cx + hx - r, cz - hz + r, 270)]
    for i, (ox, oz, a0) in enumerate(corners):
        for s in range(seg + 1):
            a = math.radians(a0 + 90 * s / seg)
            pts.append((ox + r * math.cos(a), oz + r * math.sin(a)))
        if i == 0:
            pts += [(cx + fx * f, cz + hz) for f in (1.0, 0.5, 0.0, -0.5, -1.0)]
        elif i == 1:
            pts.append((cx - hx, sz))
        elif i == 2:
            pts += [(cx - fx, cz - hz), (cx + fx, cz - hz)]
    return pts


def band(lo, hi, col, axis=(0.0, 0.0), up=0.0, colfn=None):
    """connect two rings (3D point lists) with quads facing outward from
    the vertical axis through (x, z) = axis (up > 0 tilts the reference
    upward, for the top surfaces)."""
    out = []
    n = len(lo)
    for k in range(n):
        j = (k + 1) % n
        q = [lo[k], lo[j], hi[j], hi[k]]
        mx = sum(p[0] for p in q) / 4 - axis[0]
        mz = sum(p[2] for p in q) / 4 - axis[1]
        c = colfn(k) if colfn else col
        ref = (mx, up, mz)
        if isinstance(c, tuple) and c[0] == 'lo_j':     # split on diagonal lo[j]-hi[k]
            out += face([lo[k], lo[j], hi[k]], c[1], ref) + face([lo[j], hi[j], hi[k]], c[2], ref)
        elif isinstance(c, tuple) and c[0] == 'lo_k':   # split on diagonal lo[k]-hi[j]
            out += face([lo[k], lo[j], hi[j]], c[1], ref) + face([lo[k], hi[j], hi[k]], c[2], ref)
        else:
            out += face(q, c, ref)
    return out


# ---------------------------------------------------------------- the cap
HX, HZ, R = 10.4, 5.9, 3.4     # cap half width, half depth, corner radius
ZC = -1.5                      # slot centre (z)
FX = 4.5                       # front/back extra points (x)


def cap_ring(inset, yfn):
    pts = ring(0.0, 0.0, HX - inset, HZ - inset, R - inset, FX, ZC)
    return [(x, yfn(x, z), z) for x, z in pts]


def seam(x, z):
    """bottom edge of the glossy hood: high at the sides and back, dipping
    in a wave to the front centre"""
    w = math.cos(math.pi / 2 * min(1.0, abs(x) / 8.5)) ** 2
    return 7.65 - 1.7 * w * max(0.0, min(1.0, z / 4.0))


def top_edge(x, z):
    """the top surface: lowest at the front, rising to the back"""
    return 8.95 - 0.28 * z / 4.7


r0 = cap_ring(0.9, lambda x, z: Y_BOT)
r2 = cap_ring(0.05, lambda x, z: 5.75)
rs = cap_ring(0.12, seam)                    # top of the skirt
rh = cap_ring(-0.1, seam)                    # hood lip (overhangs the skirt)
rh2 = cap_ring(0.5, lambda x, z: top_edge(x, z) - 0.35 - 0.45 * (7.65 - seam(x, z)))   # follows the wave a little
rt = cap_ring(1.15, top_edge)

# (no underside: it sits 0.35 cm above the Genesis disc and can't be seen)
band(r0, r2, SKIRT)
band(r2, rs, SKIRT)
band(rs, rh, DARK, up=-1.0)                  # dark seam under the hood lip
band(rh, rh2, HOOD)
band(rh2, rt, HOOD, up=0.5)

# ---------------------------------------------------------------- top + slot island
IHX, IHZ, IR = 7.0, 2.6, 1.6                 # island base
Y_IB, Y_IT = 9.3, 10.1                       # island base / top height
ib = [(x, Y_IB, z) for x, z in ring(0.0, ZC, IHX, IHZ, IR, FX, ZC)]
it = [(x, Y_IT, z) for x, z in ring(0.0, ZC, IHX - 0.45, IHZ - 0.45, IR - 0.45, FX, ZC)]
# a ring between the top edge and the island; the front middle panel of the
# inner band is the glossy black badge plate
def _blend(a, b):
    # 80 % of the way out to the top edge; further at the front centre, so
    # the badge plate's front edge bulges forward with the hood's wave
    w = math.cos(math.pi / 2 * min(1.0, abs(a[0]) / 8.5)) ** 2 if a[2] > 0 else 0.0
    f = 0.8 + 0.13 * w
    return tuple(a[i] * f + b[i] * (1 - f) for i in range(3))


rm = [_blend(a, b) for a, b in zip(rt, ib)]
band(rt, rm, HOOD, axis=(0, ZC), up=8.0)
FRONT_MID = 5                                # index of the panel between the front extra points
band(rm, ib, HOOD, axis=(0, ZC), up=8.0,
     colfn=lambda k: BADGE if FRONT_MID <= k < FRONT_MID + 4 else
     {FRONT_MID - 1: ('lo_j', HOOD, BADGE), FRONT_MID + 4: ('lo_k', HOOD, BADGE)}.get(k, HOOD))
band(ib, it, ISIDE, axis=(0, ZC), up=0.6)

# slot mouth in the island top; cavity straight down
MX, MZ = 5.6, 1.15                           # mouth half width / half depth (media 5.45 x 1.0)
Y_FLOOR = 5.15
n = len(it)
iL = next(i for i, p in enumerate(it) if abs(p[0] + (IHX - 0.45)) < 1e-6 and abs(p[2] - ZC) < 1e-6)
front = it[0:iL + 1] + [(-MX, Y_IT, ZC), (-MX, Y_IT, ZC + MZ), (MX, Y_IT, ZC + MZ), (MX, Y_IT, ZC)]
back = it[iL:] + [it[0], (MX, Y_IT, ZC), (MX, Y_IT, ZC - MZ), (-MX, Y_IT, ZC - MZ), (-MX, Y_IT, ZC)]
m.polygon(front, ITOP, normal=(0, 1, 0))
m.polygon(back, ITOP, normal=(0, 1, 0))
# cavity: inside faces (seen from inside the slot)
cx0, cx1, cz0, cz1 = -MX, MX, ZC - MZ, ZC + MZ
face([(cx0, Y_FLOOR, cz1), (cx1, Y_FLOOR, cz1), (cx1, Y_IT, cz1), (cx0, Y_IT, cz1)], HOLE, (0, 0, -1))
face([(cx0, Y_FLOOR, cz0), (cx1, Y_FLOOR, cz0), (cx1, Y_IT, cz0), (cx0, Y_IT, cz0)], HOLE, (0, 0, 1))
face([(cx0, Y_FLOOR, cz0), (cx0, Y_FLOOR, cz1), (cx0, Y_IT, cz1), (cx0, Y_IT, cz0)], HOLE, (1, 0, 0))
face([(cx1, Y_FLOOR, cz0), (cx1, Y_FLOOR, cz1), (cx1, Y_IT, cz1), (cx1, Y_IT, cz0)], HOLE, (-1, 0, 0))
face([(cx0, Y_FLOOR, cz0), (cx1, Y_FLOOR, cz0), (cx1, Y_FLOOR, cz1), (cx0, Y_FLOOR, cz1)], HOLE, (0, 1, 0))

# two spring dust flaps meeting in the middle, hinged on the long edges
FL_X = 5.45
FL_Y0 = Y_IT - 0.4                           # flap underside; hinge line at (y = FL_Y0, z = ZC +- 1.13)
with m.part('flap_f'):
    m.box(-FL_X, FL_Y0, ZC + 0.02, FL_X, FL_Y0 + 0.1, ZC + 1.13, FLAP)
with m.part('flap_b'):
    m.box(-FL_X, FL_Y0, ZC - 1.13, FL_X, FL_Y0 + 0.1, ZC - 0.02, FLAP)

# ---------------------------------------------------------------- vents at both side ends
def on_band(lo, hi, k, s, t, lift=0.03):
    """point on the quad lo[k], lo[k+1], hi[k+1], hi[k] at s along the ring
    and t up the band, lifted off it along the outward normal"""
    j = (k + 1) % len(lo)
    a = [lo[k][i] + (lo[j][i] - lo[k][i]) * s for i in range(3)]
    b = [hi[k][i] + (hi[j][i] - hi[k][i]) * s for i in range(3)]
    p = [a[i] + (b[i] - a[i]) * t for i in range(3)]
    e1 = _sub(lo[j], lo[k])
    e2 = _sub(hi[k], lo[k])
    nrm = _cross(e1, e2)
    if nrm[0] * p[0] + nrm[2] * p[2] < 0:
        nrm = (-nrm[0], -nrm[1], -nrm[2])
    ln = math.sqrt(sum(c * c for c in nrm))
    return tuple(p[i] + nrm[i] / ln * lift for i in range(3))


# slits stacked up the straight side face of the hood, towards the back:
# right side on panel k = 0 (side point z = ZC -> z = +2.5), left side on
# panel k = 13 (z = +2.5 -> side point z = ZC); both cover z -2.1 .. -0.7
for sgn, k, s0, s1 in ((1, 0, -0.15, 0.2), (-1, 13, 0.8, 1.15)):
    for i in range(4):
        t0, t1 = 0.2 + i * 0.19, 0.29 + i * 0.19
        pts = [on_band(rh, rh2, k, s0, t0), on_band(rh, rh2, k, s1, t0),
               on_band(rh, rh2, k, s1, t1), on_band(rh, rh2, k, s0, t1)]
        face(pts, DARK, (sgn, 0, 0))

# ---------------------------------------------------------------- back: A/V jacks on the skirt
ZB = -(HZ - 0.12) - 0.03
for x, ry in ((-3.0, 6.75), (3.0, 6.75)):
    for rad, col, lift in ((0.5, SILVER, 0.0), (0.24, HOLE, 0.02)):
        pts = [(x + rad * math.cos(2 * math.pi * i / 6), ry + rad * math.sin(2 * math.pi * i / 6), ZB - lift)
               for i in range(6)]
        m.polygon(pts, col, normal=(0, 0, -1))

# ---------------------------------------------------------------- neck under the cap
# (the plug below it is inside the Genesis slot: not modelled)
neck = Model.rounded_rect(-6.6, -2.8, 6.6, 2.8, 0.9, segments=1)
m.prism(neck, GEN_TOP - DY, Y_BOT, NECK, top=False, bottom=False)

# ---------------------------------------------------------------- onto the Genesis
m.verts = [(round(x + DX, 4), round(y + DY, 4), round(z + DZ, 4)) for x, y, z in m.verts]
m._vmap = {}

GEN_COLORS = {                         # megadrive colours -> this model's
    (41, 40, 41): ISIDE,    # body
    (16, 12, 16): DARK,     # grooves, recesses
    (99, 97, 107): RING,    # the bright rim of the disc
    (33, 28, 33): NECK,     # disc top
    (74, 73, 82): FLAP,     # vent slats
    (66, 60, 66): FLAP,     # slider knobs
    (198, 199, 198): SILVER,  # reset button, pins
    (189, 36, 41): RED,     # power strip
    (255, 89, 57): RED,     # power light
    (49, 44, 49): TONGUE,   # the raised tongue
    (24, 24, 33): NECK,     # front band with the ports
}
# hidden under the cap: Genesis faces at or below the disc top inside this
# area (the cap is 20.8 x 11.8; 1.4 cm in from its edge you can't see under it)
HIDE = (DX - 9.0, DX + 9.0, DZ - 4.5, DZ + 4.5)
gen = load_model(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'consoles', 'megadrive.obj'))
gv = gen['verts']
for ia, ib, ic, col, part, uv in gen['tris']:
    if part != 'body' or col == (0, 4, 0):
        continue                       # dust flaps and the dark cavity under them
    tri = [gv[ia], gv[ib], gv[ic]]
    if all(HIDE[0] <= x <= HIDE[1] and HIDE[2] <= z <= HIDE[3] and y <= GEN_DISC + 0.01 for x, y, z in tri):
        continue
    if col == (16, 12, 16) and all(6.6 < math.hypot(x - 2.9, z + 2.0) < 7.1 for x, y, z in tri):
        continue                       # the thin groove ring inside the disc rim (too fine at 320x240)
    m.tri(*tri, GEN_COLORS[col])

print(m.stats())
m.save()

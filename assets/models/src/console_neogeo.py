# SPDX-License-Identifier: GPL-3.0-or-later
"""SNK Neo Geo AES (home console): low-poly console model.

Real size about 32.5 x 6 x 23.7 cm. What makes it read as an AES (Commons
photos Neo-Geo-AES-FL / -FR / -BL, Neogeoaes, Neo-Geo-AES-Console-Set):
  * a wide, flat black wedge: the front face is low, the top slopes up to
    the back;
  * the big racetrack-shaped hump on the back half of the top (the loop round
    the cartridge slot), open at the front where the raised centre lid runs
    from the front edge up into it;
  * the long cartridge slot along the middle of the loop, closed by two
    spring flaps (moving parts "flap_front" / "flap_back") that swing down
    into the slot when the cart goes in;
  * a sloping vent band behind the loop with three grilles;
  * the big round reset button on the left of the top, the power slider at
    the front left, two controller ports, headphone jack and volume slider on
    the front, the memory card slit on the front right.

Proportions measured from the photos (fractions of width from the left,
depth from the front): centre lid 21%..79% at the front, narrowing to the
loop; loop 11%..89% wide, 54%..96% deep (centre 74%); reset at 15% / 42%;
ports at 29% and 65%; memory card slit 80%..97%; vent band 25%..75%.

The slot fits the AES cart (18.5 x 3.4 cm): opening 18.7 x 3.7 cm, a dark
cavity down to y = 0.4 where the cart rests.
"""
import math
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model

BODY = (41, 44, 41)        # black plastic
RING = (66, 69, 66)        # the loop's rounded rim (catches the light)
INNER = (49, 52, 49)       # floor inside the loop
FLAP = (33, 36, 33)        # slot flaps
SLOT = (0, 0, 0)           # cavity inside the slot
GROOVE = (12, 12, 12)      # seams, vents, recesses
RESET = (76, 80, 104)      # slate-blue reset button
PORT = (99, 101, 99)     # port frames, jacks
KNOB = (132, 134, 132)     # power slider knob
GOLD = (206, 164, 66)      # gold bar on the lid (where the logo sits; plain)
BOTTOM = (24, 24, 24)

W, D = 32.5, 23.7
XL, XR = -W / 2, W / 2
ZF, ZB = D / 2, -D / 2
HF = 2.8                   # front face height
HB = 5.4                   # back corner height
K = (HB - HF) / D          # top slope (rise per cm towards the back)


def ys(z):
    """height of the main top surface at depth z"""
    return HF + (ZF - z) * K


# loop (racetrack hump)
ZC = -5.6                  # centre line of loop and slot
S = 8.0                    # half length of the straight part
R_BASE, R_MID, R_TOP, RI_TOP, RI = 4.7, 4.4, 3.8, 2.6, 2.4
Y_MID = 5.7                # rounded shoulder of the rim
Y_RIM = 6.1                # top of the rim
Y_IN = 5.65                # floor inside the loop
SEG = 6                    # segments per half circle

# slot (cart 18.5 x 3.4; decals to 18.54 x 3.46)
SLX = 9.35
SLZ = 1.85
Y_FLOOR = 0.4              # the cart rests here

# centre lid: front edge +-LID_F, narrows to +-S where it meets the loop
LID_F = 9.5
LID_H = 0.25               # lid stands this much proud at the front edge
Z_LID_END = ZC + RI        # lid runs up to the loop's inner floor


def yp(z):
    """height of the centre lid top at depth z (meets Y_IN at Z_LID_END)"""
    y0 = HF + LID_H
    return y0 + (ZF - z) * (Y_IN - y0) / (ZF - Z_LID_END)


# rear vent band
VB = 8.0                   # half width
Y_VB = 4.0                 # height at the back edge

FLAP_T = 0.07              # flap thickness
FLAP_Y = Y_IN - 0.1        # flap top
FLAP_X = 9.30
FLAP_Z0, FLAP_Z1 = 0.16, 1.80   # each flap spans zc +- (0.16..1.80); the gap between shows the slot

m = Model('neogeo', 'console')


def _n(v):
    l = math.sqrt(sum(a * a for a in v))
    return tuple(a / l for a in v)


def face(pts, color, normal):
    return m.polygon(pts, color, normal=normal)


def plane_decal(pts2, fy, normal, color, lift=0.03):
    """decal on a sloped top plane: pts2 are (x, z), fy(z) the plane height"""
    n = _n(normal)
    return m.polygon([(x + n[0] * lift, fy(z) + n[1] * lift, z + n[2] * lift) for x, z in pts2], color, normal=n)


def rect(x0, a0, x1, a1):
    return [(x0, a0), (x1, a0), (x1, a1), (x0, a1)]


def octagon(cx, cy, r, n=8):
    return [(cx + r * math.cos(2 * math.pi * (i + 0.5) / n), cy + r * math.sin(2 * math.pi * (i + 0.5) / n)) for i in range(n)]


def loop_pts(r, seg=SEG):
    """U-shaped part of the racetrack outline (radius r): front-left
    junction, round the left end, along the back, round the right end to the
    front-right junction."""
    pts = []
    for i in range(seg + 1):
        a = math.radians(90 + 180 * i / seg)
        pts.append((-S + r * math.cos(a), ZC + r * math.sin(a)))
    for i in range(seg + 1):
        a = math.radians(270 + 180 * i / seg)
        pts.append((S + r * math.cos(a), ZC + r * math.sin(a)))
    return pts


def outward(x, z):
    cx = max(-S, min(S, x))
    return _n((x - cx, 0.0, z - ZC))


N_TOP = _n((0, 1, K))                       # main top plane normal
N_LID = _n((0, 1, (Y_IN - HF - LID_H) / (ZF - Z_LID_END)))

# ---------------------------------------------------------------- body shell
# side faces (wedge profile)
for sx in (-1, 1):
    x = sx * W / 2
    face([(x, 0, ZF), (x, HF, ZF), (x, HB, ZB), (x, 0, ZB)], BODY, (sx, 0, 0))
# front face and the lid's front lip
face([(XL, 0, ZF), (XR, 0, ZF), (XR, HF, ZF), (XL, HF, ZF)], BODY, (0, 0, 1))
face([(-LID_F, HF, ZF), (LID_F, HF, ZF), (LID_F, HF + LID_H, ZF), (-LID_F, HF + LID_H, ZF)], BODY, (0, 0, 1))
# back face, notched for the vent band
face([(XL, 0, ZB), (XL, HB, ZB), (-VB, HB, ZB), (-VB, Y_VB, ZB), (VB, Y_VB, ZB), (VB, HB, ZB),
      (XR, HB, ZB), (XR, 0, ZB)], BODY, (0, 0, -1))
# bottom
face([(XL, 0, ZF), (XR, 0, ZF), (XR, 0, ZB), (XL, 0, ZB)], BOTTOM, (0, -1, 0))

# main top: left and right of the lid / loop / vent band
base = loop_pts(R_BASE)
left_cap = base[1:SEG]                      # left end points between the junctions
right_cap = base[SEG + 2:-1]
lt = [(XL, ZF), (-LID_F, ZF), (-S, ZC + R_BASE)] + left_cap + [(-S, ZC - R_BASE), (-VB, ZB), (XL, ZB)]
rt = [(XR, ZB), (VB, ZB), (S, ZC - R_BASE)] + right_cap + [(S, ZC + R_BASE), (LID_F, ZF), (XR, ZF)]
for poly in (lt, rt):
    face([(x, ys(z), z) for x, z in poly], BODY, (0, 1, 0))

# rear vent band (slopes down to the back) and its little end walls
yv1 = ys(ZC - R_BASE)
face([(-VB, Y_VB, ZB), (VB, Y_VB, ZB), (VB, yv1, ZC - R_BASE), (-VB, yv1, ZC - R_BASE)], BODY, (0, 1, -0.5))
for sx in (-1, 1):
    x = sx * VB
    face([(x, Y_VB, ZB), (x, yv1, ZC - R_BASE), (x, HB, ZB)], BODY, (-sx, 0, 0))
VB_K = (yv1 - Y_VB) / (ZC - R_BASE - ZB)
N_VB = _n((0, 1, -VB_K))


def yvb(z):
    return Y_VB + (z - ZB) * VB_K


for gx in (-5.1, 0.0, 5.1):
    for k in range(3):
        z0 = ZB + 0.3 + k * 0.42
        plane_decal(rect(gx - 2.1, z0, gx + 2.1, z0 + 0.2), yvb, N_VB, GROOVE)

# ---------------------------------------------------------------- centre lid
lid = [(-LID_F, ZF), (LID_F, ZF), (S, ZC + R_BASE), (S, Z_LID_END), (-S, Z_LID_END), (-S, ZC + R_BASE)]
face([(x, yp(z), z) for x, z in lid], BODY, N_LID)
for sx in (-1, 1):
    face([(sx * LID_F, HF, ZF), (sx * S, ys(ZC + R_BASE), ZC + R_BASE),
          (sx * S, yp(ZC + R_BASE), ZC + R_BASE), (sx * LID_F, HF + LID_H, ZF)], BODY, (sx, 0, 0))
# plain gold bar and a thin grey line where the logo and caption sit
plane_decal(rect(-3.0, 4.6, 3.0, 5.4), yp, N_LID, GOLD)
plane_decal(rect(-2.6, 3.7, 2.6, 3.85), yp, N_LID, PORT)

# ---------------------------------------------------------------- the loop
top_o = loop_pts(R_TOP)
mid_o = loop_pts(R_MID)
top_i = loop_pts(RI_TOP)
bot_i = loop_pts(RI)
for i in range(len(base) - 1):
    j = i + 1
    mx, mz = (base[i][0] + base[j][0]) / 2, (base[i][1] + base[j][1]) / 2
    o = outward(mx, mz)
    # outer wall: steep lower band, rounded upper band
    face([(base[i][0], ys(base[i][1]), base[i][1]), (base[j][0], ys(base[j][1]), base[j][1]),
          (mid_o[j][0], Y_MID, mid_o[j][1]), (mid_o[i][0], Y_MID, mid_o[i][1])], RING, (o[0], 0.3, o[2]))
    face([(mid_o[i][0], Y_MID, mid_o[i][1]), (mid_o[j][0], Y_MID, mid_o[j][1]),
          (top_o[j][0], Y_RIM, top_o[j][1]), (top_o[i][0], Y_RIM, top_o[i][1])], RING, (o[0], 1.2, o[2]))
    # rim top
    face([(top_o[i][0], Y_RIM, top_o[i][1]), (top_o[j][0], Y_RIM, top_o[j][1]),
          (top_i[j][0], Y_RIM, top_i[j][1]), (top_i[i][0], Y_RIM, top_i[i][1])], RING, (0, 1, 0))
    # inner wall
    face([(top_i[i][0], Y_RIM, top_i[i][1]), (top_i[j][0], Y_RIM, top_i[j][1]),
          (bot_i[j][0], Y_IN, bot_i[j][1]), (bot_i[i][0], Y_IN, bot_i[i][1])], RING, (-o[0], 0.6, -o[2]))


def cross_lid(z0, y0, z1, y1):
    """where the line (z0,y0)-(z1,y1) meets the lid top"""
    lo, hi = 0.0, 1.0
    for _ in range(60):
        t = (lo + hi) / 2
        z, y = z0 + (z1 - z0) * t, y0 + (y1 - y0) * t
        if y < yp(z):
            lo = t
        else:
            hi = t
    t = (lo + hi) / 2
    return z0 + (z1 - z0) * t, y0 + (y1 - y0) * t


# end faces where the loop meets the lid (the part above the lid top)
prof = [(ZC + R_BASE, ys(ZC + R_BASE)), (ZC + R_MID, Y_MID), (ZC + R_TOP, Y_RIM), (ZC + RI_TOP, Y_RIM), (ZC + RI, Y_IN)]
end = None
for k in range(len(prof) - 1):
    (z0, y0), (z1, y1) = prof[k], prof[k + 1]
    if y0 < yp(z0) and y1 >= yp(z1):
        end = [cross_lid(z0, y0, z1, y1)] + prof[k + 1:]
        break
for sx in (-1, 1):
    face([(sx * S, y, z) for z, y in end], RING, (-sx, 0, 0))


# floor inside the loop, round the slot opening
def quarter(r, a0, a1, side):
    pts = []
    for i in range(SEG // 2 + 1):
        a = math.radians(a0 + (a1 - a0) * i / (SEG // 2))
        pts.append((side * S + r * math.cos(a), ZC + r * math.sin(a)))
    return pts


front_floor = quarter(RI, 180, 90, -1) + quarter(RI, 90, 0, 1) + [(SLX, ZC), (SLX, ZC + SLZ), (-SLX, ZC + SLZ), (-SLX, ZC)]
back_floor = quarter(RI, 180, 270, -1) + quarter(RI, 270, 360, 1) + [(SLX, ZC), (SLX, ZC - SLZ), (-SLX, ZC - SLZ), (-SLX, ZC)]
for poly in (front_floor, back_floor):
    face([(x, Y_IN, z) for x, z in poly], INNER, (0, 1, 0))

# the slot cavity (faces point inwards)
c = [(-SLX, ZC - SLZ), (SLX, ZC - SLZ), (SLX, ZC + SLZ), (-SLX, ZC + SLZ)]
for i in range(4):
    (x0, z0), (x1, z1) = c[i], c[(i + 1) % 4]
    mx, mz = (x0 + x1) / 2, (z0 + z1) / 2
    face([(x0, Y_FLOOR, z0), (x1, Y_FLOOR, z1), (x1, Y_IN, z1), (x0, Y_IN, z0)], SLOT, (-mx, 0, -(mz - ZC)))
face([(x, Y_FLOOR, z) for x, z in c], SLOT, (0, 1, 0))

# the two spring flaps, closed
with m.part('flap_front'):
    m.box(-FLAP_X, FLAP_Y - FLAP_T, ZC + FLAP_Z0, FLAP_X, FLAP_Y, ZC + FLAP_Z1, FLAP)
with m.part('flap_back'):
    m.box(-FLAP_X, FLAP_Y - FLAP_T, ZC - FLAP_Z1, FLAP_X, FLAP_Y, ZC - FLAP_Z0, FLAP)

# ---------------------------------------------------------------- top left: reset button, seams
RX, RZ = -11.4, 2.0


def top_disc(cx, cz, r, h, color, segs=8):
    """a round button standing on the main top plane"""
    ring = [(cx + r * math.cos(2 * math.pi * (i + 0.5) / segs), cz + r * math.sin(2 * math.pi * (i + 0.5) / segs))
            for i in range(segs)]
    top = [(x + N_TOP[0] * h, ys(z) + N_TOP[1] * h, z + N_TOP[2] * h) for x, z in ring]
    bot = [(x, ys(z) - 0.05, z) for x, z in ring]
    face(top, color, N_TOP)
    for i in range(segs):
        j = (i + 1) % segs
        mx, mz = (ring[i][0] + ring[j][0]) / 2 - cx, (ring[i][1] + ring[j][1]) / 2 - cz
        face([bot[i], bot[j], top[j], top[i]], color, (mx, 0, mz))


plane_decal(octagon(RX, RZ, 1.75), ys, N_TOP, GROOVE, lift=0.02)
top_disc(RX, RZ, 1.3, 0.35, RESET)
# seam round the power / reset corner panel
plane_decal([(XL, 6.2), (-11.0, 6.6), (-11.0, 6.75), (XL, 6.35)], ys, N_TOP, GROOVE, lift=0.02)
plane_decal([(-11.0, 6.6), (-LID_F - 0.05, ZF), (-LID_F - 0.2, ZF), (-11.15, 6.72)], ys, N_TOP, GROOVE, lift=0.02)
# seam in front of the memory card panel
plane_decal([(XR, 6.6), (LID_F + 0.6, 6.6), (LID_F + 0.6, 6.75), (XR, 6.75)], ys, N_TOP, GROOVE, lift=0.02)

# ---------------------------------------------------------------- front face
FZ = ZF
# power slider (far left)
m.decal_xy(rect(-15.3, 0.7, -12.3, 1.75), FZ, GROOVE, lift=0.03)
m.box(-14.9, 0.85, FZ, -13.7, 1.6, FZ + 0.25, KNOB, faces={'back': None})
# controller ports 1 and 2 (D-sub, wider at the top)
for px in (-6.8, 5.0):
    m.decal_xy([(px - 1.35, 0.75), (px + 1.35, 0.75), (px + 1.5, 2.05), (px - 1.5, 2.05)], FZ, PORT, lift=0.03)
    m.decal_xy([(px - 1.05, 0.95), (px + 1.05, 0.95), (px + 1.2, 1.85), (px - 1.2, 1.85)], FZ, GROOVE, lift=0.05)
# headphone jack and volume slider
m.decal_xy(octagon(-3.0, 1.4, 0.32), FZ, PORT, lift=0.03)
m.decal_xy(octagon(-3.0, 1.4, 0.16), FZ, GROOVE, lift=0.05)
m.decal_xy(rect(-1.2, 1.25, 1.6, 1.5), FZ, GROOVE, lift=0.03)
# memory card slit (front right)
m.decal_xy(rect(9.8, 0.8, 15.4, 1.55), FZ, GROOVE, lift=0.03)
m.decal_xy(rect(10.0, 1.05, 15.2, 1.3), FZ, SLOT, lift=0.05)
# seam between the lid section and the side sections of the front
for sx in (-1, 1):
    m.decal_xy(rect(sx * LID_F - 0.08, 0.2, sx * LID_F + 0.08, HF), FZ, GROOVE, lift=0.02)

# ---------------------------------------------------------------- back and sides
BZ = ZB - 0.03
for sx in (-1, 1):
    for k in range(6):
        x0 = sx * (10.6 + k * 0.85)
        m.polygon([(x0, 4.35, BZ), (x0 + sx * 0.35, 4.35, BZ), (x0 + sx * 0.35, 5.05, BZ), (x0, 5.05, BZ)],
                  GROOVE, normal=(0, 0, -1))
# A/V and power sockets (back left)
m.polygon([(-8.8, 1.2, BZ), (-14.4, 1.2, BZ), (-14.4, 3.2, BZ), (-8.8, 3.2, BZ)], GROOVE, normal=(0, 0, -1))
for cx, r in ((-10.4, 0.6), (-13.0, 0.4)):
    m.polygon([(x, y, BZ - 0.03) for x, y in octagon(cx, 2.2, r)], PORT, normal=(0, 0, -1))
for sx in (-1, 1):
    x = sx * (W / 2 + 0.03)
    for k in range(5):
        z0 = ZB + 0.8 + k * 0.7
        top = ys(z0) - 0.5
        m.polygon([(x, top - 0.6, z0), (x, top - 0.6, z0 + 0.3), (x, top, z0 + 0.3), (x, top, z0)],
                  GROOVE, normal=(sx, 0, 0))

print(m.stats())
m.save()

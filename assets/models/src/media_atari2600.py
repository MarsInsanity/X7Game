# SPDX-License-Identifier: GPL-3.0-or-later
"""Atari 2600 cartridge (the standard Atari shell): a black slab with
softly rounded corners and bevelled edges, standing upright, connector end
at y = 0, label side to +Z.

Signature features (from photos of the real shell): the front is almost
all label, sitting in a shallow pocket inside a narrow black rim; the end
label on the top edge (silver frame, black field, red title); a matching
shallow panel on the back; the connector opening in the bottom edge, with
the black dust door inside it. Tighter corners at the top (grip) end,
rounder ones at the connector end.

The front label is the picture area (the game's picture, upright when the
cartridge stands upright). The whole shell (W x H x D = 8.3 x 10.0 x 2.3 cm)
is one closed shape with flat front / back faces, so the console's slot can
be built straight around it.
(The real cartridge goes in with the label to the back of the console; X7
Game's convention puts the picture to the front.)"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model
import math

SHELL = (34, 34, 38)        # black plastic, front / back
EDGE = (64, 64, 72)         # sides, top, bevels: so the outline reads
POCKET = (14, 14, 16)       # label pocket walls
PANEL = (48, 48, 54)        # back panel floor
LABEL = (176, 176, 186)     # plain label colour (picture fallback)
SILVER = (196, 196, 206)    # end label frame
LBLACK = (18, 18, 22)       # end label field
RED = (208, 40, 32)         # end label title
HOLE = (8, 8, 10)           # connector opening walls
DOOR = (44, 44, 50)         # dust door inside the opening

m = Model('atari2600', 'media')

W, H, D = 8.3, 10.0, 2.3
hw = W / 2
ZF, ZB = D / 2, -D / 2
C = 0.14                    # edge bevel
RT, RB = 0.35, 0.6          # corner radius at the top (grip) end / connector end
SEG = 2                     # segments per corner arc


def outline(inset):
    """corner groups TR, TL, BL, BR (counter-clockwise seen from +Z), each a
    list of SEG + 1 points; `inset` shrinks the outline evenly"""
    groups = []
    for cx, cy, a0, r in [(hw - RT, H - RT, 0, RT), (-hw + RT, H - RT, 90, RT),
                          (-hw + RB, RB, 180, RB), (hw - RB, RB, 270, RB)]:
        rr = r - inset
        groups.append([(cx + rr * math.cos(math.radians(a0 + 90 * s / SEG)),
                        cy + rr * math.sin(math.radians(a0 + 90 * s / SEG))) for s in range(SEG + 1)])
    return groups


def flat(groups):
    return [p for g in groups for p in g]


CENTRE = (0.0, H / 2, 0.0)


def quad_out(a, b, c, d, col, inward=False):
    """a quad whose winding is fixed so it faces away from the body centre
    (or towards `inward`'s axis when inward is given as a point)"""
    n = (0.0, 0.0, 0.0)
    u = [b[i] - a[i] for i in range(3)]
    v = [d[i] - a[i] for i in range(3)]
    n = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
    mid = [(a[i] + b[i] + c[i] + d[i]) / 4 for i in range(3)]
    ref = inward if inward else CENTRE
    out = [mid[i] - ref[i] for i in range(3)]
    s = sum(n[i] * out[i] for i in range(3))
    if (s < 0) != bool(inward):
        return m.quad(d, c, b, a, col)
    return m.quad(a, b, c, d, col)


full = flat(outline(0.0))
ins = flat(outline(C))
N = len(full)

# ---- sides: the full outline from back bevel to front bevel; the bottom
# segment (connector end, between BL and BR groups) is left for the opening
ZF1, ZB1 = ZF - C, ZB + C
BOT = 3 * (SEG + 1) - 1           # index of the last BL point (start of the bottom edge)
for i in range(N):
    a, b = full[i], full[(i + 1) % N]
    if i != BOT:
        quad_out((a[0], a[1], ZB1), (b[0], b[1], ZB1), (b[0], b[1], ZF1), (a[0], a[1], ZF1), EDGE)
    # bevels front and back
    ia, ib = ins[i], ins[(i + 1) % N]
    quad_out((a[0], a[1], ZF1), (b[0], b[1], ZF1), (ib[0], ib[1], ZF), (ia[0], ia[1], ZF), EDGE)
    quad_out((a[0], a[1], ZB1), (b[0], b[1], ZB1), (ib[0], ib[1], ZB), (ia[0], ia[1], ZB), EDGE)


def frame(groups, inner, z, normal, col):
    """a flat face at depth z: the (inset) outline around a rectangular
    hole whose corners `inner` (TR, TL, BL, BR) each fan to one corner group"""
    for k in range(4):
        g, I = groups[k], inner[k]
        for p, q in zip(g, g[1:]):
            m.polygon([(I[0], I[1], z), (p[0], p[1], z), (q[0], q[1], z)], col, normal=normal)
        gn, In = groups[(k + 1) % 4], inner[(k + 1) % 4]
        m.polygon([(g[-1][0], g[-1][1], z), (gn[0][0], gn[0][1], z), (In[0], In[1], z), (I[0], I[1], z)],
                  col, normal=normal)


def pocket(inner, z, depth, normal_sign, wall, floor):
    """the walls and floor of a shallow rectangular pocket"""
    zf = z - normal_sign * depth
    ref = (0.0, (inner[0][1] + inner[2][1]) / 2, zf)
    for k in range(4):
        a, b = inner[k], inner[(k + 1) % 4]
        quad_out((a[0], a[1], z), (b[0], b[1], z), (b[0], b[1], zf), (a[0], a[1], zf), wall, inward=ref)
    m.polygon([(p[0], p[1], zf) for p in inner], floor, normal=(0, 0, normal_sign))
    return zf


# ---- front: narrow rim around the label pocket; the label is the picture
LX, LY0, LY1 = 3.68, 0.52, 9.5               # pocket
front_in = [(LX, LY1), (-LX, LY1), (-LX, LY0), (LX, LY0)]
frame(outline(C), front_in, ZF, (0, 0, 1), SHELL)
zf = pocket(front_in, ZF, 0.1, 1, POCKET, LBLACK)
PX, PY0, PY1 = 3.58, 0.62, 9.4               # the label sticker inside the pocket
m.image_xy(-PX, PY0, PX, PY1, zf, fallback=LABEL, lift=0.03)

# ---- back: the same rim around a shallow moulded panel
BX, BY0, BY1 = 3.45, 0.9, 9.1
back_in = [(BX, BY1), (-BX, BY1), (-BX, BY0), (BX, BY0)]
frame(outline(C), back_in, ZB, (0, 0, -1), SHELL)
pocket(back_in, ZB, 0.08, -1, POCKET, PANEL)

# ---- bottom (connector end): the bottom face around the opening, the
# opening's walls and the dust door inside
a, b = full[BOT], full[BOT + 1]               # (-hw + RB, 0), (hw - RB, 0)
OX, OZ0, OZ1, OH = 3.3, -0.62, 0.62, 0.7
outer = [(b[0], ZF1), (a[0], ZF1), (a[0], ZB1), (b[0], ZB1)]     # x, z
inner = [(OX, OZ1), (-OX, OZ1), (-OX, OZ0), (OX, OZ0)]
for k in range(4):
    p, q = outer[k], outer[(k + 1) % 4]
    r, s = inner[(k + 1) % 4], inner[k]
    m.polygon([(p[0], 0, p[1]), (q[0], 0, q[1]), (r[0], 0, r[1]), (s[0], 0, s[1])], EDGE, normal=(0, -1, 0))
ref = (0.0, OH / 2, 0.0)
for k in range(4):
    p, q = inner[k], inner[(k + 1) % 4]
    quad_out((p[0], 0, p[1]), (q[0], 0, q[1]), (q[0], OH, q[1]), (p[0], OH, p[1]), HOLE, inward=ref)
m.polygon([(p[0], OH, p[1]) for p in inner], DOOR, normal=(0, -1, 0))

# ---- end label on the top edge: silver frame, black field, red title bar
TX, TZ = hw - RT - 0.15, 0.82
m.decal_xz([(-TX, -TZ), (TX, -TZ), (TX, TZ), (-TX, TZ)], H, SILVER, lift=0.015)
m.decal_xz([(-TX + 0.12, -TZ + 0.12), (TX - 0.12, -TZ + 0.12), (TX - 0.12, TZ - 0.12), (-TX + 0.12, TZ - 0.12)],
           H, LBLACK, lift=0.03)
m.decal_xz([(-1.5, -0.2), (1.5, -0.2), (1.5, 0.2), (-1.5, 0.2)], H, RED, lift=0.045)

print(m.stats())
print(m.save())

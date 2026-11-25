# SPDX-License-Identifier: GPL-3.0-or-later
"""Neo Geo AES cartridge: the huge black shell standing upright, label to +Z.

Real size 18.5 x 13.2 x 3.4 cm (wider than tall). What makes it read as an
AES cart (Commons photos Neo-Geo-AES-Cartridge-Front / -Bottom):
  * plain black box with softly bevelled top edges;
  * the label: a near-square sticker in the upper middle of the front that
    runs up to the top edge and wraps over the top (and down the back);
  * the top edge dips where the label is: two raised shoulders at the ends,
    each with grooves running along it;
  * a band of horizontal grip ridges along the bottom of the front and back
    (wrapping round the ends), split into four panels (narrow, wide, wide,
    narrow);
  * a long guide groove down each end;
  * the bottom: one wide opening with the two circuit boards' card edges
    (gold contacts) set back inside.

The game's picture is the front label (one image area). The shell below the
label is a clean closed box of exactly 18.5 x 3.4 cm, so the console's top
slot can be built straight around it; only flat decals (ridges, grooves,
lifted 0.02 cm) sit on it.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model

SHELL = (40, 41, 40)         # black plastic
BEVEL = (74, 77, 74)         # bevelled top edges
RIDGE = (107, 109, 107)      # grip ridge highlights
GROOVE = (10, 10, 12)        # guide grooves, shoulder grooves
LABEL = (208, 208, 204)      # plain label paper (picture fallback, top / back wrap)
CAVITY = (16, 16, 16)        # inside the connector opening
PCB = (40, 98, 60)           # circuit boards
GOLD = (220, 180, 84)        # card edge contacts

W, H, D = 18.5, 13.2, 3.4
hw = W / 2
ZF, ZB = D / 2, -D / 2
C = 0.3                       # top bevel
SX, SX0, YD = 5.6, 4.7, 12.8  # shoulder starts at |x| = SX; dip floor |x| < SX0 at y = YD
LX, LY0, LY1 = 4.55, 5.8, 12.46         # label half width, bottom

m = Model('neogeo', 'media')

# ---------------------------------------------------------------- shell
top = [(-hw, H), (-SX, H), (-SX0, YD), (SX0, YD), (SX, H), (hw, H)]   # top edge, left to right
label_seg = 2                 # index of the dipped (label) segment
outline = [(-hw, 0), (hw, 0)] + [(x, y - C) for x, y in reversed(top)]
m.polygon([(x, y, ZF) for x, y in outline], SHELL, normal=(0, 0, 1))
m.polygon([(x, y, ZB) for x, y in outline], SHELL, normal=(0, 0, -1))
for i in range(len(top) - 1):
    (xa, ya), (xb, yb) = top[i], top[i + 1]
    lab = i == label_seg
    # front bevel, back bevel, top
    m.quad((xa, ya - C, ZF), (xb, yb - C, ZF), (xb, yb, ZF - C), (xa, ya, ZF - C), LABEL if lab else BEVEL)
    m.quad((xb, yb - C, ZB), (xa, ya - C, ZB), (xa, ya, ZB + C), (xb, yb, ZB + C), LABEL if lab else BEVEL)
    m.quad((xa, ya, ZF - C), (xb, yb, ZF - C), (xb, yb, ZB + C), (xa, ya, ZB + C), LABEL if lab else SHELL)
side = [(ZB, 0), (ZF, 0), (ZF, H - C), (ZF - C, H), (ZB + C, H), (ZB, H - C)]   # (z, y)
for sx in (1, -1):
    m.polygon([(sx * hw, y, z) for z, y in side], SHELL, normal=(sx, 0, 0))

# ---------------------------------------------------------------- bottom: connector opening
OX, OZ, OY = 7.4, 1.25, 1.0   # opening half width, half depth, cavity height
m.polygon([(-hw, 0, ZB), (hw, 0, ZB), (hw, 0, ZF), (OX, 0, ZF), (OX, 0, -OZ), (-OX, 0, -OZ),
           (-OX, 0, ZF), (-hw, 0, ZF)], SHELL, normal=(0, -1, 0))
m.polygon([(-OX, 0, OZ), (OX, 0, OZ), (OX, 0, ZF), (-OX, 0, ZF)], SHELL, normal=(0, -1, 0))
# cavity walls (facing inwards) and ceiling
m.quad((-OX, 0, -OZ), (OX, 0, -OZ), (OX, OY, -OZ), (-OX, OY, -OZ), CAVITY)
m.quad((OX, 0, OZ), (-OX, 0, OZ), (-OX, OY, OZ), (OX, OY, OZ), CAVITY)
m.quad((-OX, 0, OZ), (-OX, 0, -OZ), (-OX, OY, -OZ), (-OX, OY, OZ), CAVITY)
m.quad((OX, 0, -OZ), (OX, 0, OZ), (OX, OY, OZ), (OX, OY, -OZ), CAVITY)
m.quad((-OX, OY, -OZ), (OX, OY, -OZ), (OX, OY, OZ), (-OX, OY, OZ), CAVITY)
# the two boards' card edges
for zc, bx in ((0.5, 6.9), (-0.5, 6.5)):
    m.box(-bx, 0.3, zc - 0.08, bx, OY, zc + 0.08, PCB,
          faces={'top': None, 'front': GOLD, 'back': GOLD})

# ---------------------------------------------------------------- grip ridges (front, back, ends)
RY = [0.45 + 0.55 * i for i in range(4)]     # ridge bottoms
RH = 0.2
panels = [(-hw + 0.25, -7.3), (-7.0, -0.15), (0.15, 7.0), (7.3, hw - 0.25)]
for y in RY:
    for x0, x1 in panels:
        m.decal_xy([(x0, y), (x1, y), (x1, y + RH), (x0, y + RH)], ZF, RIDGE)
        m.polygon([(x1, y, ZB - 0.02), (x0, y, ZB - 0.02), (x0, y + RH, ZB - 0.02), (x1, y + RH, ZB - 0.02)],
                  RIDGE, normal=(0, 0, -1))
    for sx in (1, -1):
        xx = sx * (hw + 0.02)
        m.polygon([(xx, y, ZB + 0.15), (xx, y, ZF - 0.15), (xx, y + RH, ZF - 0.15), (xx, y + RH, ZB + 0.15)],
                  RIDGE, normal=(sx, 0, 0))

# ---------------------------------------------------------------- guide grooves down the ends
for sx in (1, -1):
    xx = sx * (hw + 0.02)
    m.polygon([(xx, 2.9, 0.75), (xx, 2.9, 1.0), (xx, 10.8, 1.0), (xx, 10.8, 0.75)], GROOVE, normal=(sx, 0, 0))

# ---------------------------------------------------------------- shoulder grooves on top
for sx in (1, -1):
    x0, x1 = sorted((sx * (SX + 0.3), sx * (hw - 0.35)))
    for zc in (0.45, -0.45):
        m.decal_xz([(x0, zc + 0.09), (x1, zc + 0.09), (x1, zc - 0.09), (x0, zc - 0.09)], H, GROOVE)

# ---------------------------------------------------------------- label: picture on the front, paper on the back
m.image_xy(-LX, LY0, LX, LY1, ZF, fallback=LABEL, lift=0.03)
m.polygon([(LX, LY0, ZB - 0.03), (-LX, LY0, ZB - 0.03), (-LX, LY1, ZB - 0.03), (LX, LY1, ZB - 0.03)],
          LABEL, normal=(0, 0, -1))

print(m.stats())
print(m.save())

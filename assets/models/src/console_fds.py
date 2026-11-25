# SPDX-License-Identifier: GPL-3.0-or-later
"""Famicom Disk System drive (HVC-022): a long red box whose front is a black
panel set in between a thin red top cap and a thicker red base. The panel
holds the slot window (the disk slot with a finger notch below it and the
yellow eject button), a raised block at each end (the right one with the
access lamp) and two banks of vent grooves. The top has a seam behind the
front cap and the battery lid at the back; a seam runs round the sides.

Measured from Commons photos (straight-on front view: 15 cm = 927 px):
height 7.0, red base 0..1.41, black panel 1.41..6.31, red cap 6.31..7.0;
the three-quarter views read a little lower and longer, so the model is
15.0 x 6.8 x 23.5 with the front features scaled to 6.8.

Moving parts: 'flap' (the dust flap just inside the slot, hinged at its
top edge, swings inwards when the disk goes in) and 'eject' (the yellow
button, pops out when the disk is seated)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model

RED = (196, 24, 34)
RED_DK = (92, 8, 14)
BLACK = (40, 40, 44)          # front panel
BLOCK = (54, 54, 60)          # raised end blocks, slot flaps
RECESS = (20, 20, 24)         # inside the slot window
CAVITY = (6, 6, 8)            # the slot tunnel, vent grooves
NOTCH = (96, 96, 102)         # finger notch below the slot
SILVER = (168, 168, 174)      # window sill
YELLOW = (252, 188, 24)       # eject button
LAMP = (150, 10, 10)          # access lamp (off)
BADGE = (186, 186, 190)       # model plate (plain)
FLAP = (30, 30, 36)           # dust flap

W, H, D = 15.0, 6.8, 23.5
K = H / 7.0                    # front features measured on a 7.0 front, scaled to H
def k(y):
    return round(y * K, 3)
HX = W / 2
ZB, ZF = -D / 2, D / 2         # back, front of the red shell
ZP = ZF - 0.25                 # black front panel (set back under the cap)
YB, YC = k(1.41), k(6.31)           # top of the red base, bottom of the red cap

# slot window (recess in the black panel)
WX0, WX1, WY0, WY1 = -5.01, 3.99, k(3.64), k(6.03)
ZW = ZP - 0.30                 # back of the window = slot entry plane
# slot opening: the 7.6 x 0.62 card, centred x -0.5, y 5.225
SYC = k(5.225)                 # card centre height when seated
SX0, SX1, SY0, SY1 = -4.40, 3.40, SYC - 0.375, SYC + 0.375
ZL = ZW - 0.30                 # back of the lip around the slot
CY1 = SY1 + 0.18                    # tunnel ceiling behind the lip (room for the flap)
GRIP_OUT = 1.10                # the card's grip band stays out of the slot
ZC = ZW + GRIP_OUT - 9.0 - 0.15   # end of the tunnel, 0.15 past the card
# eject button
EX0, EX1, EY0, EY1 = 1.08, 2.65, k(3.80), k(4.24)

m = Model('fds', 'console')

# ---------------------------------------------------------------- red shell
prof = [(ZB, 0), (ZF - 0.35, 0), (ZF, 0.45), (ZF, YB), (ZP, YB), (ZP, YC),
        (ZF, YC), (ZF, H - 0.2), (ZF - 0.2, H), (ZB, H)]
m.extrude_yz(prof, -HX, HX, RED, side=False)
edges = [  # (point a, point b, outward normal (y, z))
    (0, 1, (-1, 0)), (1, 2, (-0.35, 0.45)), (2, 3, (0, 1)), (3, 4, (1, 0)),
    (5, 6, (-1, 0)), (6, 7, (0, 1)), (7, 8, (0.2, 0.2)), (8, 9, (1, 0))]
for a, b, (ny, nz) in edges:
    (za, ya), (zb, yb) = prof[a], prof[b]
    m.polygon([(-HX, ya, za), (HX, ya, za), (HX, yb, zb), (-HX, yb, zb)], RED, normal=(0, ny, nz))

# ---------------------------------------------------------------- black front panel
BL1, BR0 = -5.61, 4.59         # inner edges of the end blocks
def fq(x0, y0, x1, y1, col=BLACK, z=ZP):
    m.quad((x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z), col)
fq(-HX, YB, HX, WY0)                       # below the window and blocks
fq(-HX, WY1, HX, YC)                       # above
fq(BL1, WY0, WX0, WY1)                     # between left block and window
fq(WX1, WY0, BR0, WY1)                     # between window and right block
# raised end blocks
m.box(-HX, WY0, ZP, BL1, WY1, ZP + 0.12, BLOCK, faces={'back': None})
m.box(BR0, WY0, ZP, HX, WY1, ZP + 0.12, BLOCK, faces={'back': None})
m.decal_xy([(5.47, k(4.07)), (5.69, k(4.07)), (5.69, k(4.29)), (5.47, k(4.29))], ZP + 0.12, LAMP)
# vent grooves, both ends, below the blocks
for y in (k(1.87), k(2.19), k(2.51), k(2.83)):
    m.decal_xy([(-HX, y), (-5.61, y), (-5.61, y + 0.15), (-HX, y + 0.15)], ZP, CAVITY)
    m.decal_xy([(3.02, y), (HX, y), (HX, y + 0.15), (3.02, y + 0.15)], ZP, CAVITY)
# plain model plate under the (omitted) maker name
m.decal_xy([(-5.28, k(1.73)), (-3.10, k(1.73)), (-3.10, k(2.02)), (-5.28, k(2.02))], ZP, BADGE)

# ---------------------------------------------------------------- slot window
m.polygon([(WX0, WY0, ZP), (WX1, WY0, ZP), (WX1, WY0, ZW), (WX0, WY0, ZW)], SILVER, normal=(0, 1, 0))
m.polygon([(WX0, WY1, ZP), (WX1, WY1, ZP), (WX1, WY1, ZW), (WX0, WY1, ZW)], RECESS, normal=(0, -1, 0))
m.polygon([(WX0, WY0, ZP), (WX0, WY1, ZP), (WX0, WY1, ZW), (WX0, WY0, ZW)], RECESS, normal=(1, 0, 0))
m.polygon([(WX1, WY0, ZP), (WX1, WY1, ZP), (WX1, WY1, ZW), (WX1, WY0, ZW)], RECESS, normal=(-1, 0, 0))
# window back, around the slot and the eject button hole
fq(WX0, SY1, WX1, WY1, RECESS, ZW)
fq(WX0, SY0, SX0, SY1, RECESS, ZW)
fq(SX1, SY0, WX1, SY1, RECESS, ZW)
fq(WX0, WY0, EX0, SY0, RECESS, ZW)
fq(EX1, WY0, WX1, SY0, RECESS, ZW)
fq(EX0, WY0, EX1, EY0, RECESS, ZW)
fq(EX0, EY1, EX1, SY0, RECESS, ZW)
# the bright sill line along the window's lower edge
m.decal_xy([(WX0, WY0 - 0.09), (WX1, WY0 - 0.09), (WX1, WY0), (WX0, WY0)], ZP, SILVER)
# the slot's upper flaps either side of the centre, and the finger notch
m.decal_xy([(SX0, SY1), (-1.72, SY1), (-1.72, WY1), (SX0, WY1)], ZW, BLOCK)
m.decal_xy([(0.75, SY1), (SX1, SY1), (SX1, WY1), (0.75, WY1)], ZW, BLOCK)
m.decal_xy([(-1.72, EY0), (0.75, EY0), (0.75, SY0), (-1.72, SY0)], ZW, NOTCH)

# ---------------------------------------------------------------- slot tunnel (faces point inwards)
m.polygon([(SX0, SY0, ZW), (SX1, SY0, ZW), (SX1, SY0, ZC), (SX0, SY0, ZC)], CAVITY, normal=(0, 1, 0))
m.polygon([(SX0, SY1, ZW), (SX1, SY1, ZW), (SX1, SY1, ZL), (SX0, SY1, ZL)], CAVITY, normal=(0, -1, 0))
m.polygon([(SX0, SY1, ZL), (SX1, SY1, ZL), (SX1, CY1, ZL), (SX0, CY1, ZL)], CAVITY, normal=(0, 0, -1))
m.polygon([(SX0, CY1, ZL), (SX1, CY1, ZL), (SX1, CY1, ZC), (SX0, CY1, ZC)], CAVITY, normal=(0, -1, 0))
wall = [(ZW, SY0), (ZC, SY0), (ZC, CY1), (ZL, CY1), (ZL, SY1), (ZW, SY1)]
m.polygon([(SX0, y, z) for z, y in wall], CAVITY, normal=(1, 0, 0))
m.polygon([(SX1, y, z) for z, y in wall], CAVITY, normal=(-1, 0, 0))
m.polygon([(SX0, SY0, ZC), (SX1, SY0, ZC), (SX1, CY1, ZC), (SX0, CY1, ZC)], CAVITY, normal=(0, 0, 1))

# ---------------------------------------------------------------- top and sides
m.decal_xz([(-HX, ZF - 1.45), (HX, ZF - 1.45), (HX, ZF - 1.32), (-HX, ZF - 1.32)], H, RED_DK)
LX0, LX1, LZ0, LZ1, T = -6.4, 6.4, ZB + 0.3, ZB + 9.0, 0.12     # battery lid outline
for q in ([(LX0, LZ0), (LX1, LZ0), (LX1, LZ0 + T), (LX0, LZ0 + T)],
          [(LX0, LZ1 - T), (LX1, LZ1 - T), (LX1, LZ1), (LX0, LZ1)],
          [(LX0, LZ0 + T), (LX0 + T, LZ0 + T), (LX0 + T, LZ1 - T), (LX0, LZ1 - T)],
          [(LX1 - T, LZ0 + T), (LX1, LZ0 + T), (LX1, LZ1 - T), (LX1 - T, LZ1 - T)]):
    m.decal_xz(q, H, RED_DK)
m.decal_xz([(-0.7, LZ1 - 1.6), (0.7, LZ1 - 1.6), (0, LZ1 - 2.5)], H, RED_DK)    # the OPEN arrow
for sx in (-1, 1):                                                              # side seam
    m.polygon([(sx * (HX + 0.02), k(3.40), ZB), (sx * (HX + 0.02), k(3.40), ZP - 0.15),
               (sx * (HX + 0.02), k(3.55), ZP - 0.15), (sx * (HX + 0.02), k(3.55), ZB)], RED_DK, normal=(sx, 0, 0))
m.polygon([(-HX, k(3.40), ZB - 0.02), (HX, k(3.40), ZB - 0.02), (HX, k(3.55), ZB - 0.02), (-HX, k(3.55), ZB - 0.02)],
          RED_DK, normal=(0, 0, -1))
# back: a port bay in the lower half between two corner feet
BX, BY, BZ = 6.3, 3.0, ZB + 0.6
m.polygon([(-HX, 0, ZB), (-BX, 0, ZB), (-BX, BY, ZB), (BX, BY, ZB), (BX, 0, ZB), (HX, 0, ZB),
           (HX, H, ZB), (-HX, H, ZB)], RED, normal=(0, 0, -1))
m.polygon([(-BX, 0, BZ), (BX, 0, BZ), (BX, BY, BZ), (-BX, BY, BZ)], RED_DK, normal=(0, 0, -1))
m.polygon([(-BX, BY, ZB), (BX, BY, ZB), (BX, BY, BZ), (-BX, BY, BZ)], RED_DK, normal=(0, -1, 0))
m.polygon([(-BX, 0.01, ZB), (BX, 0.01, ZB), (BX, 0.01, BZ), (-BX, 0.01, BZ)], RED_DK, normal=(0, 1, 0))   # bay floor
m.polygon([(-BX, 0, ZB), (-BX, BY, ZB), (-BX, BY, BZ), (-BX, 0, BZ)], RED, normal=(1, 0, 0))
m.polygon([(BX, 0, ZB), (BX, BY, ZB), (BX, BY, BZ), (BX, 0, BZ)], RED, normal=(-1, 0, 0))
# the RAM adapter cable socket and the power jack in the bay
m.polygon([(2.4, 1.0, BZ - 0.02), (4.8, 1.0, BZ - 0.02), (4.8, 2.2, BZ - 0.02), (2.4, 2.2, BZ - 0.02)],
          CAVITY, normal=(0, 0, -1))
m.polygon([(-4.6, 1.2, BZ - 0.02), (-3.8, 1.2, BZ - 0.02), (-3.8, 2.0, BZ - 0.02), (-4.6, 2.0, BZ - 0.02)],
          CAVITY, normal=(0, 0, -1))

# ---------------------------------------------------------------- moving parts
FZ = ZL - 0.06                 # flap hinge line: y FY, z FZ (system file)
FY = CY1 - 0.04
with m.part('flap'):
    m.box(SX0 + 0.05, SY0 + 0.05, FZ, SX1 - 0.05, FY, FZ + 0.05, FLAP)
with m.part('eject'):
    m.box(EX0, EY0, ZW - 0.5, EX1, EY1, ZW + 0.2, YELLOW)

if __name__ == '__main__':
    print(m.stats())
    print('flap pivot y %.3f z %.3f; seated card pos y %.3f z %.3f; tunnel end z %.3f' % (FY, FZ, SYC, ZW + GRIP_OUT, ZC))
    print(m.save())

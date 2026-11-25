# SPDX-License-Identifier: GPL-3.0-or-later
"""Super Nintendo cartridge (North American Game Pak), low-poly.

Standing upright like on a shelf: label facing +Z, connector edge at y = 0.
About 12 cm wide, 13.6 cm tall, 2 cm thick. Signature features: the boxy
grey shell with rounded top corners, the horizontal ridges across the top
front, the big recessed landscape label, the grip ribs on both sides, the
narrower connector lip at the bottom and the two locking notches on the
back edge.
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model

GREY = (150, 150, 158)        # shell
GREY_DK = (112, 112, 120)     # ridges, ribs
RECESS = (84, 84, 92)         # label recess frame, notches
SLOT = (34, 34, 38)           # connector opening
LABEL_BG = (232, 228, 214)    # label paper
LABEL_ART = (52, 92, 176)     # artwork block
LABEL_SKY = (236, 152, 48)    # artwork accent
LABEL_BAR = (196, 40, 44)     # coloured band

W2 = 6.0          # half width
ZF, ZB = 1.0, -1.0
H = 13.6
LIP = 0.7         # connector lip height

m = Model('snes', 'media')

# ---- main shell: rounded top corners seen from the front. The front face
# is built below from tiles around a real label recess, so leave it out here.
RX0, RX1, RY0, RY1 = -5.2, 5.2, 3.2, 10.9     # label recess
RD = 0.12                                     # recess depth
# rounded_rect runs top-right arc -> top-left arc -> ...; keep the two top arcs
top = [p for p in Model.rounded_rect(-W2, 0.0, W2, H, 1.1, segments=3) if p[1] > 2.0]
outline = [(-W2, LIP), (W2, LIP), (W2, RY0), (W2, RY1)] + top + [(-W2, RY1), (-W2, RY0)]
m.extrude_xy(outline, ZB, ZF, GREY, front=False)

# front tiles around the recess
m.polygon([(W2, RY1, ZF)] + [(x, y, ZF) for x, y in top] + [(-W2, RY1, ZF)], GREY, normal=(0, 0, 1))
m.quad((-W2, LIP, ZF), (W2, LIP, ZF), (W2, RY0, ZF), (-W2, RY0, ZF), GREY)
m.quad((-W2, RY0, ZF), (RX0, RY0, ZF), (RX0, RY1, ZF), (-W2, RY1, ZF), GREY)
m.quad((RX1, RY0, ZF), (W2, RY0, ZF), (W2, RY1, ZF), (RX1, RY1, ZF), GREY)
# recess walls (facing into the recess)
ZR = ZF - RD
m.quad((RX0, RY0, ZR), (RX0, RY0, ZF), (RX1, RY0, ZF), (RX1, RY0, ZR), GREY_DK)   # floor edge, faces +Y
m.quad((RX1, RY1, ZR), (RX1, RY1, ZF), (RX0, RY1, ZF), (RX0, RY1, ZR), GREY_DK)   # faces -Y
m.quad((RX0, RY1, ZR), (RX0, RY1, ZF), (RX0, RY0, ZF), (RX0, RY0, ZR), GREY_DK)   # faces +X
m.quad((RX1, RY0, ZR), (RX1, RY0, ZF), (RX1, RY1, ZF), (RX1, RY1, ZR), GREY_DK)   # faces -X

# ---- connector lip: a little narrower and thinner than the shell
m.box(-W2 + 0.35, 0.0, ZB + 0.25, W2 - 0.35, LIP, ZF - 0.25, GREY_DK,
      faces={'top': None, 'bottom': SLOT})
# the dark opening seen at the very bottom of the front and back
m.decal_xy([(-W2 + 0.8, 0.12), (W2 - 0.8, 0.12), (W2 - 0.8, 0.42), (-W2 + 0.8, 0.42)],
           ZF - 0.25, SLOT, lift=0.03)
m.polygon([(-W2 + 0.8, 0.12, ZB + 0.22), (W2 - 0.8, 0.12, ZB + 0.22),
           (W2 - 0.8, 0.42, ZB + 0.22), (-W2 + 0.8, 0.42, ZB + 0.22)], SLOT, normal=(0, 0, -1))

# ---- ridges across the top front (raised ribs)
for y in (11.55, 12.2, 12.85):
    m.box(-W2 + 1.0, y, ZF, W2 - 1.0, y + 0.32, ZF + 0.14, GREY_DK, faces={'back': None})

# ---- label: dark recess frame, paper, artwork, band. Every piece is its
# own tile of the recess floor (nothing overlaps), so no z-fighting.
def rect(x0, y0, x1, y1, col):
    m.quad((x0, y0, ZR), (x1, y0, ZR), (x1, y1, ZR), (x0, y1, ZR), col)


LX, LY0, LY1, FR = 4.95, 3.45, 10.65, 0.25
rect(-LX - FR, LY0 - FR, LX + FR, LY0, RECESS)          # frame: bottom
rect(-LX - FR, LY1, LX + FR, LY1 + FR, RECESS)          # top
rect(-LX - FR, LY0, -LX, LY1, RECESS)                   # left
rect(LX, LY0, LX + FR, LY1, RECESS)                     # right
AX = 4.6
rect(-LX, LY0, LX, 4.6, LABEL_BG)                       # paper below the art
rect(-LX, 4.6, -AX, 9.5, LABEL_BG)                      # paper margins
rect(AX, 4.6, LX, 9.5, LABEL_BG)
rect(-AX, 4.6, AX, 7.6, LABEL_ART)                      # artwork
rect(-AX, 7.6, AX, 9.5, LABEL_SKY)
rect(-LX, 9.5, LX, 9.8, LABEL_BG)
rect(-LX, 9.8, LX, 10.3, LABEL_BAR)                     # coloured band
rect(-LX, 10.3, LX, LY1, LABEL_BG)

# ---- grip ribs on both sides (upper half)
for y in (8.4, 9.2, 10.0, 10.8):
    m.box(W2, y, -0.7, W2 + 0.12, y + 0.35, 0.7, GREY_DK, faces={'left': None})
    m.box(-W2 - 0.12, y, -0.7, -W2, y + 0.35, 0.7, GREY_DK, faces={'right': None})

# ---- back: the two locking notches near the bottom edge
for sx in (-1, 1):
    x0, x1 = (W2 - 1.6, W2 - 0.3) if sx > 0 else (-W2 + 0.3, -W2 + 1.6)
    m.polygon([(x0, LIP + 0.2, ZB - 0.06), (x1, LIP + 0.2, ZB - 0.06),
               (x1, LIP + 1.6, ZB - 0.06), (x0, LIP + 1.6, ZB - 0.06)], RECESS, normal=(0, 0, -1))
# a plain label area on the back
m.polygon([(-3.5, 6.0, ZB - 0.06), (3.5, 6.0, ZB - 0.06), (3.5, 10.0, ZB - 0.06),
           (-3.5, 10.0, ZB - 0.06)], LABEL_BG, normal=(0, 0, -1))

if __name__ == '__main__':
    print(m.stats())
    print(m.save())

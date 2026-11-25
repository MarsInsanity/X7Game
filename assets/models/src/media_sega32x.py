# SPDX-License-Identifier: GPL-3.0-or-later
"""Sega 32X cartridge, low-poly.

Standing upright like on a shelf: label facing +Z, connector edge at y = 0.
About 11 cm wide, 15.5 cm tall, 2 cm thick (taller than a Genesis
cartridge). Signature features: the all-black shell, the thicker rounded
cap across the top with its sloped front, the big recessed front label
with the yellow top banner and red/black logo band over the artwork, the
grip ridges on the back of the cap, the shoulder notches on both sides and
the narrower connector tab at the bottom with the dark slot.
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model

BLACK = (40, 40, 44)          # shell
BLACK_HI = (70, 70, 78)       # cap, ridges (a touch lighter so the shapes read)
RECESS = (18, 18, 20)         # label recess frame, notches, slot
PCB = (40, 112, 56)           # contact board glimpsed in the slot
YELLOW = (248, 204, 24)       # label banner
RED = (216, 36, 36)           # logo band
LABEL_BK = (8, 8, 8)          # label black field
ART_A = (48, 96, 184)         # artwork block
ART_B = (232, 128, 40)        # artwork accent
WHITE = (228, 228, 220)       # back label

W2 = 5.5          # half width
ZF, ZB = 0.95, -0.95
H = 15.5
TAB = 0.9         # connector tab height
CAP0 = 12.6       # where the thicker top cap begins

m = Model('sega32x', 'media')

# ---- main shell below the cap: shoulder notches on both sides near the
# bottom, then the full width
NY0 = 1.8
outline = [(-W2 + 0.4, TAB), (W2 - 0.4, TAB),
           (W2 - 0.4, NY0), (W2, NY0 + 0.4), (W2, CAP0),
           (-W2, CAP0), (-W2, NY0 + 0.4), (-W2 + 0.4, NY0)]
m.extrude_xy(outline, ZB, ZF, BLACK)

# ---- the top cap: a bit thicker, sloped front, rounded-off top, seen from
# the side (z, y); extruded across the width with slightly chamfered ends
CZF, CZB = ZF + 0.25, ZB - 0.2
prof = [(CZB, CAP0), (CZF, CAP0), (CZF, CAP0 + 1.2), (CZF - 0.35, H - 0.35),
        (CZF - 0.85, H), (CZB + 0.45, H), (CZB, H - 0.4)]
m.extrude_yz(prof, -W2, W2, BLACK_HI, right=BLACK, left=BLACK)
# the cap's underside step on front and back (where it overhangs the shell)
m.polygon([(-W2, CAP0, ZF), (-W2, CAP0, CZF), (W2, CAP0, CZF), (W2, CAP0, ZF)],
          BLACK, normal=(0, -1, 0))
m.polygon([(-W2, CAP0, CZB), (-W2, CAP0, ZB), (W2, CAP0, ZB), (W2, CAP0, CZB)],
          BLACK, normal=(0, -1, 0))

# ---- connector tab at the bottom: narrower and thinner, dark slot
m.box(-W2 + 0.6, 0.0, ZB + 0.2, W2 - 0.6, TAB, ZF - 0.2, BLACK,
      faces={'top': None, 'bottom': RECESS})
m.decal_xy([(-W2 + 1.0, 0.1), (W2 - 1.0, 0.1), (W2 - 1.0, 0.55), (-W2 + 1.0, 0.55)],
           ZF - 0.2, PCB, lift=0.05)
m.polygon([(-W2 + 1.0, 0.1, ZB + 0.15), (W2 - 1.0, 0.1, ZB + 0.15),
           (W2 - 1.0, 0.55, ZB + 0.15), (-W2 + 1.0, 0.55, ZB + 0.15)], PCB, normal=(0, 0, -1))


# ---- front label: recess frame then tiles (no overlapping decals)
def rect(x0, y0, x1, y1, col, lift=0.1):
    m.decal_xy([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], ZF, col, lift=lift)


LX, LY0, LY1, FR = 4.6, 2.2, 12.2, 0.3
rect(-LX - FR, LY0 - FR, LX + FR, LY0, RECESS)
rect(-LX - FR, LY1, LX + FR, LY1 + FR, RECESS)
rect(-LX - FR, LY0, -LX, LY1, RECESS)
rect(LX, LY0, LX + FR, LY1, RECESS)
AX = 4.2
rect(-LX, LY0, LX, 2.8, YELLOW)                 # thin yellow foot strip
rect(-LX, 2.8, LX, 3.3, LABEL_BK)
rect(-LX, 3.3, -AX, 8.4, LABEL_BK)              # black margins round the art
rect(AX, 3.3, LX, 8.4, LABEL_BK)
rect(-AX, 3.3, AX, 6.6, ART_A)                  # artwork
rect(-AX, 6.6, AX, 8.4, ART_B)
rect(-LX, 8.4, LX, 8.9, LABEL_BK)
rect(-LX, 8.9, LX, 9.6, RED)                    # logo band
rect(-LX, 9.6, LX, 10.0, LABEL_BK)
rect(-LX, 10.0, LX, LY1, YELLOW)                # yellow top banner

# ---- grip ridges across the back of the cap
for y in (CAP0 + 0.3, CAP0 + 0.85, CAP0 + 1.4, CAP0 + 1.95):
    m.box(-W2 + 0.8, y, CZB - 0.12, W2 - 0.8, y + 0.3, CZB, BLACK_HI,
          faces={'front': None})

# ---- back: plain white sticker
m.polygon([(-3.6, 5.0, ZB - 0.08), (3.6, 5.0, ZB - 0.08), (3.6, 10.0, ZB - 0.08),
           (-3.6, 10.0, ZB - 0.08)], WHITE, normal=(0, 0, -1))

if __name__ == '__main__':
    print(m.stats())
    print(m.save())

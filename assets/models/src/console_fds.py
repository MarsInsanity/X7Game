# SPDX-License-Identifier: GPL-3.0-or-later
"""Famicom Disk System drive (HVC-022): a squat maroon box with a black
front bezel holding the horizontal disk slot, the eject button and the red
access lamp; the grey RAM adapter cable leaves from the back."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model

MAROON = (128, 28, 36)
MAROON_DK = (84, 16, 22)
MAROON_LT = (158, 48, 54)
BEZEL = (34, 32, 36)
SLOT = (4, 4, 6)
FLAP = (66, 64, 70)
EJECT = (84, 82, 90)
LAMP = (255, 32, 24)
CABLE = (150, 150, 156)
PLUG = (110, 110, 118)

W, H, D = 15.0, 7.0, 23.0
HX = W / 2
ZB, ZF = -D / 2, D / 2          # back, front of the whole unit
ZBODY = ZF - 1.2                # front face of the maroon shell

m = Model('fds', 'console')

# maroon shell, chamfered top edges seen from the front
shell = [(-HX, 0), (HX, 0), (HX, H - 0.9), (HX - 0.9, H), (-HX + 0.9, H), (-HX, H - 0.9)]
m.extrude_xy(shell, ZB, ZBODY, MAROON, front=False)
# shell front face behind the bezel (closes the solid)
m.polygon([(x, y, ZBODY) for x, y in shell], MAROON, normal=(0, 0, 1))

# black front bezel: a plate standing proud of the shell, its front face
# built in four pieces around the horizontal disk slot
SX0, SX1, SY0, SY1 = -4.8, 4.8, 3.7, 4.9      # slot opening
SD = 1.0                                       # slot recess depth
bz = [(-HX + 0.25, 0.25), (HX - 0.25, 0.25), (HX - 0.25, H - 1.0),
      (HX - 1.0, H - 0.25), (-HX + 1.0, H - 0.25), (-HX + 0.25, H - 1.0)]
m.extrude_xy(bz, ZBODY, ZF, BEZEL, front=False, back=False)
L, R, B, T = -HX + 0.25, HX - 0.25, 0.25, H - 0.25
m.polygon([(L, B, ZF), (SX0, B, ZF), (SX0, T, ZF), (-HX + 1.0, T, ZF), (L, H - 1.0, ZF)], BEZEL, normal=(0, 0, 1))
m.polygon([(SX1, B, ZF), (R, B, ZF), (R, H - 1.0, ZF), (HX - 1.0, T, ZF), (SX1, T, ZF)], BEZEL, normal=(0, 0, 1))
m.quad((SX0, B, ZF), (SX1, B, ZF), (SX1, SY0, ZF), (SX0, SY0, ZF), BEZEL)
m.quad((SX0, SY1, ZF), (SX1, SY1, ZF), (SX1, T, ZF), (SX0, T, ZF), BEZEL)
# the slot recess: walls and a black flap at the back of it
m.quad((SX0, SY0, ZF), (SX1, SY0, ZF), (SX1, SY0, ZF - SD), (SX0, SY0, ZF - SD), FLAP)     # floor (faces up)
m.quad((SX0, SY1, ZF - SD), (SX1, SY1, ZF - SD), (SX1, SY1, ZF), (SX0, SY1, ZF), SLOT)     # ceiling (faces down)
m.quad((SX0, SY0, ZF - SD), (SX0, SY1, ZF - SD), (SX0, SY1, ZF), (SX0, SY0, ZF), SLOT)     # left wall (faces +x)
m.quad((SX1, SY0, ZF), (SX1, SY1, ZF), (SX1, SY1, ZF - SD), (SX1, SY0, ZF - SD), SLOT)     # right wall (faces -x)
m.quad((SX0, SY0, ZF - SD), (SX1, SY0, ZF - SD), (SX1, SY1, ZF - SD), (SX0, SY1, ZF - SD), SLOT)  # back
# a lighter lip below the slot (the disk guide)
m.box(SX0 - 0.3, SY0 - 0.35, ZF, SX1 + 0.3, SY0, ZF + 0.2, FLAP, faces={'back': None})

# eject button: chunky grey button at the lower right of the bezel
m.box(2.4, 1.0, ZF, 5.6, 2.3, ZF + 0.45, EJECT, faces={'back': None})
# red access lamp at the lower left
m.box(-5.4, 1.45, ZF, -4.5, 1.85, ZF + 0.2, LAMP, faces={'back': None})

# top: a slightly raised lighter maroon panel (the label plate) and a
# moulded groove line near the front
m.decal_xz([(-5.5, -9.0), (5.5, -9.0), (5.5, 4.5), (-5.5, 4.5)], H, MAROON_LT, lift=0.03)
m.decal_xz([(-HX + 0.9, 7.0), (HX - 0.9, 7.0), (HX - 0.9, 7.35), (-HX + 0.9, 7.35)], H, MAROON_DK, lift=0.03)
# side parting line
for sx in (-1, 1):
    zs = [(ZB + 0.4, 2.7), (ZBODY - 0.2, 2.7), (ZBODY - 0.2, 3.0), (ZB + 0.4, 3.0)]
    pts = [(sx * (HX + 0.03), y, z) for z, y in zs]
    m.polygon(pts, MAROON_DK, normal=(sx, 0, 0))

# back: the RAM adapter cable with its strain relief, running down to the
# table and off to the left
CX, CY = -4.5, 2.2
m.box(CX - 0.9, CY - 0.7, ZB - 0.8, CX + 0.9, CY + 0.7, ZB, PLUG, faces={'front': None})
m.cylinder_z(CX, CY, 0.35, ZB - 2.2, ZB - 0.8, CABLE, segments=6, front=False)
# cable drops to the table and runs off to the left, then forward
T2 = 0.32
m.box(CX - T2, 0.0, ZB - 2.2 - 2 * T2, CX + T2, CY + T2, ZB - 2.2, CABLE)
m.box(-HX - 1.6, 0.0, ZB - 2.2 - 2 * T2, CX - T2, 2 * T2, ZB - 2.2, CABLE, faces={'right': None})
m.box(-HX - 1.6, 0.0, ZB - 2.2, -HX - 1.6 + 2 * T2, 2 * T2, ZB + 3.0, CABLE, faces={'back': None})

if __name__ == '__main__':
    print(m.stats())
    print(m.save())

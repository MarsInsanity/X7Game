# SPDX-License-Identifier: GPL-3.0-or-later
"""Neo Geo Pocket Color cartridge: the small light-grey (silver) card-like
cartridge with a rounded top and a ridged grip band (the monochrome Neo Geo
Pocket's carts are black), standing upright, label to +Z, contacts edge at
y = 0."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model

SHELL = (178, 182, 194)     # light silver-grey shell
EDGE = (132, 136, 150)      # side / top faces, so the outline reads
EMBOSS = (220, 224, 234)    # raised grip ribs and insert arrow
LABEL = (244, 242, 236)     # white label border
SKY = (40, 64, 168)         # picture area
GROUND = (240, 128, 32)     # picture lower part
BAND = (208, 32, 48)        # title band across the top of the label
ACC1 = (248, 208, 32)       # colour-logo accent stripes
ACC2 = (48, 176, 88)
PCB = (24, 96, 48)
GOLD = (216, 176, 64)

W, H = 4.4, 4.8
hw = W / 2
R = 0.5                     # rounded top corners
ZF, ZB, ZM = 0.28, -0.36, -0.12   # recessed label face, back, back of the front shell
ZR = 0.36                   # raised frame around the label
CX = 1.75                   # half width of the contacts opening on the back
CY = 0.6                    # height of the contacts opening
LX, LY0, LY1 = 1.85, 0.45, 3.75   # label recess
GY = 3.95                   # grip band starts here (front and back)

m = Model('ngpc', 'media')


def face(pts, z, color, nz=1):
    """flat face at depth z facing +Z (nz = 1) or -Z (nz = -1)"""
    return m.polygon([(x, y, z) for x, y in pts], color, normal=(0, 0, nz))


def top_arc(y0):
    """the rounded top edge, right to left, from height y0 up"""
    pts = Model.rounded_rect(-hw, y0 - 2 * R, hw, H, R, segments=2)
    return pts[:6]          # the two top corners (right, then left)


# front half of the shell, up to the raised frame (front faces built below)
front = [(-hw, 0), (-CX, 0), (CX, 0), (hw, 0)] + top_arc(GY)
m.extrude_xy(front, ZM, ZR, SHELL, front=False, back=False, side=EDGE)
# back half: same outline with the contacts opening at the bottom
back = [(-hw, 0), (-CX, 0), (-CX, CY), (CX, CY), (CX, 0), (hw, 0)] + top_arc(GY)
m.extrude_xy(back, ZB, ZM, SHELL, front=False, side=EDGE)
# circuit board face in the opening, with gold contacts
face([(CX, 0), (-CX, 0), (-CX, CY), (CX, CY)], ZM, PCB, -1)
n = 6
pitch = (2 * CX - 0.3) / n
for i in range(n):
    x0 = CX - 0.15 - i * pitch - 0.06
    x1 = x0 - pitch + 0.16
    face([(x0, 0.04), (x1, 0.04), (x1, CY - 0.15), (x0, CY - 0.15)], ZM - 0.03, GOLD, -1)

# raised frame around the recessed label (its outer sides are the shell's):
# top part (rounded) with the grip band, bottom strip, two side strips, and the
# step faces down into the recess
face([(-hw, LY1), (hw, LY1)] + top_arc(GY), ZR, SHELL)
face([(-hw, 0), (-CX, 0), (CX, 0), (hw, 0), (hw, LY0), (LX, LY0), (-LX, LY0), (-hw, LY0)], ZR, SHELL)
face([(-hw, LY0), (-LX, LY0), (-LX, LY1), (-hw, LY1)], ZR, SHELL)
face([(LX, LY0), (hw, LY0), (hw, LY1), (LX, LY1)], ZR, SHELL)
m.quad((-LX, LY1, ZF), (LX, LY1, ZF), (LX, LY1, ZR), (-LX, LY1, ZR), EDGE)    # faces down
m.quad((LX, LY0, ZF), (-LX, LY0, ZF), (-LX, LY0, ZR), (LX, LY0, ZR), EDGE)    # faces up
m.quad((-LX, LY0, ZF), (-LX, LY1, ZF), (-LX, LY1, ZR), (-LX, LY0, ZR), EDGE)  # faces +x
m.quad((LX, LY1, ZF), (LX, LY0, ZF), (LX, LY0, ZR), (LX, LY1, ZR), EDGE)      # faces -x

# front grip band: two raised ribs left and right of an insert arrow
for i in range(2):
    y = 4.05 + i * 0.28
    m.box(-1.6, y, ZR, -0.45, y + 0.12, ZR + 0.05, EMBOSS, faces={'back': None, 'bottom': None})
    m.box(0.45, y, ZR, 1.6, y + 0.12, ZR + 0.05, EMBOSS, faces={'back': None, 'bottom': None})
m.extrude_xy([(-0.28, 4.48), (0.28, 4.48), (0.0, 4.02)], ZR, ZR + 0.05, EMBOSS, back=False)

# label filling the recess as full-width bands with thin white side margins
# (tiled, no decal stacked on a big face; shared edge points, no T-junctions)
ax0, ax1 = -LX + 0.15, LX - 0.15
y0, gy, sy, ty, ey = LY0 + 0.1, 0.78, 1.35, 3.0, LY1 - 0.1
q = (ax1 - ax0) / 4
xs = [ax0 + k * q for k in range(5)]
face([(-LX, LY0), (LX, LY0), (LX, y0)] + [(x, y0) for x in reversed(xs)] + [(-LX, y0)], ZF, LABEL)
face([(-LX, ey)] + [(x, ey) for x in (ax0, ax1)] + [(LX, ey), (LX, LY1), (-LX, LY1)], ZF, LABEL)
face([(-LX, y0), (ax0, y0), (ax0, gy), (ax0, sy), (ax0, ty), (ax0, ey), (-LX, ey)], ZF, LABEL)
face([(ax1, y0), (LX, y0), (LX, ey), (ax1, ey), (ax1, ty), (ax1, sy), (ax1, gy)], ZF, LABEL)
# four-colour strip along the bottom (the "Color" idea): red, yellow, green, blue
for k, c in enumerate((BAND, ACC1, ACC2, SKY)):
    face([(xs[k], y0), (xs[k + 1], y0), (xs[k + 1], gy), (xs[k], gy)], ZF, c)
face([(x, gy) for x in xs] + [(ax1, sy), (ax0, sy)], ZF, GROUND)
face([(ax0, sy), (ax1, sy), (ax1, ty), (ax0, ty)], ZF, SKY)
face([(ax0, ty), (ax1, ty), (ax1, ey), (ax0, ey)], ZF, BAND)
# a white title block in the band and a small sun in the picture (thin raised parts)
m.box(-1.2, 3.2, ZF, 0.6, 3.48, ZF + 0.03, LABEL, faces={'back': None, 'bottom': None})
m.cylinder_z(0.95, 2.35, 0.32, ZF, ZF + 0.03, ACC1, segments=8, back=False)
# a hill on the horizon
m.extrude_xy([(-1.7, sy), (0.2, sy), (-0.6, 2.05)], ZF, ZF + 0.03, ACC2, back=False, side=False)

# back: grip ribs across the top band
for i in range(3):
    y = 4.0 + i * 0.26
    m.box(-1.5, y, ZB - 0.05, 1.5, y + 0.12, ZB, EDGE, faces={'front': None, 'bottom': None})

print(m.stats())
print(m.save())

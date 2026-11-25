# SPDX-License-Identifier: GPL-3.0-or-later
"""Sega SG-1000 cartridge: a squat, landscape black cartridge standing upright,
label to +Z, edge connector at y = 0. Signature details: glossy black shell,
a thicker capped top edge with a chamfered front, a big framed label (header
band + picture + stripe), grip ridges on the cap, exposed board at the bottom."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model

SHELL = (36, 36, 42)        # black plastic
CAP = (58, 58, 66)          # top cap (slightly lighter so it reads)
RIDGE = (104, 104, 112)       # grip ridges
FRAME = (226, 226, 230)     # white label frame
HEAD = (208, 32, 40)        # red header band
LOGO = (250, 250, 250)      # plain white box in the header
SKY = (56, 120, 216)        # picture: sky
GROUND = (48, 168, 72)      # picture: ground
SUN = (248, 168, 40)        # picture accent
STRIPE = (240, 208, 40)     # yellow stripe under the picture
STICK = (150, 150, 156)     # back sticker
PCB = (32, 104, 56)
GOLD = (216, 176, 64)

W, H = 10.6, 8.2
hw = W / 2
ZF, ZB = 0.85, -0.85        # main shell front / back
CY = 6.8                    # bottom of the top cap
CZ = 1.0                    # cap half depth (sticks out 0.15 front and back)
NX, NY = 4.2, 0.6           # connector notch half width / height
lx, ly0, ly1 = 4.75, 0.95, 6.55     # label on the front
sx0, sy0, sx1, sy1 = -3.6, 1.6, 3.6, 5.6   # sticker on the back

m = Model('sg1000', 'media')


def face(pts, z, color, nz):
    return m.polygon([(x, y, z) for x, y in pts], color, normal=(0, 0, nz))


def rect(x0, y0, x1, y1, z, color, nz=1):
    return face([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], z, color, nz)


# ---- main shell (below the cap), connector notch cut into the bottom
outline = [(-hw, 0), (-NX, 0), (-NX, NY), (NX, NY), (NX, 0), (hw, 0), (hw, CY), (-hw, CY)]
m.extrude_xy(outline, ZB, ZF, SHELL, front=False, back=False, side=SHELL)
# front tiled around the label
face([(-hw, 0), (-NX, 0), (-NX, NY), (NX, NY), (NX, 0), (hw, 0), (hw, ly0), (-hw, ly0)], ZF, SHELL, 1)
rect(-hw, ly1, hw, CY, ZF, SHELL)
rect(-hw, ly0, -lx, ly1, ZF, SHELL)
rect(lx, ly0, hw, ly1, ZF, SHELL)
# back tiled around the sticker
face([(-hw, 0), (-NX, 0), (-NX, NY), (NX, NY), (NX, 0), (hw, 0), (hw, sy0), (-hw, sy0)], ZB, SHELL, -1)
rect(-hw, sy1, hw, CY, ZB, SHELL, -1)
rect(-hw, sy0, sx0, sy1, ZB, SHELL, -1)
rect(sx1, sy0, hw, sy1, ZB, SHELL, -1)
rect(sx0, sy0, sx1, sy1, ZB, STICK, -1)

# ---- top cap: thicker, chamfered along the top front and back edges
prof = [(-CZ, CY), (CZ, CY), (CZ, 7.7), (CZ - 0.35, H), (-CZ + 0.35, H), (-CZ, 7.7)]
m.extrude_yz(prof, -hw, hw, CAP)
# grip ridges along the cap front
for i in range(3):
    y = 7.0 + i * 0.22
    m.box(-hw + 0.5, y, CZ, hw - 0.5, y + 0.1, CZ + 0.08, RIDGE, faces={'back': None})

# ---- circuit board in the notch, gold contacts on its front
m.box(-NX + 0.05, 0.0, -0.1, NX - 0.05, NY, 0.1, PCB, faces={'top': None})
m.decal_xy([(-NX + 0.35, 0.06), (NX - 0.35, 0.06), (NX - 0.35, NY - 0.1), (-NX + 0.35, NY - 0.1)], 0.1, GOLD)

# ---- label: thin raised slab, its face tiled into frame + design pieces
ZL = ZF + 0.06
m.box(-lx, ly0, ZF, lx, ly1, ZL, FRAME, faces={'back': None, 'front': None})
f = 0.25
ix = lx - f
iy0, iy1 = ly0 + f, ly1 - f
st1 = iy0 + 0.45            # yellow stripe top
gr1 = st1 + 1.2             # ground top
sk1 = iy1 - 1.35            # sky top (a white gap, then the header)
hd0 = sk1 + 0.2             # header bottom
rect(-lx, ly0, lx, iy0, ZL, FRAME)
rect(-lx, iy1, lx, ly1, ZL, FRAME)
rect(-lx, iy0, -ix, iy1, ZL, FRAME)
rect(ix, iy0, lx, iy1, ZL, FRAME)
rect(-ix, iy0, ix, st1, ZL, STRIPE)
# rolling hills against the sky, a sun in the upper right
hills = [(ix, gr1 - 0.3), (ix - 1.6, gr1 + 0.35), (ix - 3.4, gr1 - 0.25), (ix - 5.6, gr1 + 0.75),
         (-ix + 1.5, gr1 - 0.1), (-ix, gr1 + 0.4)]
ux0, ux1, uy0, uy1 = ix - 2.0, ix - 1.0, sk1 - 1.1, sk1 - 0.3
face([(-ix, st1), (ix, st1)] + hills, ZL, GROUND, 1)
face(hills[::-1] + [(ix, uy0), (-ix, uy0)], ZL, SKY, 1)
rect(-ix, uy1, ix, sk1, ZL, SKY)
rect(-ix, uy0, ux0, uy1, ZL, SKY)
rect(ux1, uy0, ix, uy1, ZL, SKY)
rect(ux0, uy0, ux1, uy1, ZL, SUN)
rect(-ix, sk1, ix, hd0, ZL, FRAME)
# red header with a plain white box on the left
bx0, bx1, by0, by1 = -ix + 0.3, -ix + 2.4, hd0 + 0.22, iy1 - 0.22
rect(-ix, hd0, ix, by0, ZL, HEAD)
rect(-ix, by1, ix, iy1, ZL, HEAD)
rect(-ix, by0, bx0, by1, ZL, HEAD)
rect(bx1, by0, ix, by1, ZL, HEAD)
rect(bx0, by0, bx1, by1, ZL, LOGO)

print(m.stats())
print(m.save())

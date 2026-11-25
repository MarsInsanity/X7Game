# SPDX-License-Identifier: GPL-3.0-or-later
"""Super Nintendo Entertainment System (North American model), low poly.

Built from photos of the real console (Wikimedia Commons: Nintendo-Super-
NES-Console-FL/FR/BL). 20.0 wide x 24.2 deep x 7.2 tall, light grey.

  * the tall rear block: flat top, its outer shoulders curve down at the
    front onto the lower front section; vents and ports on its back
  * the cartridge housing in the middle of it: a slightly raised plate with
    the slot (two dust flaps), its slanted front is the logo face
  * the front section: two long modules (power left, reset right) with the
    purple sliders at their back ends and the controller ports on their
    fronts, which stand out of the front; between them the recessed
    channel with the grey eject lever; plain end blocks left and right
    (power LED on the left one)
  * an inset, vertically ribbed base all round

Moving parts: 'flap_front' and 'flap_back', the two dust flaps in the slot,
hinged on the slot's long edges; they swing down into the slot when a
cartridge goes in (assets/models/systems/snes.json).

Slot: the cartridge (13.0 x 2.0 cm, label to +Z) goes straight down,
centred on x = 0, z = SLOT_Z; its lower SEAT cm go in.
"""
import math
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model  # noqa: E402

BODY = (210, 210, 216)      # light grey shell
FLAP = (190, 190, 198)      # dust flaps, a little darker than the shell
LEVER = (178, 178, 186)     # eject lever
SEAM = (140, 140, 150)      # parting lines between the blocks
BASE = (186, 186, 194)      # inset ribbed base
RIB = (128, 128, 138)       # base ribs, back vents
PURPLE = (124, 96, 212)     # power / reset sliders
PURPLE_D = (96, 70, 180)    # slider grooves
PORT = (200, 200, 206)      # controller port faces
PORT_RIM = (70, 70, 80)     # dark rim round the ports
HOLE = (26, 26, 32)         # pin holes, slot cavity, back sockets
LED = (160, 30, 30)

m = Model('snes', 'console')

# ------------------------------------------------------------ dimensions
W2 = 10.0                   # half width
ZB = -10.2                  # back
ZE = 9.2                   # front of the end blocks and the channel
ZF = 10.2                   # front of the port modules
HB = 1.25                    # top of the inset base
INS = 0.45                  # base inset
HR = 6.75                  # rear block top
HP = 7.2                    # cartridge housing top
HF = 5.3                    # front section top
HC = 4.8                    # eject channel floor
PX = 7.6                    # half width of the cartridge housing
PZ0 = -2.9                  # back of the housing
ZL0, ZL1 = 1.2, 2.5       # logo face: top edge, bottom edge
ZS, ZSL = -3.0, 5.4         # shoulders: where they start to curve down, how long
CX = 1.4                    # half width of the eject channel
MX = 6.4                    # outer edge of the port modules
CF = 0.7                    # rounding of the top front edges
CB = 1.3                    # rounding of the top back edge

# slot: fits the cartridge (x -6.5..6.5, z -1.0..1.0 around its centre)
SLOT_Z = -0.85
SX = 6.65                   # half width of the opening (0.15 clearance)
SZ = 1.25                   # half depth (0.1 clearance + room for the open flaps)
SEAT = 4.2                  # how far the cartridge goes in
FLOOR = HP - SEAT - 0.05    # cavity floor
FT = 0.15                   # flap thickness


C45 = 1 - math.sqrt(0.5)
BACK_TOP = [(ZB + CB, HR), (ZB + CB * C45, HR - CB * C45), (ZB, HR - CB)]


def front_top(z):
    return [(z, HF - CF), (z - CF * C45, HF - CF * C45), (z - CF, HF)]


def mirror(f):
    for side in (-1, 1):
        f(side)


# ------------------------------------------------------------ base
m.prism([(-W2 + INS, ZB + INS), (W2 - INS, ZB + INS), (W2 - INS, ZE - INS), (MX - INS, ZE - INS),
         (MX - INS, ZF - INS), (CX + INS, ZF - INS), (CX + INS, ZE - INS), (-CX - INS, ZE - INS),
         (-CX - INS, ZF - INS), (-MX + INS, ZF - INS), (-MX + INS, ZE - INS), (-W2 + INS, ZE - INS)],
        0.0, HB, BASE, top=False)
RW = 0.12
for k in range(-12, 13):                       # ribs: front (modules, channel, end blocks)
    x = k * 0.78
    if abs(x) > W2 - INS - 0.3 or min(abs(abs(x) - (MX - INS)), abs(abs(x) - (CX + INS))) < 0.25:
        continue
    z = ZF - INS if CX + INS < abs(x) < MX - INS else ZE - INS
    m.decal_xy([(x - RW, 0.12), (x + RW, 0.12), (x + RW, HB - 0.08), (x - RW, HB - 0.08)], z, RIB, lift=0.03)
for side in (-1, 1):                           # ribs: sides
    xs = side * (W2 - INS + 0.03)
    for k in range(14):
        z = ZB + INS + 0.7 + k * (ZE - ZB - 2 * INS - 1.4) / 13
        a, b = z - RW, z + RW
        m.polygon([(xs, 0.12, a), (xs, 0.12, b), (xs, HB - 0.08, b), (xs, HB - 0.08, a)], RIB, normal=(side, 0, 0))
for k in range(16):                            # ribs: back
    x = -W2 + INS + 0.6 + k * (2 * W2 - 2 * INS - 1.2) / 15
    m.polygon([(x + RW, 0.12, ZB + INS - 0.03), (x - RW, 0.12, ZB + INS - 0.03), (x - RW, HB - 0.08, ZB + INS - 0.03),
               (x + RW, HB - 0.08, ZB + INS - 0.03)], RIB, normal=(0, 0, -1))
# the body's underside around the base
m.polygon([(-W2, HB, ZB), (W2, HB, ZB), (W2, HB, ZE), (-W2, HB, ZE)], BODY, normal=(0, -1, 0))
for xa, xb in ((-MX, -CX), (CX, MX)):
    m.polygon([(xa, HB, ZE), (xb, HB, ZE), (xb, HB, ZF), (xa, HB, ZF)], BODY, normal=(0, -1, 0))

# ------------------------------------------------------------ outer strips (shoulders + end blocks)
arc = [(ZS + ZSL * math.sin(math.radians(a)), HF + (HR - HF) * math.cos(math.radians(a))) for a in (0, 30, 60, 90)]
outer = [(ZB, HB), (ZE, HB)] + front_top(ZE) + arc[::-1] + BACK_TOP
m.extrude_yz(outer, -W2, -PX, BODY)
m.extrude_yz(outer, PX, W2, BODY)

# ------------------------------------------------------------ rear piece behind the housing
m.extrude_yz([(ZB, HB), (PZ0, HB), (PZ0, HR)] + BACK_TOP, -PX, PX, BODY,
             right=False, left=False)

# ------------------------------------------------------------ cartridge housing with the slot
z0, z1 = SLOT_Z - SZ, SLOT_Z + SZ
m.polygon([(-PX, HP, PZ0), (PX, HP, PZ0), (PX, HP, z0), (-PX, HP, z0)], BODY, normal=(0, 1, 0))
m.polygon([(-PX, HP, z1), (PX, HP, z1), (PX, HP, ZL0), (-PX, HP, ZL0)], BODY, normal=(0, 1, 0))
m.polygon([(-PX, HP, z0), (-SX, HP, z0), (-SX, HP, z1), (-PX, HP, z1)], BODY, normal=(0, 1, 0))
m.polygon([(SX, HP, z0), (PX, HP, z0), (PX, HP, z1), (SX, HP, z1)], BODY, normal=(0, 1, 0))
m.polygon([(PX, HR, PZ0), (-PX, HR, PZ0), (-PX, HP, PZ0), (PX, HP, PZ0)], BODY, normal=(0, 0, -1))
m.polygon([(-PX, HB, PZ0), (-PX, HB, ZL0), (-PX, HP, ZL0), (-PX, HP, PZ0)], BODY, normal=(-1, 0, 0))
m.polygon([(PX, HB, PZ0), (PX, HB, ZL0), (PX, HP, ZL0), (PX, HP, PZ0)], BODY, normal=(1, 0, 0))
# the cavity: dark walls and floor
m.polygon([(SX, FLOOR, z1), (-SX, FLOOR, z1), (-SX, HP, z1), (SX, HP, z1)], HOLE, normal=(0, 0, -1))
m.polygon([(-SX, FLOOR, z0), (SX, FLOOR, z0), (SX, HP, z0), (-SX, HP, z0)], HOLE, normal=(0, 0, 1))
m.polygon([(-SX, FLOOR, z0), (-SX, FLOOR, z1), (-SX, HP, z1), (-SX, HP, z0)], HOLE, normal=(1, 0, 0))
m.polygon([(SX, FLOOR, z1), (SX, FLOOR, z0), (SX, HP, z0), (SX, HP, z1)], HOLE, normal=(-1, 0, 0))
m.polygon([(-SX, FLOOR, z0), (SX, FLOOR, z0), (SX, FLOOR, z1), (-SX, FLOOR, z1)], HOLE, normal=(0, 1, 0))
# the dust flaps, closed: flush with the housing top, meeting in the middle
FG = 0.03
with m.part('flap_front'):
    m.box(-SX + 0.05, HP - FT, SLOT_Z + FG, SX - 0.05, HP, z1, FLAP)
with m.part('flap_back'):
    m.box(-SX + 0.05, HP - FT, z0, SX - 0.05, HP, SLOT_Z - FG, FLAP)

# ------------------------------------------------------------ front section (from the logo face on)
inner = [(ZL0, HB), (ZE, HB)] + front_top(ZE) + [(ZL1, HF), (ZL0, HP)]
module = [(ZL0, HB), (ZF, HB)] + front_top(ZF) + [(ZL1, HF), (ZL0, HP)]
zc = ZL0 + (HC - HP) * (ZL1 - ZL0) / (HF - HP)          # logo slope meets the channel floor
channel = [(ZL0, HB), (ZE, HB), (ZE, HC), (zc, HC), (ZL0, HP)]
m.extrude_yz(inner, -PX, -MX, BODY, right=False)
m.extrude_yz(inner, MX, PX, BODY, left=False)
m.extrude_yz(module, -MX, -CX, BODY)
m.extrude_yz(module, CX, MX, BODY)
m.extrude_yz(channel, -CX, CX, BODY, right=False, left=False)

# eject lever: a flat plate at the back of the channel
m.box(-CX + 0.12, HC, zc + 0.05, CX - 0.12, HC + 0.15, zc + 4.4, LEVER, faces={'bottom': None})


def front_details(side):
    xa, xb = sorted((side * CX, side * MX))
    # seams on the top between module and end block
    xg = side * MX
    m.decal_xz([(xg - 0.05, ZL1), (xg + 0.05, ZL1), (xg + 0.05, ZE - CF), (xg - 0.05, ZE - CF)], HF, SEAM)
    # slider at the back of the module, with its long groove
    sx0, sx1 = xa + 0.3, xb - 0.3
    m.box(sx0, HF, ZL1 + 0.05, sx1, HF + 0.3, ZL1 + 1.75, PURPLE, faces={'bottom': None})
    m.decal_xz([(sx0 + 0.45, ZL1 + 0.55), (sx1 - 0.45, ZL1 + 0.55), (sx1 - 0.45, ZL1 + 1.25),
                (sx0 + 0.45, ZL1 + 1.25)], HF + 0.3, PURPLE_D)
    # controller port: a pill with one flat end (round end towards the middle)
    cxp = (xa + xb) / 2
    py0, py1 = 2.1, 3.3

    def pill(x0, x1, y0, y1):
        r = (y1 - y0) / 2
        pts = [(x0, y0), (x1 - r * 0.6, y0), (x1, y0 + r * 0.7), (x1, y1 - r * 0.7), (x1 - r * 0.6, y1), (x0, y1)]
        return [(2 * cxp - x, y) for x, y in pts] if side > 0 else pts
    m.decal_xy(pill(cxp - 1.9, cxp + 1.9, py0, py1), ZF, PORT_RIM, lift=0.02)
    m.decal_xy(pill(cxp - 1.75, cxp + 1.75, py0 + 0.13, py1 - 0.13), ZF, PORT, lift=0.04)
    for gx0, gx1 in ((-1.5, -0.12), (0.12, 1.35)):
        gx0, gx1 = sorted((side * -gx0, side * -gx1)) if side > 0 else (gx0, gx1)
        m.decal_xy([(cxp + gx0, 2.55), (cxp + gx1, 2.55), (cxp + gx1, 2.85), (cxp + gx0, 2.85)], ZF, HOLE,
                   lift=0.06)
    # step line above the port on the module front
    m.decal_xy([(xa + 0.05, 3.75), (xb - 0.05, 3.75), (xb - 0.05, 3.83), (xa + 0.05, 3.83)], ZF, SEAM)


mirror(front_details)
# seam lines round the sides (above the base)
for side in (-1, 1):
    xs = side * (W2 + 0.02)
    a, b = (ZB + 0.1, ZE - 0.1)
    m.polygon([(xs, 1.55, a), (xs, 1.55, b), (xs, 1.65, b), (xs, 1.65, a)], SEAM, normal=(side, 0, 0))
# power LED on the front of the left end block
m.decal_xy([(-7.25, 2.0), (-6.95, 2.0), (-6.95, 2.3), (-7.25, 2.3)], ZE, LED)

# ------------------------------------------------------------ back: vents and sockets
ZBK = ZB - 0.02


def back_rect(x0, x1, y0, y1, col):
    m.polygon([(x0, y0, ZBK), (x1, y0, ZBK), (x1, y1, ZBK), (x0, y1, ZBK)], col, normal=(0, 0, -1))


for k in range(16):                            # vents across the middle
    x = 6.0 - k * 0.8
    back_rect(x - 0.14, x + 0.14, 3.7, 5.0, RIB)
back_rect(-8.0, 0.2, 1.45, 3.35, SEAM)         # recessed socket bay (right of the back, seen from behind)
ZBK -= 0.02
back_rect(-2.6, -0.6, 2.0, 2.8, HOLE)          # multi-out
back_rect(-3.75, -3.15, 2.1, 2.7, HOLE)        # RF out
back_rect(-7.1, -6.6, 2.1, 2.7, HOLE)          # power in

if __name__ == '__main__':
    print(m.stats())
    print(m.save())

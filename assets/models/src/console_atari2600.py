# SPDX-License-Identifier: GPL-3.0-or-later
"""Atari 2600, four-switch wood-grain model (1980-82), low-poly.

Built to the Commons reference photos (front-left, front-right, back-right
three-quarter views of the four-switch "woody"):

  * a black base tray, 34.5 x 23.5 cm, 4.2 cm high, whose whole front is
    the wood-grain strip; small feet underneath
  * on it, inset a little, the black upper shell: a long, almost flat
    ribbed deck over the front 55 % of the depth (16 ribs across the
    width), then the raised back hump: its front is the sloping switch
    plate (orange outline, two toggle switches left, two right, cartridge
    slot in the middle), a narrow flat top at 8.7 cm and a sloping back
    face with the two controller ports; the hump's sides lean inwards
  * the cartridge slot is a real vertical well (cartridge 8.3 x 2.3 cm plus
    0.15 / 0.2 cm clearance) behind two spring dust doors, moving parts
    "door_f" and "door_b" that fold down into the well

Front faces +Z, origin at the bottom centre.
"""
import math
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model

TRAY = (24, 23, 22)       # base tray
SHELL = (46, 44, 42)      # upper shell
RIB = (70, 68, 65)        # rib tops on the deck
GROOVE = (12, 12, 12)     # grooves between ribs
PLATE = (28, 28, 30)      # switch plate
ORANGE = (222, 122, 40)   # plate outline
WOOD = (132, 90, 46)
GRAIN = (80, 50, 22)
GRAIN2 = (166, 120, 64)
SILVER = (206, 206, 212)
DARK = (6, 6, 6)          # slot well, ports, switch slots
DOOR = (54, 54, 60)       # dust doors
BEZEL = (84, 84, 88)     # rim around the slot

m = Model('atari2600', 'console')

HX, ZF, ZB = 17.25, 11.75, -11.75     # tray half width, front, back
YT0, YT1 = 0.5, 4.2                   # tray bottom / top
CH = 0.8                              # tray corner chamfer

# ---------------------------------------------------------------- base tray
oct_ = [(-HX + CH, ZF), (HX - CH, ZF), (HX, ZF - CH), (HX, ZB + CH),
        (HX - CH, ZB), (-HX + CH, ZB), (-HX, ZB + CH), (-HX, ZF - CH)]
m.prism(oct_, YT0, YT1, TRAY, top=False)

# feet
for fx0, fx1 in ((-16.0, -13.0), (13.0, 16.0)):
    for fz0, fz1 in ((8.6, 10.8), (-10.8, -8.6)):
        m.box(fx0, 0, fz0, fx1, YT0, fz1, DARK, faces={'top': None})

# wood-grain front strip and its grain
m.decal_xy([(-16.3, 1.0), (16.3, 1.0), (16.3, 4.1), (-16.3, 4.1)], ZF, WOOD, lift=0.02)
for x0, x1, y, h, c in [(-16.3, -2.0, 1.30, 0.10, GRAIN), (3.5, 16.3, 1.45, 0.14, GRAIN),
                        (-12.0, 1.0, 1.70, 0.08, GRAIN2), (-9.0, 9.5, 2.00, 0.10, GRAIN),
                        (11.0, 16.3, 2.10, 0.08, GRAIN2), (-16.3, -6.0, 2.40, 0.14, GRAIN),
                        (1.0, 16.3, 2.65, 0.10, GRAIN), (-4.0, 6.0, 2.95, 0.08, GRAIN2),
                        (-14.0, 4.0, 3.20, 0.10, GRAIN), (8.0, 16.3, 3.45, 0.12, GRAIN),
                        (-16.3, -9.5, 3.70, 0.10, GRAIN), (-6.0, 12.0, 3.85, 0.08, GRAIN2)]:
    m.decal_xy([(x0, y), (x1, y), (x1, y + h), (x0, y + h)], ZF, c, lift=0.045)

# ---------------------------------------------------------------- upper shell
SX = 16.6                    # shell half width up to the hump
SZF, SZB = 11.45, -11.0      # shell front / back at the tray top
YK = 5.75                    # above this the hump's sides lean inwards
YTOP = 9.0                   # top of the hump
WTOP = 14.0                  # hump half width at the top
PZ0, PY0 = -1.2, 6.1         # switch plate: bottom edge
PZ1, PY1 = -6.2, YTOP        # switch plate: top edge
TZ = -8.6                    # back edge of the hump top


def w_at(y):
    if y <= YK:
        return SX
    return SX - (y - YK) / (YTOP - YK) * (SX - WTOP)


def back_z(y):
    """the sloping back face: from (TZ, YTOP) down to (SZB, YT1)"""
    return TZ + (YTOP - y) / (YTOP - YT1) * (SZB - TZ)


profile = [(SZF, YT1), (SZF, 4.9), (11.1, 5.15), (PZ0, YK), (PZ0, PY0),
           (PZ1, PY1), (TZ, YTOP), (back_z(YK), YK), (SZB, YT1)]


def side_caps():
    lower = [(SZF, YT1), (SZF, 4.9), (11.1, 5.15), (PZ0, YK), (back_z(YK), YK), (SZB, YT1)]
    upper = [(PZ0, YK), (PZ0, PY0), (PZ1, PY1), (TZ, YTOP), (back_z(YK), YK)]
    for s in (1, -1):
        for poly in (lower, upper):
            pts = [(s * w_at(y), y, z) for z, y in poly]
            # outward normal of the (possibly leaning) side plane
            if poly is lower:
                n = (s, 0, 0)
            else:
                n = (s * (YTOP - YK), SX - WTOP, 0)
            m.polygon(pts, SHELL, normal=n)


side_caps()


def strip(a, b, color):
    """quad across the shell between profile points a and b (z, y), facing out"""
    (za, ya), (zb, yb) = a, b
    wa, wb = w_at(ya), w_at(yb)
    # outward normal in (y, z): profile goes front -> back over the top
    n = (0, (za - zb), (yb - ya))
    m.polygon([(-wa, ya, za), (wa, ya, za), (wb, yb, zb), (-wb, yb, zb)], color, normal=n)


strip(profile[0], profile[1], SHELL)          # front lip
strip(profile[1], profile[2], SHELL)          # lip bevel
strip(profile[2], profile[3], RIB)            # ribbed deck
strip(profile[3], profile[4], SHELL)          # step up to the switch plate
strip(profile[5], profile[6], SHELL)          # hump top
# back face: one plane, its outline kinked where the hump's sides start leaning
_zk = back_z(YK)
m.polygon([(-SX, YT1, SZB), (SX, YT1, SZB), (SX, YK, _zk), (WTOP, YTOP, TZ), (-WTOP, YTOP, TZ), (-SX, YK, _zk)],
          SHELL, normal=(0, TZ - SZB, -(YTOP - YT1)))

# rim of the tray around the shell (ring between the octagon and the shell foot)
inner = [(-SX, SZF), (SX, SZF), (SX, SZB), (-SX, SZB)]
up = (0, 1, 0)
y = YT1
m.polygon([(oct_[0][0], y, oct_[0][1]), (oct_[1][0], y, oct_[1][1]), (SX, y, SZF), (-SX, y, SZF)], TRAY, normal=up)
m.polygon([(oct_[1][0], y, oct_[1][1]), (oct_[2][0], y, oct_[2][1]), (SX, y, SZF)], TRAY, normal=up)
m.polygon([(oct_[2][0], y, oct_[2][1]), (oct_[3][0], y, oct_[3][1]), (SX, y, SZB), (SX, y, SZF)], TRAY, normal=up)
m.polygon([(oct_[3][0], y, oct_[3][1]), (oct_[4][0], y, oct_[4][1]), (SX, y, SZB)], TRAY, normal=up)
m.polygon([(oct_[4][0], y, oct_[4][1]), (oct_[5][0], y, oct_[5][1]), (-SX, y, SZB), (SX, y, SZB)], TRAY, normal=up)
m.polygon([(oct_[5][0], y, oct_[5][1]), (oct_[6][0], y, oct_[6][1]), (-SX, y, SZB)], TRAY, normal=up)
m.polygon([(oct_[6][0], y, oct_[6][1]), (oct_[7][0], y, oct_[7][1]), (-SX, y, SZF), (-SX, y, SZB)], TRAY, normal=up)
m.polygon([(oct_[7][0], y, oct_[7][1]), (oct_[0][0], y, oct_[0][1]), (-SX, y, SZF)], TRAY, normal=up)

# ribs: dark grooves across the deck
DZ0, DY0, DZ1, DY1 = 11.1, 5.15, PZ0, YK
dn = (DZ0 - DZ1, DY1 - DY0)                   # (y, z) components of the deck normal
dl = math.hypot(*dn)
dny, dnz = dn[0] / dl, dn[1] / dl


def deck_pt(x, z, lift=0.02):
    y = DY0 + (DZ0 - z) / (DZ0 - DZ1) * (DY1 - DY0)
    return (x, y + lift * dny, z + lift * dnz)


NG = 16
for i in range(NG):
    zc = 10.55 - i * (10.55 - (PZ0 + 0.45)) / (NG - 1)
    m.polygon([deck_pt(-SX + 0.25, zc + 0.17), deck_pt(SX - 0.25, zc + 0.17),
               deck_pt(SX - 0.25, zc - 0.17), deck_pt(-SX + 0.25, zc - 0.17)], GROOVE, normal=(0, dny, dnz))

# ---------------------------------------------------------------- switch plate
TH = math.atan2(PY1 - PY0, PZ0 - PZ1)          # slope angle
CT, ST = math.cos(TH), math.sin(TH)
PL = math.hypot(PY1 - PY0, PZ0 - PZ1)          # plate length along the slope
NY, NZ = CT, ST                                # plate normal (up and to the front)


def ppt(x, s, c=0.0):
    """point on the plate: x across, s along the slope from its bottom edge, c off the surface"""
    return (x, PY0 + s * ST + c * NY, PZ0 - s * CT + c * NZ)


def s_of_z(z):
    return (PZ0 - z) / CT


def prect(x0, x1, s0, s1, color, c=0.02):
    m.polygon([ppt(x0, s0, c), ppt(x1, s0, c), ppt(x1, s1, c), ppt(x0, s1, c)], color, normal=(0, NY, NZ))


def pw(s):
    return w_at(PY0 + s * ST)


# the slot well: cartridge 8.3 x 2.3 cm, centred at x = 0, z = SLZ
SLZ = -3.55
SLX = 4.15 + 0.15            # well half width  (0.15 cm clearance)
SLD = 1.15 + 0.2             # well half depth  (0.2 cm clearance, room for the folded doors)
WZF, WZB = SLZ + SLD, SLZ - SLD
SF, SB = s_of_z(WZF), s_of_z(WZB)
FLOOR = 1.5                  # well floor: the cartridge's bottom when seated

# plate around the hole (four planar pieces)
m.polygon([ppt(-pw(0), 0), ppt(pw(0), 0), ppt(pw(SF), SF), ppt(-pw(SF), SF)], PLATE, normal=(0, NY, NZ))
m.polygon([ppt(-pw(SB), SB), ppt(pw(SB), SB), ppt(pw(PL), PL), ppt(-pw(PL), PL)], PLATE, normal=(0, NY, NZ))
m.polygon([ppt(-pw(SF), SF), ppt(-SLX, SF), ppt(-SLX, SB), ppt(-pw(SB), SB)], PLATE, normal=(0, NY, NZ))
m.polygon([ppt(SLX, SF), ppt(pw(SF), SF), ppt(pw(SB), SB), ppt(SLX, SB)], PLATE, normal=(0, NY, NZ))

# well walls and floor (all facing into the well)
yf, yb = PY0 + SF * ST, PY0 + SB * ST
m.polygon([(-SLX, FLOOR, WZF), (-SLX, yf, WZF), (SLX, yf, WZF), (SLX, FLOOR, WZF)], DARK, normal=(0, 0, -1))
m.polygon([(-SLX, FLOOR, WZB), (SLX, FLOOR, WZB), (SLX, yb, WZB), (-SLX, yb, WZB)], DARK, normal=(0, 0, 1))
m.polygon([(-SLX, FLOOR, WZF), (-SLX, FLOOR, WZB), (-SLX, yb, WZB), (-SLX, yf, WZF)], DARK, normal=(1, 0, 0))
m.polygon([(SLX, FLOOR, WZF), (SLX, yf, WZF), (SLX, yb, WZB), (SLX, FLOOR, WZB)], DARK, normal=(-1, 0, 0))
m.polygon([(-SLX, FLOOR, WZF), (SLX, FLOOR, WZF), (SLX, FLOOR, WZB), (-SLX, FLOOR, WZB)], DARK, normal=(0, 1, 0))

# light bezel ring around the slot
BZ = 0.45
prect(-SLX - BZ, SLX + BZ, SF - BZ, SF, BEZEL)
prect(-SLX - BZ, SLX + BZ, SB, SB + BZ, BEZEL)
prect(-SLX - BZ, -SLX, SF, SB, BEZEL)
prect(SLX, SLX + BZ, SF, SB, BEZEL)

# orange outline around the plate
OX, OS0, OS1, LW = 13.6, 0.35, PL - 0.35, 0.14
prect(-OX, OX, OS0, OS0 + LW, ORANGE)
prect(-OX, OX, OS1 - LW, OS1, ORANGE)
prect(-OX, -OX + LW, OS0, OS1, ORANGE)
prect(OX - LW, OX, OS0, OS1, ORANGE)

# four toggle switches: black slot plate + chrome lever standing off the plate
SS = s_of_z(SLZ)
for sx in (-9.7, -6.5, 6.8, 10.2):
    prect(sx - 0.45, sx + 0.45, SS - 0.9, SS + 0.9, DARK)
    a, b, h = 0.2, 0.2, 1.5
    q = [ppt(sx - a, SS - b, 0), ppt(sx + a, SS - b, 0), ppt(sx + a, SS + b, 0), ppt(sx - a, SS + b, 0)]
    # lever leans a little towards the top of the plate
    t = [ppt(sx - a, SS - b + 0.35, h), ppt(sx + a, SS - b + 0.35, h),
         ppt(sx + a, SS + b + 0.35, h), ppt(sx - a, SS + b + 0.35, h)]
    m.polygon([t[0], t[1], t[2], t[3]], SILVER, normal=(0, NY, NZ))
    for i in range(4):
        j = (i + 1) % 4
        m.quad(q[i], q[j], t[j], t[i], SILVER)

# ---------------------------------------------------------------- back face: ports and switches
BL = math.hypot(YTOP - YT1, TZ - SZB)
bny, bnz = (TZ - SZB) / BL, -(YTOP - YT1) / BL       # outward normal (up, back)


def bpt(x, t, lift=0.02):
    """point on the back face: t = 0 at the tray top, 1 at the hump top"""
    return (x, YT1 + t * (YTOP - YT1) + lift * bny, SZB + t * (TZ - SZB) + lift * bnz)


def brect(x0, x1, t0, t1, color, lift=0.02):
    m.polygon([bpt(x0, t0, lift), bpt(x1, t0, lift), bpt(x1, t1, lift), bpt(x0, t1, lift)], color, normal=(0, bny, bnz))


for px in (-8.5, 8.5):                         # controller ports (D shape)
    m.polygon([bpt(px - 1.4, 0.62), bpt(px + 1.4, 0.62), bpt(px + 1.1, 0.38), bpt(px - 1.1, 0.38)],
              DARK, normal=(0, bny, bnz))
for px in (-12.5, -3.2, 3.2):                  # difficulty / channel slide switches
    brect(px - 0.45, px + 0.45, 0.42, 0.58, DARK)

# ---------------------------------------------------------------- dust doors (moving parts)
T = 0.08                     # door thickness
REC = 0.35                   # doors sit this far under the plate surface


def door_pt(x, z_on_bottom_line, along, off):
    """a point of a door: start from the bottom-surface line of the closed
    doors at depth z, go `along` the slope (towards the back), `off` along
    the plate normal"""
    # bottom-surface line: plate surface offset by -(REC + T) along the normal
    c = -(REC + T)
    # point on that line with the given z: z = PZ0 - s*CT + c*NZ
    s = (PZ0 + c * NZ - z_on_bottom_line) / CT
    p = ppt(x, s, c)
    return (p[0], p[1] + along * ST + off * NY, p[2] - along * CT + off * NZ)


DX = SLX - 0.1
PIVF_Z = WZF - T * ST - 0.02           # front door hinge (bottom surface)
PIVB_Z = WZB + 0.02                    # back door hinge (bottom surface)
span = (PIVF_Z - PIVB_Z) / CT
DL = (span - 0.06) / 2


def door(z0, d0, d1):
    """a door as a box in a local frame (x, plate normal, down the slope)
    placed at the hinge point; along-slope extent d0..d1 (towards the back)"""
    base = door_pt(0, z0, 0, 0)
    lo, hi = min(d0, d1), max(d0, d1)
    ids = m.box(-DX, 0, -hi, DX, T, -lo, DOOR, faces={'bottom': DARK})

    def f(p):
        x, o, d = p            # d runs down the slope (= -along)
        return (x, base[1] + o * NY - d * ST, base[2] + o * NZ + d * CT)
    m.transform(ids, f)


with m.part('door_f'):
    door(PIVF_Z, 0, DL)
with m.part('door_b'):
    door(PIVB_Z, 0, -DL)

PIVOT_F = door_pt(0, PIVF_Z, 0, 0)
PIVOT_B = door_pt(0, PIVB_Z, 0, 0)

if __name__ == '__main__':
    path = m.save()
    st = m.stats()
    print(path, st)
    print('slope deg %.2f  well z %.3f..%.3f  x +-%.3f  floor %.2f  yf %.3f yb %.3f' % (
        math.degrees(TH), WZB, WZF, SLX, FLOOR, yf, yb))
    print('pivot_f', [round(v, 4) for v in PIVOT_F], 'angle', round(-(90 + math.degrees(TH)), 3))
    print('pivot_b', [round(v, 4) for v in PIVOT_B], 'angle', round(90 - math.degrees(TH), 3))

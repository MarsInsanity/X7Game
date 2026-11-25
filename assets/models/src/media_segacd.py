# SPDX-License-Identifier: GPL-3.0-or-later
"""Sega CD game disc in its CD jewel case, standing upright, front to +Z.

Real size ~14.2 x 12.5 x 1.0 cm. Signature features: the clear case read as
light grey edges and a raised frame around the front lid, the ridged hinge
strip down the left side of the lid, the black tray seen through the lid,
the silver 12 cm disc with a coloured label ring, clear hub and centre hole,
the red cover band across the top of the front (the system's header
stripe) with a thin white line, and the dark spine on the left edge.
"""
import math
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'tools', 'models'))
from x7model import Model

CLEAR = (178, 190, 204)      # clear plastic edges / lid frame
HINGE = (214, 222, 232)      # hinge strip (thicker clear plastic, catches light)
HINGE_D = (120, 132, 148)    # hinge ridges
TRAY = (22, 22, 28)          # black tray seen through the lid
SILVER = (226, 230, 238)     # disc surface
LABEL = (40, 96, 210)        # disc label ring
LABEL2 = (240, 200, 60)      # thin accent ring on the label
HUB = (128, 136, 150)        # clear hub of the disc
HOLE = (10, 10, 14)          # centre hole
RED = (206, 28, 36)          # cover header band
WHITE = (240, 240, 240)      # thin line under the band
SPINE = (36, 36, 44)         # spine / back insert
BACK = (70, 74, 86)          # back insert artwork area

W, H = 14.2, 12.5
X0, X1 = -W / 2, W / 2
ZB, ZF = -0.5, 0.42          # case body back / front face (tray behind lid)
ZL = 0.5                     # raised lid frame / hinge front
HW = 1.0                     # hinge strip width on the left

m = Model('segacd', 'media')

# Every flat face is tiled without overlapping decals: big stacked decals
# z-fight under the affine depth of a software rasteriser.

F = 0.35                     # width of the raised lid frame
XA, XB = X0 + HW, X1 - F     # lid opening (inside the frame)
YA, YB = F, H - F
BY = H - 2.6                 # bottom of the red cover band
YC = BY - 0.22               # bottom of the white line = top of the disc window


def front_rect(x0, y0, x1, y1, z, color):
    m.quad((x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z), color)


def back_rect(x0, y0, x1, y1, z, color):
    m.quad((x1, y0, z), (x0, y0, z), (x0, y1, z), (x1, y1, z), color)


def clip_below(poly, yc):
    """Sutherland-Hodgman: keep the part of a 2D polygon with y <= yc."""
    out = []
    for i in range(len(poly)):
        p, q = poly[i], poly[(i + 1) % len(poly)]
        pin, qin = p[1] <= yc, q[1] <= yc
        if pin:
            out.append(p)
        if pin != qin:
            t = (yc - p[1]) / (q[1] - p[1])
            out.append((p[0] + t * (q[0] - p[0]), yc))
    return out


def front_poly(pts, color):
    pts = clip_below(pts, YC)
    if len(pts) >= 3:
        m.polygon([(x, y, ZF) for x, y in pts], color, normal=(0, 0, 1))


# case body: clear right side, top and bottom (front, back and spine tiled below)
m.box(X0, 0, ZB, X1, H, ZF, CLEAR, faces={'front': None, 'back': None, 'left': None})

# raised lid frame: one U-shaped extrusion (top, right, bottom edges)
m.extrude_xy([(XA, H), (XA, YB), (XB, YB), (XB, YA), (XA, YA), (XA, 0), (X1, 0), (X1, H)],
             ZF, ZL, CLEAR, back=False)

# hinge strip down the left edge, a little prouder, with ridges near both ends
m.box(X0, 0, ZF, X0 + HW, H, ZL + 0.06, HINGE, faces={'back': None})
for y in (0.8, H - 1.3):
    m.decal_xy([(X0 + 0.18, y), (X0 + HW - 0.18, y), (X0 + HW - 0.18, y + 0.5), (X0 + 0.18, y + 0.5)],
               ZL + 0.06, HINGE_D, lift=0.03)

# cover band and white line across the top of the lid opening
front_rect(XA, BY, XB, YB, ZF, RED)
front_rect(XA, YC, XB, BY, ZF, WHITE)

# disc window: concentric rings on the black tray, clipped under the band
N = 16
DCX, DCY = (XA + XB) / 2, H / 2


def ring_pt(r, i, n=N):
    a = 2 * math.pi * i / n + math.pi / N
    return (DCX + r * math.cos(a), DCY + r * math.sin(a))


RINGS = [(5.85, SILVER), (4.3, LABEL), (2.35, LABEL2), (1.95, HUB)]
for k, (r, col) in enumerate(RINGS):
    if k + 1 < len(RINGS):
        ri = RINGS[k + 1][0]
        for i in range(N):
            front_poly([ring_pt(ri, i), ring_pt(ri, i + 1), ring_pt(r, i + 1), ring_pt(r, i)], col)
    else:
        # clear hub between the 16-gon and an 8-gon centre hole
        RH = 0.75
        for j in range(N // 2):
            front_poly([ring_pt(RH, j, N // 2), ring_pt(RH, j + 1, N // 2),
                        ring_pt(r, 2 * j + 2), ring_pt(r, 2 * j + 1), ring_pt(r, 2 * j)], col)
        front_poly([ring_pt(RH, j, N // 2) for j in range(N // 2)], HOLE)

# black tray around the disc: one piece per disc segment out to the window edge
CORNERS = [(XB, YB), (XA, YB), (XA, YA), (XB, YA)]
CORNER_A = [math.atan2(cy - DCY, cx - DCX) % (2 * math.pi) for cx, cy in CORNERS]


def rect_hit(i):
    a = 2 * math.pi * i / N + math.pi / N
    dx, dy = math.cos(a), math.sin(a)
    ts = []
    if dx > 1e-9: ts.append((XB - DCX) / dx)
    if dx < -1e-9: ts.append((XA - DCX) / dx)
    if dy > 1e-9: ts.append((YB - DCY) / dy)
    if dy < -1e-9: ts.append((YA - DCY) / dy)
    t = min(ts)
    return (DCX + t * dx, DCY + t * dy), a % (2 * math.pi)


R0 = RINGS[0][0]
for i in range(N):
    (p0, a0), (p1, a1) = rect_hit(i), rect_hit(i + 1)
    if a1 < a0:
        a1 += 2 * math.pi
    mids = sorted((ca if ca >= a0 else ca + 2 * math.pi, c) for ca, c in zip(CORNER_A, CORNERS))
    mids = [c for ca, c in mids if a0 < ca < a1]
    front_poly([ring_pt(R0, i), p0] + mids + [p1, ring_pt(R0, i + 1)], TRAY)

# back insert, tiled: artwork panel, red band, dark surround
back_rect(X0, 0, X1, 0.9, ZB, SPINE)
back_rect(X0, 0.9, X0 + 1.2, H - 3.0, ZB, SPINE)
back_rect(X0 + 1.2, 0.9, X1 - 0.7, H - 3.0, ZB, BACK)
back_rect(X1 - 0.7, 0.9, X1, H - 3.0, ZB, SPINE)
back_rect(X0, H - 3.0, X1, H - 2.4, ZB, SPINE)
back_rect(X0, H - 2.4, X1, H - 0.6, ZB, RED)
back_rect(X0, H - 0.6, X1, H, ZB, SPINE)

# spine (left edge), with the red band continuing round it
for y0, y1, col in ((0, H - 2.4, SPINE), (H - 2.4, H - 0.6, RED), (H - 0.6, H, SPINE)):
    m.quad((X0, y0, ZB), (X0, y0, ZF), (X0, y1, ZF), (X0, y1, ZB), col)

print(m.stats())
m.save()

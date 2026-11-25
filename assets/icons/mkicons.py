# SPDX-License-Identifier: GPL-3.0-or-later
"""
mkicons.py - the frontend's app icons as one-colour SVGs.

    python assets/icons/mkicons.py [#RRGGBB]

Writes <name>.svg next to this script. Every icon is a single <path> with a
single fill colour (ACCENT, or the colour given) on a 48 x 48 grid, without
strokes, gradients, masks or transforms, so the simplest SVG rasteriser
draws it. Cut-outs (the D-pad, the disc's hole, the play triangle ...) are
holes in the path (fill-rule evenodd), so they show the background. The
music icon has no holes; its overlapping parts join (fill-rule nonzero,
every part wound clockwise).

The icons are original drawings of what each app does; none copies an
existing logo.
"""
import math
import os
import sys

ACCENT = '#A596E7'      # the frontend accent: a light SNES-like purple (exact in RGB565)
OUT = os.path.dirname(os.path.abspath(__file__))


def f(v):
    s = ('%.2f' % v).rstrip('0').rstrip('.')
    return '0' if s == '-0' else s


def poly(pts):
    return 'M' + ' L'.join('%s %s' % (f(x), f(y)) for x, y in pts) + ' Z'


def circle(cx, cy, r):
    return 'M%s %s A%s %s 0 1 1 %s %s A%s %s 0 1 1 %s %s Z' % (
        f(cx + r), f(cy), f(r), f(r), f(cx - r), f(cy), f(r), f(r), f(cx + r), f(cy))


def ellipse(cx, cy, rx, ry, deg):
    a = math.radians(deg)
    dx, dy = rx * math.cos(a), rx * math.sin(a)
    return 'M%s %s A%s %s %s 1 1 %s %s A%s %s %s 1 1 %s %s Z' % (
        f(cx + dx), f(cy + dy), f(rx), f(ry), f(deg), f(cx - dx), f(cy - dy),
        f(rx), f(ry), f(deg), f(cx + dx), f(cy + dy))


def rrect(x0, y0, x1, y1, r):
    return ('M%s %s H%s A%s %s 0 0 1 %s %s V%s A%s %s 0 0 1 %s %s H%s A%s %s 0 0 1 %s %s V%s A%s %s 0 0 1 %s %s Z'
            % (f(x0 + r), f(y0), f(x1 - r), f(r), f(r), f(x1), f(y0 + r), f(y1 - r), f(r), f(r), f(x1 - r), f(y1),
               f(x0 + r), f(r), f(r), f(x0), f(y1 - r), f(y0 + r), f(r), f(r), f(x0 + r), f(y0)))


def ring_points(cx, cy, radii, n, phase=0.0):
    """closed outline alternating between the given radii (a gear)"""
    out = []
    for i in range(n):
        for k, (r, da) in enumerate(radii):
            a = math.radians(phase + 360.0 * i / n + da)
            out.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return out


# ------------------------------------------------------------------ the icons
def retroarch():
    """RetroArch: a game pad (D-pad left, four buttons right)."""
    body = ('M14 11 H34 C40 11 43.2 14.5 44.6 19.5 L46.6 30 C47.6 35.5 44.8 39.5 40.6 39.5 '
            'C37.8 39.5 36.2 38 34.8 35.6 L33 32.5 H15 L13.2 35.6 C11.8 38 10.2 39.5 7.4 39.5 '
            'C3.2 39.5 0.4 35.5 1.4 30 L3.4 19.5 C4.8 14.5 8 11 14 11 Z')
    cx, cy, a, b = 13.5, 22.5, 1.7, 5.2            # D-pad: arm half width, arm reach
    cross = [(cx - a, cy - b), (cx + a, cy - b), (cx + a, cy - a), (cx + b, cy - a), (cx + b, cy + a),
             (cx + a, cy + a), (cx + a, cy + b), (cx - a, cy + b), (cx - a, cy + a), (cx - b, cy + a),
             (cx - b, cy - a), (cx - a, cy - a)]
    bx, by, d, r = 34.5, 22.5, 3.9, 2.0             # four face buttons in a diamond
    buttons = [circle(bx + dx, by + dy, r) for dx, dy in ((0, -d), (d, 0), (0, d), (-d, 0))]
    pills = [rrect(19.8, 27.2, 23.2, 29.0, 0.9), rrect(24.8, 27.2, 28.2, 29.0, 0.9)]   # select, start
    return [body, poly(cross)] + buttons + pills


def _bite_disc(cx, cy, r, bx, by, br):
    """a disc with a round bite taken out of it (the bite overlaps its edge)"""
    d = math.hypot(bx - cx, by - cy)
    a = (r * r - br * br + d * d) / (2 * d)         # from the disc centre along the line to the bite
    h = math.sqrt(r * r - a * a)
    ux, uy = (bx - cx) / d, (by - cy) / d
    mx, my = cx + a * ux, cy + a * uy
    p1 = (mx - h * uy, my + h * ux)
    p2 = (mx + h * uy, my - h * ux)
    # disc edge from p1 the long way round to p2, then the bite's edge back to p1
    return 'M%s %s A%s %s 0 1 1 %s %s A%s %s 0 0 0 %s %s Z' % (
        f(p1[0]), f(p1[1]), f(r), f(r), f(p2[0]), f(p2[1]), f(br), f(br), f(p1[0]), f(p1[1]))


def pcsx4all():
    """PCSX4All settings: a game disc with a gear in front of it."""
    dcx, dcy, dr = 20.5, 20.5, 18.0
    gcx, gcy = 36.0, 36.0
    disc = _bite_disc(dcx, dcy, dr, gcx, gcy, 13.0)
    groove = [circle(dcx, dcy, 7.4), circle(dcx, dcy, 6.0)]          # a thin ring round the hub
    hole = circle(dcx, dcy, 3.4)
    # gear: 8 teeth (outer radius 10.5, root 7.9), with its axle hole
    gear = ring_points(gcx, gcy, [(10.5, -9.0), (10.5, 9.0), (7.9, 15.5), (7.9, 29.5)], 8, phase=22.5)
    return [disc] + groove + [hole, poly(gear), circle(gcx, gcy, 3.6)]


def music():
    """Music: two beamed notes."""
    heads = [ellipse(14.0, 37.7, 6.5, 4.8, -25), ellipse(34.0, 33.7, 6.5, 4.8, -25)]
    # stems along the heads' right sides, joined by a sloping beam (one outline)
    s1x0, s1x1, s2x0, s2x1 = 17.1, 20.2, 37.1, 40.2
    top_l, top_r, t = 11.2, 5.2, 5.6                # beam top at the left and right, thickness
    k = (top_r - top_l) / (s2x1 - s1x0)             # the beam's slope (its underside runs parallel)
    notes = [(s1x0, 37.2), (s1x0, top_l), (s2x1, top_r), (s2x1, 33.2), (s2x0, 33.2),
             (s2x0, top_l + k * (s2x0 - s1x0) + t), (s1x1, top_l + k * (s1x1 - s1x0) + t), (s1x1, 37.2)]
    return heads + [poly(notes)]


def video():
    """Video: a film frame with sprocket holes and a play triangle."""
    frame = rrect(3, 8, 45, 40, 4.5)
    holes = []
    for i in range(6):
        x = 7.5 + i * 6
        holes += [rrect(x, 10.6, x + 3, 13.6, 0.8), rrect(x, 34.4, x + 3, 37.4, 0.8)]
    play = poly([(20.0, 17.0), (31.5, 24.0), (20.0, 31.0)])
    return [frame] + holes + [play]


def ebook():
    """E-Book: an open book with lines of text."""
    left = 'M22.8 13.2 C18 9.6 10.8 8.6 3 10 V38.4 C10.8 37 18 38 22.8 41.6 Z'
    right = 'M25.2 13.2 C30 9.6 37.2 8.6 45 10 V38.4 C37.2 37 30 38 25.2 41.6 Z'
    lines = []
    for i in range(4):
        y = 16.6 + i * 5.4
        lines.append(poly([(7.2, y - 1.6), (19.0, y + 0.6), (19.0, y + 2.4), (7.2, y + 0.2)]))
        lines.append(poly([(40.8, y - 1.6), (29.0, y + 0.6), (29.0, y + 2.4), (40.8, y + 0.2)]))
    return [left, right] + lines


def photos():
    """Photos: a picture frame with mountains and the sun."""
    frame = rrect(3, 7, 45, 41, 5)
    x0, y0, x1, r = 7.5, 11.5, 40.5, 2.0
    # the window above the mountain ridge (the mountains stay solid)
    ridge = [(x1, 31.5), (32.5, 23.5), (28.2, 27.8), (19.0, 18.6), (x0, 30.6)]
    window = ('M%s %s V%s A%s %s 0 0 1 %s %s H%s A%s %s 0 0 1 %s %s ' % (
        f(x0), f(ridge[-1][1]), f(y0 + r), f(r), f(r), f(x0 + r), f(y0), f(x1 - r), f(r), f(r), f(x1), f(y0 + r))
        + 'L' + ' L'.join('%s %s' % (f(x), f(y)) for x, y in ridge[:-1]) + ' Z')
    sun = circle(33.0, 17.0, 3.2)
    return [frame, window, sun]


ICONS = {'retroarch': retroarch, 'pcsx4all': pcsx4all, 'music': music,
         'video': video, 'ebook': ebook, 'photos': photos}


def main():
    color = sys.argv[1] if len(sys.argv) > 1 else ACCENT
    for name, fn in ICONS.items():
        d = ' '.join(fn())
        rule = 'nonzero' if name == 'music' else 'evenodd'
        svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="48" height="48">\n'
               '<path fill="%s" fill-rule="%s" d="%s"/>\n</svg>\n' % (color, rule, d))
        path = os.path.join(OUT, name + '.svg')
        with open(path, 'w', newline='\n') as fh:
            fh.write(svg)
        print(path)


if __name__ == '__main__':
    main()

# SPDX-License-Identifier: GPL-3.0-or-later
"""
x7model - build X7 Game's low-poly 3D models in Python and write them as
Wavefront OBJ + MTL.

Conventions (every model):
  * units: centimetres, real-world size (a console and its cartridge share
    one scale)
  * Y up, the front of the object faces +Z, origin at the bottom centre
    (the object stands on y = 0, centred on x = 0, z = 0)
  * triangles only, wound counter-clockwise seen from outside (the frontend
    culls back faces)
  * flat colours; every colour is an exact RGB565 colour (the frontend runs
    in 16-bit), stored as an MTL material "c_RRGGBB"
  * the one exception is the image area (material "image", with texture
    coordinates): the frontend draws the game's picture there, e.g. on a
    cartridge label (image_rect / image_xy / image_ring / image_polygon).
    u runs along the picture's width (left to right), v along its height
    (bottom to top, the OBJ convention)
  * no text, logos or trademarks: labels are plain coloured areas
  * moving parts (a lid, a door, a tray) are built inside `with m.part('lid'):`
    and saved as OBJ groups ("g lid"); everything else is group "body".
    Parts are modelled in their closed position; how they move is in the
    system file (assets/models/systems/<id>.json, see render.py)

Typical use:

    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tools', 'models'))
    from x7model import Model

    m = Model('snes', 'console')
    body = m.box(-12, 0, -10, 12, 6, 10, (180, 180, 190))
    m.save()            # writes assets/models/consoles/snes.obj + .mtl

Run tools/models/render.py on the .obj to see it.
"""
import math
import os
import re

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
KIND_DIRS = {'console': 'consoles', 'media': 'media'}
IMAGE = 'image'           # the "colour" of image-area triangles


def rgb565(r, g, b):
    """The nearest RGB565 colour, as 8-bit (r, g, b) the way the hardware
    expands it (5/6 bits replicated into the low bits)."""
    r5 = max(0, min(31, int(round(r * 31 / 255))))
    g6 = max(0, min(63, int(round(g * 63 / 255))))
    b5 = max(0, min(31, int(round(b * 31 / 255))))
    return ((r5 << 3) | (r5 >> 2), (g6 << 2) | (g6 >> 4), (b5 << 3) | (b5 >> 2))


def color_name(c):
    return 'c_%02X%02X%02X' % c


def _sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _norm(a):
    l = math.sqrt(_dot(a, a))
    return (a[0] / l, a[1] / l, a[2] / l) if l > 1e-12 else (0.0, 0.0, 0.0)


def _area2(p):
    """twice the signed area of a 2D polygon (counter-clockwise > 0)"""
    s = 0.0
    for i in range(len(p)):
        x0, y0 = p[i]
        x1, y1 = p[(i + 1) % len(p)]
        s += x0 * y1 - x1 * y0
    return s


def triangulate(poly):
    """Ear-clipping triangulation of a simple 2D polygon (any winding).
    Returns index triples, counter-clockwise in the polygon's 2D space."""
    n = len(poly)
    idx = list(range(n))
    if _area2(poly) < 0:
        idx.reverse()
    tris = []

    def inside(p, a, b, c):
        def s(p1, p2, p3):
            return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])
        d1, d2, d3 = s(p, a, b), s(p, b, c), s(p, c, a)
        neg = d1 < 0 or d2 < 0 or d3 < 0
        pos = d1 > 0 or d2 > 0 or d3 > 0
        return not (neg and pos)

    guard = 0
    while len(idx) > 3 and guard < 10000:
        guard += 1
        found = False
        for k in range(len(idx)):
            i0, i1, i2 = idx[k - 1], idx[k], idx[(k + 1) % len(idx)]
            a, b, c = poly[i0], poly[i1], poly[i2]
            if (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]) <= 1e-12:
                continue            # reflex or flat
            if any(inside(poly[j], a, b, c) for j in idx if j not in (i0, i1, i2)):
                continue
            tris.append((i0, i1, i2))
            idx.pop(k)
            found = True
            break
        if not found:
            break
    if len(idx) == 3:
        tris.append(tuple(idx))
    return tris


class Model:
    """A list of coloured triangles. Every helper returns the indices of the
    triangles it added, so a part can be moved or recoloured afterwards."""

    def __init__(self, name, kind):
        assert kind in KIND_DIRS, kind
        self.name = name
        self.kind = kind
        self.verts = []          # (x, y, z)
        self.tris = []           # (i0, i1, i2, colour or IMAGE)
        self.parts = {}          # triangle index -> part name (absent = 'body')
        self.uvs = {}            # triangle index -> ((u, v), (u, v), (u, v)) for IMAGE triangles
        self.image_fallback = (200, 200, 200)   # drawn when there is no picture
        self.image_frames = []   # (width_cm, height_cm) of each image area
        self._part = 'body'
        self._vmap = {}

    # ----------------------------------------------------------- basics
    def _v(self, p):
        key = (round(p[0], 4), round(p[1], 4), round(p[2], 4))
        i = self._vmap.get(key)
        if i is None:
            i = len(self.verts)
            self.verts.append(key)
            self._vmap[key] = i
        return i

    def tri(self, a, b, c, color):
        """One triangle a, b, c (counter-clockwise seen from its front)."""
        col = IMAGE if color == IMAGE else rgb565(*color)
        ia, ib, ic = self._v(a), self._v(b), self._v(c)
        if len({ia, ib, ic}) < 3:
            return []
        n = _cross(_sub(self.verts[ib], self.verts[ia]), _sub(self.verts[ic], self.verts[ia]))
        if _dot(n, n) < 1e-14:
            return []
        self.tris.append((ia, ib, ic, col))
        if self._part != 'body':
            self.parts[len(self.tris) - 1] = self._part
        return [len(self.tris) - 1]

    def part(self, name):
        """Build a moving part:  with m.part('lid'): m.box(...)
        Names: lower case letters, digits, underscore."""
        assert re.match(r'^[a-z][a-z0-9_]*$', name), name
        model = self

        class _Part:
            def __enter__(self):
                self.prev = model._part
                model._part = name
                return model

            def __exit__(self, *exc):
                model._part = self.prev
        return _Part()

    def part_of(self, t):
        return self.parts.get(t, 'body')

    # ----------------------------------------------------------- image area
    def image_polygon(self, pts, frame, fallback=None, normal=None):
        """An image area: a flat polygon (3D points, like polygon()) showing
        the game's picture. frame = (bottom_left, bottom_right, top_left), 3D
        points of the picture's corners in the same plane; each vertex gets
        its texture coordinates by projection onto that frame, so the
        polygon may be any shape inside it (a rounded label, part of a ring).
        `fallback` is the colour drawn when there is no picture."""
        o, pu, pv = frame
        U, V = _sub(pu, o), _sub(pv, o)
        uu, vv = _dot(U, U), _dot(V, V)
        if fallback is not None:
            self.image_fallback = rgb565(*fallback)
        ids = self.polygon(pts, IMAGE, normal=normal)
        for t in ids:
            uv = []
            for i in self.tris[t][:3]:
                d = _sub(self.verts[i], o)
                uv.append((round(_dot(d, U) / uu, 5), round(_dot(d, V) / vv, 5)))
            self.uvs[t] = tuple(uv)
        self.image_frames.append((math.sqrt(uu), math.sqrt(vv)))
        return ids

    def image_rect(self, origin, u, v, fallback=None):
        """A rectangular image area: corners origin (the picture's bottom
        left), origin+u (bottom right), origin+u+v, origin+v (top left). It
        faces the side u x v points to (u right, v up as seen from the
        front)."""
        o = origin
        p1 = (o[0] + u[0], o[1] + u[1], o[2] + u[2])
        p3 = (o[0] + v[0], o[1] + v[1], o[2] + v[2])
        p2 = (p1[0] + v[0], p1[1] + v[1], p1[2] + v[2])
        return self.image_polygon([o, p1, p2, p3], (o, p1, p3), fallback, normal=_cross(u, v))

    def image_xy(self, x0, y0, x1, y1, z, fallback=None, lift=0.03, outline=None):
        """The usual cartridge label: an image area facing +Z at depth z
        (drawn `lift` cm in front of it), the picture filling the rectangle
        x0..x1, y0..y1. `outline` (2D x, y points inside that rectangle) cuts
        it to another shape, e.g. Model.rounded_rect(...)."""
        zz = z + lift
        pts = outline or [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        return self.image_polygon([(x, y, zz) for x, y in pts],
                                  ((x0, y0, zz), (x1, y0, zz), (x0, y1, zz)), fallback, normal=(0, 0, 1))

    def image_ring(self, cx, cy, z, r0, r1, segments=16, fallback=None):
        """A disc label: a ring (r0 = hole, r1 = outer edge) facing +Z at
        depth z, the picture filling the square around the outer circle."""
        frame = ((cx - r1, cy - r1, z), (cx + r1, cy - r1, z), (cx - r1, cy + r1, z))
        o, pu, pv = frame
        if fallback is not None:
            self.image_fallback = rgb565(*fallback)
        ids = []
        for i in range(segments):
            a0, a1 = 2 * math.pi * i / segments, 2 * math.pi * (i + 1) / segments
            q = [(cx + r0 * math.cos(a0), cy + r0 * math.sin(a0), z), (cx + r1 * math.cos(a0), cy + r1 * math.sin(a0), z),
                 (cx + r1 * math.cos(a1), cy + r1 * math.sin(a1), z), (cx + r0 * math.cos(a1), cy + r0 * math.sin(a1), z)]
            for t in self.quad(*q, IMAGE):
                self.uvs[t] = tuple(((self.verts[k][0] - o[0]) / (2 * r1), (self.verts[k][1] - o[1]) / (2 * r1))
                                    for k in self.tris[t][:3])
                ids.append(t)
        self.image_frames.append((2 * r1, 2 * r1))
        return ids

    def quad(self, a, b, c, d, color):
        """a, b, c, d counter-clockwise seen from the front."""
        return self.tri(a, b, c, color) + self.tri(a, c, d, color)

    def polygon(self, pts, color, normal=None):
        """A flat polygon (3D points, simple, planar). Counter-clockwise seen
        from the front; or give `normal` and the winding is fixed to face it."""
        if normal is None:
            normal = _norm(_cross(_sub(pts[1], pts[0]), _sub(pts[2], pts[0])))
            # Newell's method for a robust normal of a possibly concave polygon
            nx = ny = nz = 0.0
            for i in range(len(pts)):
                p, q = pts[i], pts[(i + 1) % len(pts)]
                nx += (p[1] - q[1]) * (p[2] + q[2])
                ny += (p[2] - q[2]) * (p[0] + q[0])
                nz += (p[0] - q[0]) * (p[1] + q[1])
            normal = _norm((nx, ny, nz))
        n = _norm(normal)
        # 2D basis in the plane
        ref = (1, 0, 0) if abs(n[0]) < 0.9 else (0, 1, 0)
        u = _norm(_cross(ref, n))
        v = _cross(n, u)
        p2 = [(_dot(p, u), _dot(p, v)) for p in pts]
        out = []
        for i0, i1, i2 in triangulate(p2):
            out += self.tri(pts[i0], pts[i1], pts[i2], color)
        return out

    # ----------------------------------------------------------- shapes
    def box(self, x0, y0, z0, x1, y1, z1, color, faces=None):
        """Axis-aligned box. `faces` may give per-side colours:
        {'top','bottom','front','back','left','right'} -> colour; missing
        sides use `color`. Pass faces={'bottom': None} to leave a side out."""
        faces = faces or {}

        def col(k):
            return faces.get(k, color)
        p = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
             (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
        out = []
        sides = {
            'front': (4, 5, 6, 7), 'back': (1, 0, 3, 2), 'left': (0, 4, 7, 3),
            'right': (5, 1, 2, 6), 'top': (7, 6, 2, 3), 'bottom': (0, 1, 5, 4),
        }
        for k, (a, b, c, d) in sides.items():
            if k in faces and faces[k] is None:
                continue
            out += self.quad(p[a], p[b], p[c], p[d], col(k))
        return out

    def prism(self, outline, y0, y1, color, top=None, bottom=None, side=None):
        """Extrude a 2D outline in the XZ plane (x, z points; any winding,
        simple polygon, may be concave) from height y0 to y1. Separate colours
        for top / bottom / sides optional (None = `color`; False = leave out)."""
        pts = list(outline)
        if _area2([(x, -z) for x, z in pts]) < 0:   # make it CCW seen from above (+Y)
            pts.reverse()
        out = []
        if top is not False:
            out += self.polygon([(x, y1, z) for x, z in pts], top or color, normal=(0, 1, 0))
        if bottom is not False:
            out += self.polygon([(x, y0, z) for x, z in pts], bottom or color, normal=(0, -1, 0))
        if side is not False:
            n = len(pts)
            for i in range(n):
                (xa, za), (xb, zb) = pts[i], pts[(i + 1) % n]
                out += self.quad((xa, y0, za), (xb, y0, zb), (xb, y1, zb), (xa, y1, za), side or color)
        return out

    def extrude_xy(self, outline, z0, z1, color, front=None, back=None, side=None):
        """Extrude a 2D outline in the XY plane (x, y points) from z0 to z1
        (z1 = front). Good for flat things seen from the front: handhelds,
        cartridges, cabinet side panels."""
        pts = list(outline)
        if _area2(pts) < 0:
            pts.reverse()                     # CCW seen from +Z
        out = []
        if front is not False:
            out += self.polygon([(x, y, z1) for x, y in pts], front or color, normal=(0, 0, 1))
        if back is not False:
            out += self.polygon([(x, y, z0) for x, y in pts], back or color, normal=(0, 0, -1))
        if side is not False:
            n = len(pts)
            for i in range(n):
                (xa, ya), (xb, yb) = pts[i], pts[(i + 1) % n]
                out += self.quad((xa, ya, z1), (xa, ya, z0), (xb, yb, z0), (xb, yb, z1), side or color)
        return out

    def extrude_yz(self, outline, x0, x1, color, right=None, left=None, side=None):
        """Extrude a 2D outline in the ZY plane (z, y points) from x0 to x1
        (x1 = right). Good for side profiles: wedge-shaped consoles,
        cabinets."""
        pts = list(outline)
        if _area2([(-z, y) for z, y in pts]) < 0:
            pts.reverse()                     # CCW seen from +X
        out = []
        if right is not False:
            out += self.polygon([(x1, y, z) for z, y in pts], right or color, normal=(1, 0, 0))
        if left is not False:
            out += self.polygon([(x0, y, z) for z, y in pts], left or color, normal=(-1, 0, 0))
        if side is not False:
            n = len(pts)
            for i in range(n):
                (za, ya), (zb, yb) = pts[i], pts[(i + 1) % n]
                out += self.quad((x1, ya, za), (x0, ya, za), (x0, yb, zb), (x1, yb, zb), side or color)
        return out

    def cylinder(self, cx, cz, r, y0, y1, color, segments=12, top=None, bottom=None, side=None):
        """Upright cylinder (Y axis)."""
        pts = [(cx + r * math.cos(2 * math.pi * i / segments),
                cz + r * math.sin(2 * math.pi * i / segments)) for i in range(segments)]
        return self.prism(pts, y0, y1, color, top=top, bottom=bottom, side=side)

    def cylinder_z(self, cx, cy, r, z0, z1, color, segments=12, front=None, back=None, side=None):
        """Cylinder along Z (a button seen from the front, a disc on a wall)."""
        pts = [(cx + r * math.cos(2 * math.pi * i / segments),
                cy + r * math.sin(2 * math.pi * i / segments)) for i in range(segments)]
        return self.extrude_xy(pts, z0, z1, color, front=front, back=back, side=side)

    def cylinder_x(self, cz, cy, r, x0, x1, color, segments=12, right=None, left=None, side=None):
        """Cylinder along X."""
        pts = [(cz + r * math.cos(2 * math.pi * i / segments),
                cy + r * math.sin(2 * math.pi * i / segments)) for i in range(segments)]
        return self.extrude_yz(pts, x0, x1, color, right=right, left=left, side=side)

    @staticmethod
    def rounded_rect(x0, y0, x1, y1, r, segments=3):
        """A 2D rounded rectangle outline (for extrude_xy / prism)."""
        r = min(r, (x1 - x0) / 2, (y1 - y0) / 2)
        pts = []
        corners = [(x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180), (x1 - r, y0 + r, 270)]
        for cx, cy, a0 in corners:
            for s in range(segments + 1):
                a = math.radians(a0 + 90 * s / segments)
                pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        return pts

    def decal_xy(self, outline, z, color, lift=0.02):
        """A flat coloured area (label, screen, stripe) on a front-facing
        surface at depth z: drawn `lift` cm in front of it."""
        return self.polygon([(x, y, z + lift) for x, y in outline], color, normal=(0, 0, 1))

    def decal_xz(self, outline, y, color, lift=0.02):
        """A flat coloured area on an upward-facing surface at height y."""
        return self.polygon([(x, y + lift, z) for x, z in outline], color, normal=(0, 1, 0))

    # ----------------------------------------------------------- editing
    def transform(self, tri_ids, fn):
        """Apply fn((x, y, z)) -> (x, y, z) to the vertices of these
        triangles (vertices are shared only within identical positions, so
        moving a part may detach it from others at the same spot: build
        parts in place where possible)."""
        ids = set()
        for t in tri_ids:
            ia, ib, ic, _ = self.tris[t]
            ids.update((ia, ib, ic))
        remap = {}
        for i in ids:
            p = fn(self.verts[i])
            remap[i] = len(self.verts)
            self.verts.append((round(p[0], 4), round(p[1], 4), round(p[2], 4)))
        for t in tri_ids:
            ia, ib, ic, c = self.tris[t]
            self.tris[t] = (remap[ia], remap[ib], remap[ic], c)
        self._vmap = {}

    @staticmethod
    def rot_y(deg):
        a = math.radians(deg)
        c, s = math.cos(a), math.sin(a)
        return lambda p: (p[0] * c + p[2] * s, p[1], -p[0] * s + p[2] * c)

    @staticmethod
    def rot_x(deg, cy=0.0, cz=0.0):
        a = math.radians(deg)
        c, s = math.cos(a), math.sin(a)
        return lambda p: (p[0], cy + (p[1] - cy) * c - (p[2] - cz) * s, cz + (p[1] - cy) * s + (p[2] - cz) * c)

    @staticmethod
    def move(dx, dy, dz):
        return lambda p: (p[0] + dx, p[1] + dy, p[2] + dz)

    # ----------------------------------------------------------- output
    def stats(self):
        used = sorted({t[3] for t in self.tris if t[3] != IMAGE})
        xs = [v[0] for v in self.verts] or [0]
        ys = [v[1] for v in self.verts] or [0]
        zs = [v[2] for v in self.verts] or [0]
        parts = {}
        for t in range(len(self.tris)):
            parts[self.part_of(t)] = parts.get(self.part_of(t), 0) + 1
        return {
            'triangles': len(self.tris),
            'vertices': len({i for t in self.tris for i in t[:3]}),
            'colors': len(used),
            'image_triangles': sum(1 for t in self.tris if t[3] == IMAGE),
            'image_aspect': round(self.image_frames[0][0] / self.image_frames[0][1], 4) if self.image_frames else None,
            'parts': parts,
            'size_cm': (round(max(xs) - min(xs), 2), round(max(ys) - min(ys), 2), round(max(zs) - min(zs), 2)),
            'min_y': round(min(ys), 3),
        }

    def save(self, path=None):
        """Write <path or assets/models/<kind>s/<name>>.obj and .mtl; returns the .obj path."""
        if path is None:
            path = os.path.join(ROOT, 'assets', 'models', KIND_DIRS[self.kind], self.name + '.obj')
        os.makedirs(os.path.dirname(path), exist_ok=True)
        base = os.path.splitext(os.path.basename(path))[0]
        # drop unused vertices, renumber
        used = sorted({i for t in self.tris for i in t[:3]})
        newi = {o: n + 1 for n, o in enumerate(used)}
        colors = sorted({t[3] for t in self.tris if t[3] != IMAGE})
        if any(t[3] == IMAGE for t in self.tris):
            colors.append(IMAGE)
        parts = ['body'] + sorted({p for p in self.parts.values() if p != 'body'})
        s = self.stats()
        with open(path, 'w', newline='\n') as f:
            f.write('# X7 Game low-poly model: %s (%s)\n' % (self.name, self.kind))
            f.write('# %d triangles, %d vertices, %d colours (RGB565); cm, Y up, front +Z\n'
                    % (s['triangles'], s['vertices'], s['colors']))
            if s['image_aspect']:
                f.write('# image_aspect %.4f (width / height of the picture area)\n' % s['image_aspect'])
            f.write('mtllib %s.mtl\no %s\n' % (base, self.name))
            for o in used:
                v = self.verts[o]
                f.write('v %.4f %.4f %.4f\n' % v)
            vt = []
            for t in sorted(self.uvs):
                if self.tris[t][3] == IMAGE:
                    for uv in self.uvs[t]:
                        f.write('vt %.5f %.5f\n' % uv)
                    vt.append(t)
            vti = {t: 1 + 3 * n for n, t in enumerate(vt)}
            for p in parts:
                tl = [t for t in range(len(self.tris)) if self.part_of(t) == p]
                if not tl:
                    continue
                f.write('g %s\n' % p)
                for c in colors:
                    sel = [t for t in tl if self.tris[t][3] == c]
                    if not sel:
                        continue
                    f.write('usemtl %s\n' % (c if c == IMAGE else color_name(c)))
                    for t in sel:
                        ia, ib, ic = self.tris[t][:3]
                        if c == IMAGE:
                            k = vti[t]
                            f.write('f %d/%d %d/%d %d/%d\n' % (newi[ia], k, newi[ib], k + 1, newi[ic], k + 2))
                        else:
                            f.write('f %d %d %d\n' % (newi[ia], newi[ib], newi[ic]))
        with open(os.path.splitext(path)[0] + '.mtl', 'w', newline='\n') as f:
            f.write('# X7 Game model colours: every one an exact RGB565 colour\n')
            for c in colors:
                if c == IMAGE:
                    fb = self.image_fallback
                    f.write('# the game\'s picture; Kd is the colour drawn when there is none\n')
                    f.write('newmtl image\nKd %.6f %.6f %.6f\nKa 0 0 0\nKs 0 0 0\nillum 1\nmap_Kd image.png\n\n'
                            % (fb[0] / 255, fb[1] / 255, fb[2] / 255))
                    continue
                f.write('newmtl %s\nKd %.6f %.6f %.6f\nKa 0 0 0\nKs 0 0 0\nillum 1\n\n'
                        % (color_name(c), c[0] / 255, c[1] / 255, c[2] / 255))
        return path


def load_model(path):
    """Read an OBJ written by Model.save. Returns a dict:
      verts: [(x, y, z)], uvs: [(u, v)],
      tris: [(i0, i1, i2, (r, g, b), part, uv)] where uv is None or the
            three uv indices of an image-area triangle (its colour is then
            the fallback colour),
      image_aspect: width / height of the picture area or None."""
    verts, uvs, tris, mats = [], [], [], {}
    cur, cur_name, part, aspect = (200, 200, 200), '', 'body', None
    d = os.path.dirname(path)
    with open(path) as f:
        lines = f.read().splitlines()
    for ln in lines:
        if ln.startswith('mtllib '):
            mp = os.path.join(d, ln.split(None, 1)[1].strip())
            if os.path.exists(mp):
                name = None
                for ml in open(mp).read().splitlines():
                    if ml.startswith('newmtl '):
                        name = ml.split(None, 1)[1].strip()
                    elif ml.startswith('Kd ') and name:
                        r, g, b = (float(x) for x in ml.split()[1:4])
                        mats[name] = (int(round(r * 255)), int(round(g * 255)), int(round(b * 255)))
        elif ln.startswith('# image_aspect '):
            aspect = float(ln.split()[2])
    for ln in lines:
        p = ln.split()
        if not p:
            continue
        if p[0] == 'v':
            verts.append((float(p[1]), float(p[2]), float(p[3])))
        elif p[0] == 'vt':
            uvs.append((float(p[1]), float(p[2])))
        elif p[0] == 'g':
            part = p[1] if len(p) > 1 else 'body'
        elif p[0] == 'usemtl':
            cur_name = p[1]
            cur = mats.get(p[1], (200, 200, 200))
        elif p[0] == 'f':
            idx = [int(x.split('/')[0]) - 1 for x in p[1:]]
            tix = [int(x.split('/')[1]) - 1 if '/' in x and x.split('/')[1] else None for x in p[1:]]
            img = cur_name == IMAGE and None not in tix
            for k in range(1, len(idx) - 1):
                tris.append((idx[0], idx[k], idx[k + 1], cur, part,
                             (tix[0], tix[k], tix[k + 1]) if img else None))
    return {'verts': verts, 'uvs': uvs, 'tris': tris, 'image_aspect': aspect}


def load_obj(path):
    """Read an OBJ written by Model.save (or any triangle OBJ + MTL with Kd
    colours): returns (verts, tris) with tris = (i0, i1, i2, (r, g, b))."""
    m = load_model(path)
    return m['verts'], [t[:4] for t in m['tris']]

# SPDX-License-Identifier: GPL-3.0-or-later
"""
check.py - does the game go into its console without passing through it?

    python tools/models/check.py assets/models/systems/<id>.json [--samples 41]

At evenly spaced moments of the insertion (and at the end) it looks for
triangles of the media that cut through triangles of the console, and for
moving parts that cut through the rest of the console. Faces that only
touch (lying flat against each other, meeting at an edge) don't count.
Prints the moments with problems and where; exit status 1 if any.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scene import System  # noqa: E402

EPS = 1e-6
SHRINK = 0.03          # cm: each triangle is pulled in this much, so touching edges don't count


def _sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def shrink(t):
    c = tuple((t[0][i] + t[1][i] + t[2][i]) / 3 for i in range(3))
    out = []
    for p in t:
        d = _sub(p, c)
        l = _dot(d, d) ** 0.5
        k = max(0.0, 1 - min(SHRINK, 0.2 * l) / l) if l > 0 else 0
        out.append(tuple(c[i] + d[i] * k for i in range(3)))
    return out


def _interval(vv, d):
    d0, d1, d2 = d
    v0, v1, v2 = vv

    def isect(a0, a1, a2, e0, e1, e2):
        t0 = a0 + (a1 - a0) * e0 / (e0 - e1)
        t1 = a0 + (a2 - a0) * e0 / (e0 - e2)
        return (min(t0, t1), max(t0, t1))
    if d0 * d1 > 0:
        return isect(v2, v0, v1, d2, d0, d1)
    if d0 * d2 > 0:
        return isect(v1, v0, v2, d1, d0, d2)
    if d1 * d2 > 0 or d0 != 0:
        return isect(v0, v1, v2, d0, d1, d2)
    if d1 != 0:
        return isect(v1, v0, v2, d1, d0, d2)
    if d2 != 0:
        return isect(v2, v0, v1, d2, d0, d1)
    return None


def tri_tri(V, U):
    """True if the triangles cross (Moller 1997); coplanar = no."""
    N1 = _cross(_sub(V[1], V[0]), _sub(V[2], V[0]))
    d1 = -_dot(N1, V[0])
    du = [_dot(N1, u) + d1 for u in U]
    sc = max(1e-12, _dot(N1, N1) ** 0.5)
    du = [0.0 if abs(x) / sc < EPS else x for x in du]
    if (du[0] > 0 and du[1] > 0 and du[2] > 0) or (du[0] < 0 and du[1] < 0 and du[2] < 0):
        return False
    N2 = _cross(_sub(U[1], U[0]), _sub(U[2], U[0]))
    d2 = -_dot(N2, U[0])
    dv = [_dot(N2, v) + d2 for v in V]
    sc = max(1e-12, _dot(N2, N2) ** 0.5)
    dv = [0.0 if abs(x) / sc < EPS else x for x in dv]
    if (dv[0] > 0 and dv[1] > 0 and dv[2] > 0) or (dv[0] < 0 and dv[1] < 0 and dv[2] < 0):
        return False
    if all(x == 0 for x in du) or all(x == 0 for x in dv):
        return False                              # coplanar: touching, not crossing
    D = _cross(N1, N2)
    ax = max(range(3), key=lambda i: abs(D[i]))
    i1 = _interval([v[ax] for v in V], dv)
    i2 = _interval([u[ax] for u in U], du)
    if i1 is None or i2 is None:
        return False
    return not (i1[1] < i2[0] + 1e-9 or i2[1] < i1[0] + 1e-9)


def _box(t):
    return (min(p[0] for p in t), min(p[1] for p in t), min(p[2] for p in t),
            max(p[0] for p in t), max(p[1] for p in t), max(p[2] for p in t))


def _overlap(a, b):
    return all(a[i] <= b[i + 3] and b[i] <= a[i + 3] for i in range(3))


def crossings(scene, groups_a, groups_b, limit=6):
    """Pairs of crossing triangles between triangle groups a and b."""
    v = scene['verts']
    ta, tb = [], []
    for k, t in enumerate(scene['tris']):
        g = scene['who'][k]
        tri = shrink([v[t[0]], v[t[1]], v[t[2]]])
        if g in groups_a:
            ta.append((tri, _box(tri), g))
        if g in groups_b:
            tb.append((tri, _box(tri), g))
    hits = []
    count = 0
    for A, ba, ga in ta:
        for B, bb, gb in tb:
            if ga == gb or not _overlap(ba, bb):
                continue
            if tri_tri(A, B):
                count += 1
                if len(hits) < limit:
                    c = tuple(round(sum(p[i] for p in A) / 3, 2) for i in range(3))
                    hits.append('%s x %s near (%.2f, %.2f, %.2f)' % (ga, gb, *c))
    return count, hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('system')
    ap.add_argument('--samples', type=int, default=41)
    a = ap.parse_args()
    s = System(a.system)
    groups = sorted(set('console:' + t[4] for t in s.console['tris']))
    moving = ['console:' + n for n in s.parts]
    fixed = [g for g in groups if g not in moving]
    bad = 0
    for k in range(a.samples):
        t = k / (a.samples - 1)
        sc = s.scene(t)
        n1, h1 = crossings(sc, {'media'}, set(groups))
        n2, h2 = crossings(sc, set(moving), set(fixed)) if moving else (0, [])
        n3, h3 = crossings(sc, set(moving), set(moving)) if len(moving) > 1 else (0, [])
        if n1 or n2 or n3:
            bad += 1
            print('t=%.3f: %d media/console, %d part/body, %d part/part crossings' % (t, n1, n2, n3))
            for h in h1 + h2 + h3:
                print('    ' + h)
    if bad:
        print('%s: problems at %d of %d moments' % (os.path.basename(a.system), bad, a.samples))
        sys.exit(1)
    print('%s: clean at all %d moments (nothing passes through anything)' % (os.path.basename(a.system), a.samples))


if __name__ == '__main__':
    main()

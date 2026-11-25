# SPDX-License-Identifier: GPL-3.0-or-later
"""
scene.py - a system file: how a game (cartridge, disc, card, board) goes
into its console, for the frontend's game list. When a game is selected, its
media moves along a path into the console while lids, doors and trays open
and close.

assets/models/systems/<id>.json (paths relative to that file):

{
  "console": "../consoles/psx.obj",
  "media":   "../media/psx.obj",
  "view":    [35, 30],                 # camera yaw, pitch that shows the insertion well
  "parts": {                           # the console's moving parts (OBJ groups), modelled closed
    "lid":  {"hinge": {"pivot": [0, 4.5, -6], "axis": [1, 0, 0], "angle": -75}},
    "tray": {"slide": [0, 0, 14]}      # open = moved by this vector (cm)
  },
  "path": [                            # poses of the media in console space (cm, degrees)
    {"pos": [0, 20, 15], "rot": [0, 0, 0]},     # 0: ready, outside the console, lined up
    {"pos": [0, 6, -1],  "rot": [-90, 0, 0]},   # ...
    {"pos": [0, 4.6, -1], "rot": [-90, 0, 0]}   # last: seated
  ],
  "steps": [                           # played in order; actions in one step run together
    {"time": 0.35, "open": ["lid"]},
    {"time": 0.6,  "media": [0, 2]},             # move from waypoint 0 to 2 (through 1)
    {"time": 0.35, "close": ["lid"]}
  ]
}

A pose: the media model (origin at its bottom centre, front +Z) is turned
by rot[0] degrees about X, then rot[1] about Y, then rot[2] about Z (right-
hand rule: positive = counter-clockwise looking from the axis' positive
end towards the origin), then moved to pos. Poses in between are linear in
position and angles, eased (smoothstep) over each step. A hinge turns its
part by `angle` degrees about `axis` through `pivot` when open; a slide
moves it by the vector. Parts start closed.
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from x7model import load_model  # noqa: E402


def _rot(p, r):
    x, y, z = p
    a = math.radians(r[0])
    y, z = y * math.cos(a) - z * math.sin(a), y * math.sin(a) + z * math.cos(a)
    a = math.radians(r[1])
    x, z = x * math.cos(a) + z * math.sin(a), -x * math.sin(a) + z * math.cos(a)
    a = math.radians(r[2])
    x, y = x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a)
    return (x, y, z)


def pose_fn(pose):
    pos, rot = pose['pos'], pose.get('rot', [0, 0, 0])

    def f(p):
        q = _rot(p, rot)
        return (q[0] + pos[0], q[1] + pos[1], q[2] + pos[2])
    return f


def _axis_rot(p, pivot, axis, deg):
    l = math.sqrt(sum(a * a for a in axis))
    k = [a / l for a in axis]
    v = [p[i] - pivot[i] for i in range(3)]
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    kv = sum(k[i] * v[i] for i in range(3))
    kxv = (k[1] * v[2] - k[2] * v[1], k[2] * v[0] - k[0] * v[2], k[0] * v[1] - k[1] * v[0])
    return tuple(pivot[i] + v[i] * c + kxv[i] * s + k[i] * kv * (1 - c) for i in range(3))


def part_fn(spec, state):
    if 'hinge' in spec:
        h = spec['hinge']
        return lambda p: _axis_rot(p, h['pivot'], h['axis'], h['angle'] * state)
    if 'slide' in spec:
        d = spec['slide']
        return lambda p: (p[0] + d[0] * state, p[1] + d[1] * state, p[2] + d[2] * state)
    raise ValueError('part needs "hinge" or "slide": %r' % spec)


def _smooth(f):
    f = max(0.0, min(1.0, f))
    return f * f * (3 - 2 * f)


def _lerp_pose(a, b, f):
    ra, rb = a.get('rot', [0, 0, 0]), b.get('rot', [0, 0, 0])
    return {'pos': [a['pos'][i] + (b['pos'][i] - a['pos'][i]) * f for i in range(3)],
            'rot': [ra[i] + (rb[i] - ra[i]) * f for i in range(3)]}


class System:
    def __init__(self, path):
        self.path = path
        with open(path) as f:
            s = json.load(f)
        base = os.path.dirname(os.path.abspath(path))
        self.spec = s
        self.console = load_model(os.path.normpath(os.path.join(base, s['console'])))
        self.media = load_model(os.path.normpath(os.path.join(base, s['media'])))
        self.parts = s.get('parts', {})
        self.path_pts = s['path']
        self.steps = s.get('steps', [])
        self.view = s.get('view', [35, 22])
        have = {t[4] for t in self.console['tris']}
        for name in self.parts:
            if name not in have:
                raise ValueError('part "%s" is not a group in the console OBJ (it has: %s)' % (name, sorted(have)))
        for st in self.steps:
            for n in st.get('open', []) + st.get('close', []):
                if n not in self.parts:
                    raise ValueError('step uses unknown part "%s"' % n)
            if 'media' in st:
                a, b = st['media']
                if not (0 <= a < len(self.path_pts) and 0 <= b < len(self.path_pts)):
                    raise ValueError('step media range %r outside the path' % (st['media'],))
        self.total = sum(st['time'] for st in self.steps) or 1.0

    def state(self, t):
        """(media pose, {part: 0..1 open}) at t = 0 (start) .. 1 (end)."""
        T = t * self.total
        parts = {n: 0.0 for n in self.parts}
        pose = self.path_pts[0]
        acc = 0.0
        for st in self.steps:
            dur = st['time']
            if T <= acc:
                break
            f = _smooth((T - acc) / dur) if dur > 0 else 1.0
            for n in st.get('open', []):
                parts[n] = f
            for n in st.get('close', []):
                parts[n] = 1.0 - f
            if 'media' in st:
                a, b = st['media']
                if a == b:
                    pose = self.path_pts[a]
                else:
                    step = 1 if b > a else -1
                    seg = list(range(a, b, step))
                    x = f * len(seg)
                    k = min(int(x), len(seg) - 1)
                    pose = _lerp_pose(self.path_pts[seg[k]], self.path_pts[seg[k] + step], x - k)
            acc += dur
        return pose, parts

    def scene(self, t, with_media=True):
        """One combined model at time t: dict like load_model plus 'who'
        per triangle ('console:<part>' or 'media')."""
        pose, parts = self.state(t)
        verts, uvs, tris, who = [], [], [], []
        cv = self.console['verts']
        fns = {n: part_fn(self.parts[n], parts[n]) for n in self.parts}
        vmap = {}
        for ia, ib, ic, col, part, uv in self.console['tris']:
            idx = []
            for i in (ia, ib, ic):
                key = (i, part)
                if key not in vmap:
                    vmap[key] = len(verts)
                    verts.append(fns[part](cv[i]) if part in fns else cv[i])
                idx.append(vmap[key])
            tris.append((idx[0], idx[1], idx[2], col, part, uv))
            who.append('console:' + part)
        uvs.extend(self.console['uvs'])
        if with_media:
            mf = pose_fn(pose)
            off, uoff = len(verts), len(uvs)
            verts.extend(mf(p) for p in self.media['verts'])
            uvs.extend(self.media['uvs'])
            for ia, ib, ic, col, part, uv in self.media['tris']:
                tris.append((ia + off, ib + off, ic + off, col, 'media',
                             None if uv is None else tuple(u + uoff for u in uv)))
                who.append('media')
        return {'verts': verts, 'uvs': uvs, 'tris': tris, 'who': who, 'pose': pose, 'parts': parts}

# Graphics performance (measured)

Measured on the developer's R36SX (v2.7 hardware, V2.6 bootloader) with X7
Game 0.3.1 and its `x7-bench3d` tool, 2026-11-22. The tool was removed from
the system afterwards; its source is kept in the history:
[x7-bench3d.c at 06d62fa](https://github.com/MarsInsanity/X7Game/blob/06d62faeaa1e2c3818f7ce83e32ff6a3553317f9/br2-external/package/x7-hwmon/src/x7-bench3d.c)
(build it with `-lm`; the 0.3.1 release image still contains it). The
console has **no 3D GPU**: all 3D below is software rendering on the CPU
(MIPS 74Kc, one core, 900 MHz, hardware FPU).

## 1. Filling the whole 640x480 screen

| Screen mode | Time per full frame | Max frames/s (nothing drawn) |
|---|---|---|
| 16-bit (RGB565) | 4.2 ms | 237 |
| 32-bit (ARGB8888) | 8.5 ms | 118 |

The framebuffer is uncached memory, so every full-screen copy costs this
much. 16-bit halves it.

## 2. Real-time 3D (spinning model)

Model: a torus, 64x64 texture (affine mapping, nearest), per-vertex
(Gouraud) lighting, 16-bit z-buffer, back-face culling; rendered into a
16-bit buffer in normal memory, then copied to the screen ("copy ms").
"Drawn" = triangles facing the camera (about half).

| Render size | Screen | Model triangles | Drawn | fps | 3D ms | Copy ms |
|---|---|---|---|---|---|---|
| 320x240 (scaled 2x) | 16-bit | 12 | 2 | 129.7 | 2.6 | 5.1 |
| 320x240 (scaled 2x) | 16-bit | 250 | 146 | 101.0 | 4.8 | 5.1 |
| 320x240 (scaled 2x) | 16-bit | 500 | 263 | 94.4 | 5.5 | 5.1 |
| 320x240 (scaled 2x) | 16-bit | 1000 | 510 | 82.4 | 7.0 | 5.1 |
| 320x240 (scaled 2x) | 16-bit | 2000 | 973 | 73.2 | 8.5 | 5.1 |
| 320x240 (scaled 2x) | 16-bit | 4000 | 1919 | 58.2 | 12.0 | 5.2 |
| 320x240 (scaled 2x) | 32-bit | 12 | 2 | 82.7 | 2.6 | 9.5 |
| 320x240 (scaled 2x) | 32-bit | 250 | 146 | 69.9 | 4.8 | 9.5 |
| 320x240 (scaled 2x) | 32-bit | 500 | 263 | 66.7 | 5.5 | 9.5 |
| 320x240 (scaled 2x) | 32-bit | 1000 | 510 | 60.5 | 7.0 | 9.5 |
| 320x240 (scaled 2x) | 32-bit | 2000 | 975 | 55.3 | 8.6 | 9.5 |
| 320x240 (scaled 2x) | 32-bit | 4000 | 1917 | 46.3 | 12.1 | 9.5 |
| 640x480 | 16-bit | 500 | 263 | 42.5 | 15.6 | 7.9 |
| 640x480 | 16-bit | 2000 | 973 | 35.0 | 20.7 | 7.9 |

## 3. Pre-rendered turntable sprites

36 frames of 160x160, drawn straight to the screen (no 3D at run time):

| Screen | 1 sprite | 6 sprites |
|---|---|---|
| 16-bit | 1518 fps | 254 fps |
| 32-bit | 949 fps | 159 fps |

## What this means for the frontend

- **Use 16-bit screen mode.** Copying a frame costs 5 ms instead of 9.5 ms
  (2x-scaled) and leaves more of each 16.7 ms frame (60 fps) for drawing.
- **Real-time 3D at 320x240 (scaled 2x), 60 fps:** up to about **1,000
  drawn triangles** (a model of ~2,000 triangles) measured 73 fps; ~1,900
  drawn (a 4,000-triangle model) still 58 fps. To leave room for the UI,
  input and music playback, aim for **~500 drawn triangles** (models of
  ~1,000 triangles in total) with 64x64-128x128 textures: ~10.6 ms per
  frame.
- **Full 640x480 3D** runs at 35-42 fps: fine for 30 fps animation or a
  smaller 3D area, not for 60 fps full-screen.
- **Pre-rendered turntables are nearly free** (six 160x160 sprites at
  254 fps): the best choice for carousels of consoles and cartridges, and
  they can be rendered in high quality (Blender) beforehand.

Not measured yet (each costs extra): larger textures (128x128, 256x256),
bilinear filtering, perspective-correct texturing, transparency / alpha
blending, several overlapping models (overdraw), and the CPU used by the
rest of the frontend (e.g. MP3 decoding). One model filled roughly half
the 320x240 view; fill cost grows with how much of the screen the 3D
covers.

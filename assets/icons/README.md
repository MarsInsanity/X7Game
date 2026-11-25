# Frontend app icons

One-colour SVG icons for the frontend's apps, on a 48 x 48 grid:

| File | App |
|---|---|
| `retroarch.svg` | RetroArch: a game pad |
| `pcsx4all.svg` | PCSX4All (its settings app): a game disc with a gear |
| `music.svg` | Music: two beamed notes |
| `video.svg` | Video: a film frame with a play triangle |
| `ebook.svg` | E-Book: an open book |
| `photos.svg` | Photos: a picture frame with mountains and the sun |

Each icon is one `<path>` with one fill colour:
- **Colour:** the frontend's accent, `#A596E7`, a light SNES-like purple. It is
  exact in RGB565, so it does not shift on the 16-bit screen. It reads best on
  dark to mid-dark grey: at least 3:1 contrast up to `#505050`.
- **Simple to draw:** there are no strokes, gradients, masks or transforms,
  so a simple SVG rasteriser draws them correctly.
- **Cut-outs** (the D-pad, the disc's hole, the play triangle) are holes in
  the path, so the background shows through.
- **Original drawings:** none copies an existing logo.

`mkicons.py` writes all six. To change the colour, run it with a different one:

    python assets/icons/mkicons.py "#RRGGBB"

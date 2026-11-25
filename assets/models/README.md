# Frontend 3D models

Low-poly models of each system's console and its cartridge (or disc, card,
disk or board) for the frontend carousel.

- `consoles/<id>.obj` + `.mtl`: the 24 consoles (`arcade` is an upright cabinet)
- `media/<id>.obj` + `.mtl`: the 24 cartridges/media (disc systems are a CD in
  a jewel case, `fds` is a disk card, `arcade` is a game board)
- `src/<kind>_<id>.py`: the script that builds each model; run it to rebuild
  the OBJ/MTL (`python assets/models/src/console_nes.py`)
- `previews/`: renders at the frontend's 320x240 in RGB565, doubled to 640x480,
  plus the two contact sheets

Ids are the ROM folder names: nes, fds, snes, gb, gbc, gba, mastersystem,
megadrive, gamegear, sg1000, segacd, sega32x, pcengine, pcenginecd, ngp, ngpc,
wswan, wswanc, atari2600, atari7800, lynx, psx, neogeo, arcade.

## Conventions

- Centimetres at real-world size. Y is up, the front faces +Z, the origin is
  the bottom centre (the model stands on y = 0).
- Triangles only, counter-clockwise seen from outside (back faces can be
  culled).
- Flat colours, no textures. Each material `c_RRGGBB` is an exact RGB565
  colour, and each model uses at most 14 colours.
- Triangle limits: consoles and the arcade cabinet 600, handhelds 450,
  cartridges/media 250.
- No text, logos or trademarks. Labels are plain coloured areas.

## Tools (`tools/models/`)

- `x7model.py`: the modelling library the generators use (boxes, prisms,
  extrusions, cylinders, decals; it snaps colours to RGB565 and writes OBJ/MTL)
- `render.py`: a software preview the way the frontend will draw it.
  `--nocull` paints back faces magenta to find wrongly wound triangles.
- `sheet.py`: a contact sheet of previews with names

## Notes for the renderer

`render.py` interpolates depth linearly in screen space, not
perspective-correct. With that, decals (labels, screens) lying over large,
thin triangles can break up at steep angles. The generators avoid this by
cutting such faces into small pieces or by building the detail into the
geometry. A frontend rasteriser that has the same depth behaviour will draw
these models cleanly. A perspective-correct depth buffer (1/z) would be more
forgiving still.

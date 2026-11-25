# Frontend 3D models

Low-poly models of each system's console and its cartridge (or disc, card,
disk or board) for the frontend game list. When a game is selected, its
media moves into the console, while lids, doors and trays open and close.

- `consoles/<id>.obj` + `.mtl`: the 24 consoles (`arcade` is an upright cabinet)
- `media/<id>.obj` + `.mtl`: the 24 cartridges/media. The disc systems (segacd,
  pcenginecd, psx) are bare discs, `fds` is a disk card, and `arcade` is a game board
- `systems/<id>.json`: how that system's media goes into its console (see below)
- `src/<kind>_<id>.py`: the script that builds each model. Run it to rebuild
  the OBJ/MTL (`python assets/models/src/console_nes.py`). `console_segacd.py`
  and `console_sega32x.py` add the Genesis from `consoles/megadrive.obj` (under
  the 32X, on top of the Sega CD), so build that first
- `previews/`: renders at the frontend's 320x240 in RGB565, doubled to 640x480:
  - `console_*` and `media_*`, one per model
  - `system_*`, a four-frame insertion strip per system
  - contact sheets: `sheet_console`, `sheet_media`, and `sheet_system_1` to `_4`

Ids are the ROM folder names: nes, fds, snes, gb, gbc, gba, mastersystem,
megadrive, gamegear, sg1000, segacd, sega32x, pcengine, pcenginecd, ngp, ngpc,
wswan, wswanc, atari2600, atari7800, lynx, psx, neogeo, arcade.

## Conventions

- Centimetres at real-world size. Y is up, the front faces +Z, and the origin
  is the bottom centre (the model stands on y = 0).
- Triangles only, wound counter-clockwise seen from outside, so back faces can
  be culled.
- Flat colours. Each material `c_RRGGBB` is an exact RGB565 colour, and each
  model uses at most 14 of them.
- Triangle limits: consoles and the arcade cabinet 600, handhelds 450, and
  cartridges/media 250. Moving parts count towards the limit. The one
  exception is `sega32x`, the 32X plugged into a Genesis: 850.
- No text, logos or trademarks.
- The shapes and proportions are taken from photos of the real hardware on
  Wikimedia Commons.

## The game's picture

Every media model has one picture area, where the frontend draws the game's
box art or label:
- **Cartridges and cards:** the label.
- **Discs:** the printed side, as a ring around the hole.
- **The arcade board:** a sticker.

How the picture area is defined:
- Its triangles use the material `image`, and they carry texture coordinates
  (`vt`, `f v/t`).
- u runs from left to right, and v from bottom to top (the OBJ convention), so
  the picture appears upright as the media stands facing +Z.
- The comment `# image_aspect W/H` in the OBJ gives the area's shape, so the
  frontend can crop the picture to fit.
- The MTL gives `image` a fallback colour (`Kd`) for when there is no picture,
  and a placeholder `map_Kd image.png`.

## Moving parts

Lids, doors, dust flaps, trays and switches are OBJ groups (`g lid`, `g tray`,
...), modelled in their closed position. Everything else is the group `body`.
The system file says how each part moves.

## System files (`systems/<id>.json`)

```json
{
  "console": "../consoles/psx.obj",
  "media": "../media/psx.obj",
  "view": [28, 34],
  "parts": {"lid": {"hinge": {"pivot": [0, 5.5, -7.95], "axis": [1, 0, 0], "angle": -90}}},
  "path": [
    {"pos": [0, 11.5, 5.0], "rot": [-30, 0, 0]},
    {"pos": [0, 9.0, 5.0], "rot": [-90, 0, 0]},
    {"pos": [0, 3.76, 5.0], "rot": [-90, 0, 0]}
  ],
  "steps": [
    {"time": 0.35, "open": ["lid"]},
    {"time": 0.75, "media": [0, 2]},
    {"time": 0.3, "close": ["lid"]}
  ]
}
```

- **`view`:** the camera yaw and pitch, in degrees, that show the insertion well.
- **`parts`:** how each moving part opens:
  - `hinge`: turns the part by `angle` degrees about `axis`, through `pivot`.
  - `slide`: moves the part by the vector given.
- **`path`:** poses of the media in the console's space.
  - Waypoint 0 is the ready pose, outside the console and lined up with the slot.
  - The last waypoint is seated.
  - A pose turns the media by `rot` (degrees: about X, then Y, then Z), then
    moves it to `pos`.
- **`steps`:** played in order.
  - The actions in one step run together over its `time`, in seconds, with
    smoothstep easing.
  - `media: [a, b]` moves the media along the path from waypoint a to waypoint b.
  - Poses in between are linear in position and angles.

The media and the moving parts are checked so that nothing passes through
anything at any moment.

## Tools (`tools/models/`)

- **`x7model.py`:** the modelling library the generators use.
  - It provides boxes, prisms, extrusions, cylinders and decals; picture areas
    (`image_xy`, `image_rect`, `image_ring`, `image_polygon`); and moving parts
    (`with m.part('lid'):`).
  - It snaps colours to RGB565 and writes OBJ/MTL. `load_model` reads OBJ/MTL
    back.
- **`scene.py`:** loads a system file, and gives the media pose and part states
  at any moment (`System.state(t)`), or the whole scene as one model
  (`System.scene(t)`).
- **`render.py`:** a software preview drawn the way the frontend will draw it,
  with perspective-correct depth and texture.
  - `--system FILE --frames 0,0.35,0.7,1`: an insertion strip.
  - `--image PNG`: a picture for the image areas. Without it, a test card is
    drawn: red top-left, green top-right, blue bottom-left, yellow
    bottom-right, and a white arrow pointing up.
  - `--nocull`: paints back faces magenta, to find wrongly wound triangles.
  - `--cut "x>0"`: cuts the model open, to look into slots.
- **`check.py SYSTEM.json`:** checks the whole insertion at 41 moments for
  media crossing the console, and for moving parts crossing the body or each
  other. Faces that only touch don't count.
- **`sheet.py [--tile WxH] OUT COLS LABEL=png ...`:** a contact sheet of
  previews with names.

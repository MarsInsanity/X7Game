# X7 Game

A small, fast Linux for the **R36SX / R36S V2.6 / R36S V2.7** handhelds, the
R36S look-alikes built on the **HiChip E3100** (MIPS 74Kc, one core, 256 MB
RAM). X7 Game replaces the locked-down stock "hOS" (Linux 4.4) with a modern
**Linux 7.2** kernel and a **Buildroot** system, started straight from the SD
card. The console's flash chip is never touched: put the stock card back and
the console is exactly as it was.

The base OS is done; **emulation is being added now**. Until the real
frontend arrives, the screen shows a simple text-mode **test game list**
that browses `X7DATA/roms` and starts each game in its emulator (see
[Playing games](#playing-games-test-stage)).

> **Status:** the base OS (boot, screen, buttons, sound, data partition, USB
> shell, updates) works on a real R36SX. Emulation is new and still being
> tested. Please report what you see (see
> [Reporting problems](#reporting-problems)).

## What it does

| | |
|---|---|
| Boot | Linux 7.2 + BusyBox from the SD card (TF1), read-only squashfs root, no initramfs. Target: under 10 s to the console |
| Image | one `.img` of about 54 MiB (FAT32 boot partition + root file system) |
| Data partition | made at the first start on the rest of the card: **X7DATA** (exFAT), a second drive on a PC, for ROMs, BIOS files, saves, music, videos and photos (RecalBox folder names). Flashing a newer image keeps it |
| Updates | copy a `.x7update` file into X7DATA and switch on: installed into the second system slot, verified, then the console restarts into it; data and settings stay, the previous version stays available |
| Screen | the boot log, then the test game list (`x7-browser`); its **System information** page shows the hardware state and the latest hardware events |
| Games | RetroArch (a slim build made for this console) with libretro cores for the 8/16-bit and handheld systems, Game Boy Advance and arcade; PCSX4All (with an X7 Game port) for the PlayStation |
| Buttons | D-pad, A, B, X, Y, L1, L2, R1, R2, SELECT, START, FN, VOL+, VOL-, POWER; every press and release is logged (`/run/x7-events.log`, kept to its newest 64-256 KiB). L2, R2, VOL+, VOL-, FN, POWER and the headphone jack are interrupt-driven; the main pad is sampled every 16 ms (8 ms during games). The emulators see them as one gamepad, "X7 Game Gamepad". The analog sticks are wired to the D-pad and face buttons |
| Display | 640x480, 32-bit colour (16.7 million colours) framebuffer console, 16-bit in games; the panel timing is the one the bootloader sets up |
| Sound | ALSA sound card (speaker and headphone jack). `x7-soundtest` plays test tones |
| Brightness | FN + VOL+ / VOL- (remembered across restarts). Optional idle dimming and screen-off in `x7game.cfg` (`dim_after_s`, `screen_off_after_s`, `dim_level`; off by default): any button brings the screen back |
| Headphones | automatic switching: headphones in = speaker off, headphones out = speaker on, printed on every change. The speaker amplifier is also off while the volume is 0 |
| DC port | charger plugged / unplugged printed; battery % printed whenever it goes up or down |
| OTG port | connected / disconnected printed; a **root shell over USB serial** (PuTTY) |
| Power | POWER pressed = clean power-off; at power-on the console switches straight off again if the battery is at or below the cutoff and no charger is plugged in |
| Crashes | a kernel driver bug (an "oops") stops only the program that hit it: the game list comes back and the details reach the logs |
| TF2 | not supported: the R36SX's second card slot can't be used (see [Known limits](#known-limits)) |
| Memory | about 114 MiB for programs, plus compressed memory (zram, 32 MiB by default, `zram_mb` in `x7game.cfg`, 32-128 or 0 = off) so big games aren't stopped when memory runs short |

## Supported consoles

| Console | Image |
|---|---|
| R36SX / R36S running the **V2.6 firmware** (unencrypted boot files), including V2.7 hardware running it | `x7game-r36sx-<version>.img` |
| **"Bootloader protected" V2.7** consoles | `x7game-r36sx-v27protected-<version>.img`, only built when the V2.7 boot key is available (see [Known limits](#known-limits)) |

## Install

1. Download `x7game-r36sx-<version>.img.zip` (or `.img.xz`) from the
   [releases](../../releases) and unzip it.
2. Write the `.img` to a microSD card (2 GB or bigger) with
   [balenaEtcher](https://etcher.balena.io/) or [Rufus](https://rufus.ie/).
   This erases the card, so don't use your stock card. Keep the stock card as
   your way back.
3. Put the card in the **TF1** slot and switch the console on.

The first start takes a few seconds longer: X7 Game turns the rest of the card
into the data partition (see below).

On a PC the card then shows two drives:

- **X7GAME** (48 MB): the boot files. `x7game/x7game.cfg` holds the settings
  (battery cutoffs, headphone polarity, start volume, update battery level,
  zram size). They are all commented out, so X7 Game's defaults apply and
  follow updates; remove the `#` in front of one to change it. One
  `KEY=VALUE` per line, text after `#` is ignored, and a line with an empty
  value keeps the default. Lines the console can't use are
  listed in `boot.log`. `x7game/logs/` holds the logs of the last start
  (`boot.log`) and of the last session (`last-session.log`, written when you
  switch off with POWER).
- **X7DATA** (the rest of the card): your files.

## Data partition (X7DATA)

| Folder | What |
|---|---|
| `roms/<system>/` | games, one folder per system, named like RecalBox: `nes`, `snes`, `gb`, `gbc`, `gba`, `megadrive`, `mastersystem`, `gamegear`, `pcengine`, `psx`, `neogeo`, `fbneo`, ... (list: [data-folders.txt](br2-external/board/r36sx/overlay/usr/share/x7game/data-folders.txt); the systems that run today are under [Playing games](#playing-games-test-stage), the other folders wait for their emulators) |
| `bios/` | BIOS files some systems need |
| `saves/` | game saves and save states |
| `screenshots/` | screenshots |
| `music/`, `videos/`, `photos/` | media |
| `overlays/`, `shaders/`, `system/`, `userscripts/` | for the frontend and emulators (later) |

- It is exFAT (no 4 GB file limit; Windows, macOS and Linux read it). A
  FAT32 X7DATA made on a PC (or by older versions) works too.
- If X7DATA wasn't closed cleanly (the battery ran out, the console hung),
  the console asks at the next start, before the game list, whether to check
  and repair it (A = repair, B = not now; you're asked again next time).
  Over the USB shell: `x7-datarepair`.
- On the console it is mounted at `/share`.
- Missing folders are created again at every start; nothing in it is ever
  deleted.
- **Re-flashing keeps your data:** flashing a newer X7 Game image
  (balenaEtcher, or Rufus in image mode) rewrites only the first part of the
  card. The next start finds X7DATA where it was and only restores its
  partition table entry; it never formats a partition that holds a file
  system. Back up anyway before re-flashing.
- The partition table entry now covers X7DATA exactly to the end of the card.
  Cards made by earlier versions are corrected at the first start (the entry
  was rounded down, and Windows could then offer to format the drive: don't,
  start the console once instead).
- A data partition X7 Game doesn't recognise or finds damaged is left alone
  (never formatted, never mounted); check it on a PC.

## Playing games (test stage)

The game list on the screen is temporary: it exists to test the emulators
until the real X7 Game frontend is written.

1. On a PC, copy your games into **X7DATA** `roms/<system>/` (folder names
   below) and any BIOS files into `bios/`. Zipped cartridge games work.
2. On the console pick a system, then a game, and press **A**.

| Game list | |
|---|---|
| D-pad up / down | move |
| D-pad left / right, L1 / R1 | page up / down |
| A | open the folder / start the game |
| B | back |
| X | start the game with another emulator (systems that have more than one) |

| Folder | System | Emulator | BIOS (in `bios/`) |
|---|---|---|---|
| `nes`, `fds` | NES / Famicom, Famicom Disk System | FCEUmm | `disksys.rom` (FDS only) |
| `snes` | Super Nintendo | Snes9x 2005 | |
| `gb`, `gbc` | Game Boy, Game Boy Color | Gambatte | |
| `gba` | Game Boy Advance | gpSP | `gba_bios.bin` (optional, a built-in one is used otherwise) |
| `mastersystem`, `megadrive`, `gamegear`, `sg1000`, `segacd`, `sega32x` | Sega 8/16-bit, Sega CD, 32X | PicoDrive | `bios_CD_U.bin`, `bios_CD_E.bin`, `bios_CD_J.bin` (Sega CD only) |
| `pcengine`, `pcenginecd` | PC Engine / TurboGrafx-16 (+ CD) | Beetle PCE Fast | `syscard3.pce` (CD only) |
| `ngp`, `ngpc` | Neo Geo Pocket (Color) | RACE | |
| `wswan`, `wswanc` | WonderSwan (Color) | Beetle WonderSwan | |
| `atari2600` | Atari 2600 | Stella 2014 | |
| `atari7800` | Atari 7800 | ProSystem | `7800 BIOS (U).rom` (optional) |
| `lynx` | Atari Lynx | Handy | `lynxboot.img` |
| `neogeo` | Neo Geo | FB Alpha 2012 Neo Geo | `neogeo.zip` (next to the games) |
| `fbneo` | Arcade: CPS-1, CPS-2, Neo Geo | FB Alpha 2012 CPS-1 / CPS-2 / Neo Geo (X picks) | FB Alpha 2012 romsets |
| `psx` | PlayStation (`.cue`/`.bin`, `.chd`, `.pbp`, `.iso`, `.img`) | PCSX4All | `scph1001.bin` (or `scph5501.bin`, `scph7001.bin`, ...; without one a built-in BIOS is used, which most games accept) |

**In a game (RetroArch):** hold **FN** and press

| | | | |
|---|---|---|---|
| X | menu | START | quit to the game list |
| R1 | save state | L1 | load state |
| D-pad left / right | state slot - / + | R2 | fast forward on / off |
| Y | screenshot | B | pause |
| SELECT | reset | | |

**In a PlayStation game (PCSX4All):** B = Cross, A = Circle, X = Triangle,
Y = Square, plus L1/R1/L2/R2, SELECT, START and the D-pad. **FN** opens the
emulator's menu (D-pad to move, A to choose, B back, FN or SELECT back to the
game); **Quit to game list** is at the bottom.

VOL+ / VOL- change the volume and POWER switches off (the game's save is
written first), as everywhere. In the first 15-20 s after switching on, a
game may wait a few seconds ("Preparing memory") until all of the RAM is
available.

Saves and save states go to `saves/<system>/` (PlayStation:
`saves/psx/memcards/` and `saves/psx/states/`), screenshots to
`screenshots/`. RetroArch writes in-game saves every 30 s when they change.
RetroArch's settings live in `system/retroarch/retroarch.cfg` (changes made in
its menu are saved there; it is checked before every game and replaced with
X7 Game's defaults if it is missing or damaged, so deleting it gets the
defaults back). If a game doesn't start, the game list shows the error and
`system/logs/last-game.log` holds the emulator's output. The game list also
warns when X7DATA is read-only or almost full, because saves would fail.

## Updating

From X7 Game 0.3 on, updates don't need a PC flashing tool:

1. Download `x7game-r36sx-<version>.x7update` from the
   [releases](../../releases).
2. Copy it into the **X7DATA** drive (or `X7DATA/update/`).
3. Put the card back and switch the console on. It checks the file, installs
   it (a few seconds, shown on the screen), renames it to
   `.x7update.installed` and restarts straight into the new version. Any
   other waiting `.x7update` files are renamed to `.x7update.skipped`, so an
   older one can't be installed over the new system later (rename one back
   to install it). A file with the version that is already running is only
   renamed, not installed again.

Your files (X7DATA) and settings (`x7game/x7game.cfg`) are not touched. The
update is checked against its checksums before anything is written, and it
waits for a charger if the battery is low (below about 25 %,
`battery_update_level` in `x7game.cfg`). A file for another console or card
layout is renamed to `.x7update.rejected`; `x7game/logs/update.log` says why.

How it works: the card has two system slots (A and B). An update writes the
new system into the slot that is not running and reads it back; only then
it switches the kernel files on X7GAME to the kernel for that slot. If the
power fails while the slot is written, the old system is untouched and the
update simply runs again at the next start.

**Going back:** the previous kernel files are kept in `x7game/previous/`
and the previous system stays in the other slot until the next update.
Over the USB shell type `x7-update --rollback` then `reboot`, or on a PC copy
the files from `x7game/previous/` into `cubegm/`.

Over the USB shell: `x7-update --status` (running slot and versions),
`x7-update --check FILE`, `x7-update FILE` (install, then `reboot`; until
that reboot a second install or a rollback is refused).

From 0.2 or older, flash the 0.3 image once (X7DATA is kept): the system
slots came with 0.3.

## USB serial shell

Connect the console's **OTG** USB-C port to a PC. Windows 10/11 shows a new
**USB Serial Device (COMx)** in Device Manager > Ports (no driver needed;
note the number, it can change between X7 Game versions). In PuTTY:

1. On the **Session** page (the top of the tree on the left) set
   **Connection type: Serial**, **Serial line: COMx** (the number from
   Device Manager) and **Speed: 115200** (any speed works). The Connection >
   Serial page alone is not enough: with "SSH" still selected on the Session
   page and no host name, Open does nothing.
2. Optional: Connection > Serial > Flow control: None.
3. Click **Open**, then **press Enter**: you get a root shell
   (`x7game:~#`).

Only one program can have the COM port open at a time.

If it doesn't work, switch the console off with POWER and look at
`x7game/logs/last-session.log` on the card (its "USB serial shell" section).

```
x7-status                    the hardware state
x7-console                   the hardware state, then every hardware event, live
x7-launch fceumm FILE        start a game (emulator name from systems.txt;
                             refused while another game runs)
x7-soundtest                 test tones (speaker or headphones)
x7-datarepair                check and repair X7DATA
x7-update --status           running system slot and versions
poweroff                     switch the console off
```

## Known limits

- **Emulation is new:** RetroArch, the cores and PCSX4All have not been
  through much testing on the console yet.
- **TF2:** the second card slot can't be used. The SoC has one SD
  controller, the stock system never saw a second card, and it is not a USB
  card reader ([TreeFrogUI's investigation](https://github.com/tzubertowski/TreeFrogUI/blob/main/docs/dev/sd2-investigation.md)).
  X7 Game uses TF1 only.
- **Headphone detection polarity** is not confirmed. If plugging and
  unplugging are reported the wrong way round, set
  `headphone_plugged_level=1` in `x7game/x7game.cfg`.
- **Battery** readings come from the SoC's ADC on the console's own scale
  (about 128 = empty, 175 = full), not calibrated in volts. The percentage
  is a straight line between those points.
- **Refresh rate:** the panel runs at the timing the bootloader programs (the
  stock firmware's mode); X7 Game does not change it yet.
- **Protected V2.7 consoles** need the bootloader's ChaCha20 key to wrap the
  kernel. It is not in this repository. With a dump of a V2.7 console's NOR
  bootloader, the key can be given to the build as the `X7_V27_KEY` secret.
- Only the lower 128 MiB of RAM are usable (the upper half mirrors it).

## Reporting problems

Open an [issue](../../issues) with a photo of the screen and, if the console
got that far, `x7game/logs/boot.log` from the card.

## Building

The GitHub workflow (`.github/workflows/build.yml`) builds the image on every
pushed `v*` tag and publishes it as a release; it can also be started by hand
(Actions > Build X7 Game > Run workflow). Locally, on Linux or WSL:

```
sudo apt install build-essential bc bison flex cpio rsync unzip file wget python3 git libssl-dev
scripts/build.sh [OUTPUT_DIR]   # images in output/images/
```

The first build takes about an hour (it builds the toolchain). On WSL, clone
X7 Game into the Linux home directory (not `/mnt/c`: the kernel has file
names that differ only in case) and build with a `PATH` without the Windows
entries (Buildroot refuses spaces in `PATH`). `X7_VERSION` and `X7_COMMIT`
may only contain `A-Z a-z 0-9 . _ -`. A release can only be published from
the commit its version tag points at: for a new build, use a new version.

| Path | What |
|---|---|
| `br2-external/` | the Buildroot external tree (`BR2_EXTERNAL`) |
| `br2-external/configs/x7game_r36sx_defconfig` | the Buildroot configuration |
| `br2-external/board/r36sx/patches/linux/` | kernel patches: NZEUS Deck's R36S drivers + X7 Game's changes |
| `br2-external/board/r36sx/linux.config`, `linux-x7.fragment` | kernel configuration |
| `br2-external/board/r36sx/x7game-r36sx.dts` | the board description appended to the kernel |
| `br2-external/board/r36sx/mkx7boot.py` | builds the boot files the factory bootloader loads |
| `br2-external/board/r36sx/mkdisk.py`, `mkupdate.py`, `post-image.sh` | build the SD card image and the update file (card layout in `post-image.sh`) |
| `br2-external/board/r36sx/overlay/` | the system's own files (init scripts, USB shell) |
| `br2-external/board/r36sx/stock/` | the console's stock board files (see below) |
| `br2-external/package/x7-hwmon/` | the console's hardware monitor, the virtual gamepad (`x7-padd`), the test game list (`x7-browser`) and `x7-datapart` (data partition table entry and clean-close check) |
| `br2-external/package/retroarch/` | RetroArch: `Makefile.r36sx` (the slim build) and the `x7fb` video driver, as a patch |
| `br2-external/package/libretro-*/` | the libretro cores |
| `br2-external/package/libudev-zero/` | libudev without a udev daemon (RetroArch finds the gamepad with it) |
| `br2-external/package/pcsx4all/` | PCSX4All, the PlayStation emulator, with the X7 Game port (screen, buttons, sound; no SDL), as patches |
| `br2-external/board/r36sx/overlay/usr/share/x7game/` | `systems.txt` (system folders and their emulators), RetroArch's defaults (`retroarch.cfg`, `retroarch-fixed.cfg`) |
| `docs/HARDWARE.md` | what is known about the hardware and where it comes from |
| `docs/BENCHMARKS.md` | measured graphics performance: screen fill, software 3D, sprites |

## Credits and licences

X7 Game is free software under the **GNU General Public License v3.0 or
later** ([LICENSE](LICENSE)). The kernel patches and the board description
are under **GPL-2.0**, like the Linux kernel. X7 Game builds directly on:

- **[NZEUS Deck](https://github.com/nzeuslab/nzeus-deck)** by NZEUS LAB
  (Naser Ashknani), GPL-3.0-or-later; its Linux kernel code is GPL-2.0. X7
  Game takes from it the R36S kernel drivers (framebuffer, sound, battery,
  charger and power button, AVP memory release, USB, AVP mailbox), the CPU
  timer and clock patches, the kernel configuration, the board description,
  the boot container and entry shim, the AVP stand-in, the V2.7 boot-file
  wrapper, the power-on picture format and the USB serial shell (gadget
  descriptor and shell launcher), plus the hardware findings behind all of
  them.
- **[linux-hichip](https://github.com/SiarheiVolkau/linux-hichip)** by
  Siarhei Volkau, GPL-2.0: the HiChip HC16xx Linux kernel (branch
  `hc16xx-7.2`, commit `da5f1a22`). Builds download it from X7 Game's
  [fork](https://github.com/MarsInsanity/linux-hichip), where that commit is
  tagged `x7game-base-da5f1a22`.
- **[Buildroot](https://buildroot.org/)**, GPL-2.0-or-later: the build
  system. Every package keeps its own licence (BusyBox GPL-2.0, glibc
  LGPL-2.1, alsa-lib LGPL-2.1, alsa-utils GPL-2.0, ...); a build writes them
  all to `output/legal-info` with `make legal-info`.

Emulation:

- **[RetroArch](https://github.com/libretro/RetroArch)** 1.22.2 by the
  libretro team, GPL-3.0-or-later: the frontend for the libretro cores. X7
  Game builds it with its own `Makefile.r36sx` and adds a framebuffer video
  driver, `x7fb` (`br2-external/package/retroarch/`).
- **[libudev-zero](https://github.com/illiliti/libudev-zero)** by illiliti,
  ISC: libudev without a udev daemon, for RetroArch's input drivers.
- The libretro cores, each under its own licence. Several allow only
  non-commercial use (marked *n-c*); X7 Game is free and never sold, and
  anyone selling a product based on it must leave those cores out.

  | Core | Upstream | Licence |
  |---|---|---|
  | FCEUmm | [libretro/libretro-fceumm](https://github.com/libretro/libretro-fceumm) | GPL-2.0-or-later |
  | Snes9x 2005 | [libretro/snes9x2005](https://github.com/libretro/snes9x2005) | Snes9x licence (*n-c*) |
  | Gambatte | [libretro/gambatte-libretro](https://github.com/libretro/gambatte-libretro) | GPL-2.0 |
  | gpSP | [libretro/gpsp](https://github.com/libretro/gpsp) | GPL-2.0-or-later |
  | PicoDrive | [libretro/picodrive](https://github.com/libretro/picodrive) | PicoDrive licence (*n-c*); its SH2 code MAME licence (*n-c*); libchdr BSD-3-Clause; emu2413 MIT; zlib Zlib; Tremor BSD-3-Clause; dr_libs Unlicense or MIT-0; LZMA SDK public domain; zstd BSD-3-Clause or GPL-2.0 |
  | Beetle PCE Fast, Beetle WonderSwan (Mednafen) | [libretro/beetle-pce-fast-libretro](https://github.com/libretro/beetle-pce-fast-libretro), [libretro/beetle-wswan-libretro](https://github.com/libretro/beetle-wswan-libretro) | GPL-2.0-or-later |
  | RACE | [libretro/RACE](https://github.com/libretro/RACE) | GPL-2.0-or-later |
  | Stella 2014 | [libretro/stella2014-libretro](https://github.com/libretro/stella2014-libretro) | GPL-2.0 |
  | ProSystem | [libretro/prosystem-libretro](https://github.com/libretro/prosystem-libretro) | GPL-2.0-or-later; bupboop Zlib |
  | Handy | [libretro/libretro-handy](https://github.com/libretro/libretro-handy) | zlib licence (Blip_Buffer LGPL-2.1-or-later) |
  | FB Alpha 2012 CPS-1, CPS-2, Neo Geo | [libretro/fbalpha2012_cps1](https://github.com/libretro/fbalpha2012_cps1), [_cps2](https://github.com/libretro/fbalpha2012_cps2), [_neogeo](https://github.com/libretro/fbalpha2012_neogeo) | FB Alpha licence (*n-c*), MAME licence (*n-c*); zlib and minizip Zlib; Neo Geo also LZMA SDK public domain, un7z BSD-3-Clause |

- **[PCSX4All](https://github.com/gameblabla/pcsx4all_rs97_rg350)**,
  gameblabla's RG350 fork (from PCSX / PCSX-df / PCSX-R, with work by
  Franxis & Chui, Unai, Ulrich Hecht, notaz (PCSX ReARMed), Dmitry Smagin,
  senquack and gameblabla), GPL-2.0-or-later, its MIPS dynarec MIT, minizip
  Zlib: the PlayStation emulator. X7 Game adds its own port for the console
  (`br2-external/package/pcsx4all/`).
- **[libchdr](https://github.com/rtissera/libchdr)** by Romain Tisserand,
  BSD-3-Clause: CHD disc images for PCSX4All.

Hardware research used (no code copied):

- **[TreeFrogUI](https://github.com/tzubertowski/TreeFrogUI)** (frontend
  CC BY-NC-SA 4.0, other parts under their own licences): the R36SX card
  format, the second-SD-slot investigation, battery/charger ADC values, the
  OTG controller, and which libretro cores and build switches suit this
  CPU.
- **[LilSmokeOS](https://github.com/josepilas/LilSmokeOS)** (MPL-2.0): stock
  board-file analysis and evidence that stock cards may carry a second
  partition.
- **[ShallotsOS](https://github.com/MarsInsanity/ShallotsOS)** (CC BY-NC-SA
  4.0): the idea and PC-side workflow of the USB serial shell (configfs ACM
  gadget, PuTTY on Windows' built-in driver).

**Stock board files:** `br2-external/board/r36sx/stock/` holds the console
manufacturer's own board description files (`Bubbles.scr`, `dtb.bin`) from
the stock V2.6 and V2.7 firmware, unmodified. The factory bootloader reads
them at power-on (they set up the screen), so the card image must contain
them. They remain the manufacturer's.

# X7 Game

A small, fast Linux for the **R36SX / R36S V2.6 / R36S V2.7** handhelds, the
R36S look-alikes built on the **HiChip E3100** (MIPS 74Kc, one core, 256 MB
RAM). X7 Game replaces the locked-down stock "hOS" (Linux 4.4) with a modern
**Linux 7.2** kernel and a **Buildroot** system, started straight from the SD
card. The console's flash chip is never touched: put the stock card back and
the console is exactly as it was.

This is the base OS: no frontend yet, just a console on the screen that shows
what the hardware is doing and ends with **"Welcome to X7 Game!"**. A
retro-gaming frontend comes next.

> **Status: first builds, not yet tested on hardware.** Everything below is
> built on code that NZEUS Deck runs on real consoles, but X7 Game's own
> image has not been booted yet. Please report what you see (see
> [Reporting problems](#reporting-problems)).

## What it does

| | |
|---|---|
| Boot | Linux 7.2 + BusyBox from the SD card (TF1), read-only squashfs root, no initramfs. Target: under 10 s to the console |
| Image | one `.img` of 73 MiB (FAT32 boot partition + root file system) |
| Console | the boot log, the hardware state, **"Welcome to X7 Game!"**, then a line for every hardware event |
| Buttons | D-pad, A, B, X, Y, L1, L2, R1, R2, SELECT, START, FN, VOL+, VOL-, POWER, each press and release is printed. The analog sticks are wired to the D-pad and face buttons |
| Display | 640x480, 32-bit colour (16.7 million colours) framebuffer console; the panel timing is the one the bootloader sets up. `x7-colortest` shows colour ramps |
| Sound | ALSA sound card (speaker and headphone jack). `x7-soundtest` plays test tones |
| Headphones | automatic switching: headphones in = speaker off, headphones out = speaker on, printed on every change |
| DC port | charger plugged / unplugged printed; battery % printed whenever it goes up or down |
| OTG port | connected / disconnected printed; a **root shell over USB serial** (PuTTY) |
| Power | POWER pressed = clean power-off; at power-on the console switches straight off again if the battery is at or below the cutoff and no charger is plugged in |
| TF2 | inserted / removed and card size printed **when the kernel sees the card** (see [Known limits](#known-limits)) |

## Supported consoles

| Console | Image |
|---|---|
| R36SX / R36S running the **V2.6 firmware** (unencrypted boot files), including V2.7 hardware running it | `x7game-r36sx-<version>.img` |
| **"Bootloader protected" V2.7** consoles | `x7game-r36sx-v27protected-<version>.img`, only built when the V2.7 boot key is available (see [Known limits](#known-limits)) |

## Install

1. Download `x7game-r36sx-<version>.img.zip` (or `.img.xz`) from the
   [releases](../../releases) and unzip it.
2. Write the `.img` to a microSD card (any size) with
   [balenaEtcher](https://etcher.balena.io/) or [Rufus](https://rufus.ie/).
   This erases the card, so don't use your stock card. Keep the stock card as
   your way back.
3. Put the card in the **TF1** slot and switch the console on.

The card then shows up on a PC as a small drive called **X7GAME**:
`x7game/x7game.cfg` holds the settings (battery cutoffs, headphone polarity,
start volume) and `x7game/logs/boot.log` the log of the last start.

## USB serial shell

Connect the console's **OTG** USB-C port to a PC. Windows 10/11 shows a new
**USB Serial Device (COMx)** in Device Manager > Ports (no driver needed). In
PuTTY choose connection type **Serial**, that COM port, any speed; under
Connection > Serial set **Flow control: None**; click Open, then **press
Enter**: you get a root shell. Only one program can have the COM port open
at a time.

If it doesn't work, switch the console off with POWER and look at
`x7game/logs/last-session.log` on the card (its "USB serial shell" section).

```
x7-status                    the hardware state
tail -f /run/x7-events.log   the console's event lines, live
x7-soundtest                 test tones (speaker or headphones)
x7-colortest                 colour ramps on the screen
x7-tf2-probe                 read-only helper to find TF2's wiring
poweroff                     switch the console off
```

## Known limits

- **Not yet tested on hardware.** In particular the V2.6 bootloader starting
  this kernel, and the screen take-over, are still to be confirmed.
- **TF2:** no one has found the second card slot in software yet. The SoC has
  one SD controller, the stock system never saw a second card, and it is not
  a USB card reader ([TreeFrogUI's investigation](https://github.com/tzubertowski/TreeFrogUI/blob/main/docs/dev/sd2-investigation.md)).
  X7 Game reports any second card the kernel sees, and `x7-tf2-probe` watches
  every GPIO pin and the SD controller's card-detect lines while you insert
  and remove a card, to find the slot's wiring.
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
scripts/build.sh            # images in output/images/
```

The first build takes about an hour (it builds the toolchain).

| Path | What |
|---|---|
| `br2-external/` | the Buildroot external tree (`BR2_EXTERNAL`) |
| `br2-external/configs/x7game_r36sx_defconfig` | the Buildroot configuration |
| `br2-external/board/r36sx/patches/linux/` | kernel patches: NZEUS Deck's R36S drivers + X7 Game's changes |
| `br2-external/board/r36sx/linux.config`, `linux-x7.fragment` | kernel configuration |
| `br2-external/board/r36sx/x7game-r36sx.dts` | the board description appended to the kernel |
| `br2-external/board/r36sx/mkx7boot.py` | builds the boot files the factory bootloader loads |
| `br2-external/board/r36sx/mkdisk.py`, `post-image.sh` | build the SD card image |
| `br2-external/board/r36sx/overlay/` | the system's own files (init scripts, USB shell) |
| `br2-external/board/r36sx/stock/` | the console's stock board files (see below) |
| `br2-external/package/x7-hwmon/` | the console's hardware monitor and the TF2 probe |
| `docs/HARDWARE.md` | what is known about the hardware and where it comes from |

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
  `hc16xx-7.2`, commit `da5f1a22`).
- **[Buildroot](https://buildroot.org/)**, GPL-2.0-or-later: the build
  system. Every package keeps its own licence (BusyBox GPL-2.0, glibc
  LGPL-2.1, alsa-lib LGPL-2.1, alsa-utils GPL-2.0, ...); a build writes them
  all to `output/legal-info` with `make legal-info`.

Hardware research used (no code copied):

- **[TreeFrogUI](https://github.com/tzubertowski/TreeFrogUI)** (frontend
  CC BY-NC-SA 4.0, other parts under their own licences): the R36SX card
  format, the second-SD-slot investigation, battery/charger ADC values, the
  OTG controller.
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

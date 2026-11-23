# R36SX / R36S V2.6 / V2.7 hardware notes

What X7 Game relies on, and where each fact comes from. "NZEUS" = NZEUS Deck
(`linux-port/`), measured on real consoles; "TreeFrogUI", "ShallotsOS" and
"LilSmokeOS" = those projects' docs; "stock DT" = the stock `Bubbles.scr`.

## SoC and memory

- HiChip E3100 (HC16xx family), board HC16E3100V20: MIPS 74Kc, little-endian,
  MIPS32r2 with FPU, one core. The FPU corrupts stores at the factory
  1188 MHz, so the kernel runs at 900 MHz (`nzclk=900`, NZEUS).
- 256 MB DDR3, but the upper 128 MiB mirror the lower half (NZEUS). Linux
  uses 0-0x02f91e50 plus, once the AVP is proven off, 0x030bf000-0x08000000
  (about 117 MiB total). 0x02f92000-0x030bf000 is the bootloader's boot
  framebuffer and logo.
- A second CPU, the "AVP", runs HiChip's RTOS on the stock system (display,
  sound, backlight). X7 Game replaces its firmware with a 5-instruction
  stand-in (NZEUS) and drives the hardware from Linux.

## Boot

- The factory bootloader (512 KB NOR flash) reads the first FAT32 partition
  of the card in TF1 and loads `cubegm/`: kernel (`advapi32.dll` /
  `vmlinux.uImage`), AVP firmware (`ApplicationFrame.dll` / `avp.uImage`),
  board file (`Bubbles.scr` / `dtb.bin`) and power-on picture
  (`xgame-logo.bmp`, 640x480 32-bit BMP). Stock V2.6 cards have both name
  sets (stock DT `external_files`; LilSmokeOS); `Bubbles.scr` is the one
  stock Linux used (TreeFrogUI).
- V2.6 firmware: plain legacy uImages (the stock V2.6 card's kernel and AVP
  files are unencrypted). V2.7 "protected": each file is
  `nonce(12) | length(4, LE) | ChaCha20(uImage)`, key derived from the
  bootloader (NZEUS `boot-analysis/image_codec.py`).
- Plain-MBR FAT32 cards boot (TreeFrogUI's install guide formats them on a
  PC); NZEUS's console card had sector 0 XOR-scrambled with `DEADBEEF`.
  A second partition is tolerated (LilSmokeOS).
- Our kernel: gzip uImage, load 0x80100000, entry 0x81000000 (shim that
  jumps to `kernel_entry`), DTB appended (`CONFIG_MIPS_RAW_APPENDED_DTB`),
  below the bootloader heap at 0x01da0000 (NZEUS).

## Buttons (NZEUS `input/README.md`)

- 12-bit shift register, clock L08, data L09: bit 0 L1, 1 X, 2 Y, 3 R1, 4 B,
  5 A, 6 SELECT, 7 START, 8 UP, 9 DOWN, 10 LEFT, 11 RIGHT. The left stick is
  wired to the D-pad, the right stick to X/A/B/Y (no analog input).
- Direct pins, active low: L2 = L07, R2 = L11, VOL+ = L13, VOL- = L12 (also
  UART0 TX: X7 Game keeps the UART off), FN = L02, POWER = L14.

## Power

- Battery and charger: SAR ADC left running by the bootloader, sample bytes
  at 0x188184d0; level = 241 * raw[ch] / raw[ch0]; ch1 battery (about
  128 empty .. 175 full; the bootloader treats <= 127 as low), ch5 charger
  (0 unplugged, about 138 plugged; threshold 64) (NZEUS; TreeFrogUI reads the
  same through `/dev/check_adc1`/`5`).
- POWER button L14 only senses the button; the power-off line is L01 (drive
  low = off) (NZEUS). Holding POWER about 7 s cuts power in hardware.
- Restart: watchdog at 0x18818500 (NZEUS).

## Display

- 640x480 MIPI-DSI panel, set up by the bootloader from the board file's
  `panel-init-sequence` (V2.6 and V2.7 differ). The kernel framebuffer points
  the GMA0 layer at its own ARGB8888 or RGB565 buffer (NZEUS
  `display/hc16xx-gma-fb.c`).

## Sound

- I2S block SND0 (0x1880a000) -> TM8211 DAC -> 8002D speaker amp; amp
  enable L19 (low = on); headphone detect L15 (polarity unconfirmed)
  (NZEUS `audio/`, stock DT `panel` node).

## USB

- OTG USB-C port = MUSB controller at 0x18844000 (TreeFrogUI, ShallotsOS).
  The second MUSB (0x18850000) is unused. The DC USB-C port only charges.

## TF2

- Not found in software: one DesignWare SD controller (0x1884c000, pins
  T00-T05), no second controller, no USB card reader; `num-slots = <2>` in
  the stock DT stopped the stock kernel booting (TreeFrogUI
  `docs/dev/sd2-investigation.md`, ShallotsOS). X7 Game has given up on
  TF2 and uses TF1 only.

## No RTC

- The console has no real-time clock (TreeFrogUI).

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
- How X7 Game reads them: the shift register is sampled every 16 ms (8 ms
  while a game started from the game list runs; it can't raise interrupts).
  The direct pins and the headphone detect pin L15 use the GPIO controller's
  edge interrupts (gpio-hc16xx; the SF3000 device tree does the same for
  L07/L11/L13): gpio-keys for L2/R2/VOL+/VOL-/FN, and an interrupt that
  starts the power button and headphone checks (patch 0017), so an idle
  console no longer samples them on a timer. Interrupts on L02, L12, L14 and
  L15 were first used by X7 Game (to be confirmed on hardware).

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
- The layer is described by a 640-byte descriptor in memory (GMA_DMBA
  0x1883a304 points at it); layout from HiChip's hcRTOS SDK (`hcfb.h`,
  `gma_header_t`, public copy in github.com/bnister/sf2000_hcrtos):
  dword0 flags (bit 2 scale on, bit 3 edge preserve, bits 7:4 format),
  dword2/3 the window on the screen (start | inclusive end << 16), dword4 the
  source size, dword5 alpha and pitch (bits 29:16), dword7 the pixel
  address, dword8 bit 0 scale mode (0 filter, 1 duplicate), dword9 the scale
  steps (4.12 fixed point, 4096 x source / output, horizontal low half),
  dwords 16-143 the polyphase filter table (4/3 taps, 16 phases).
  Registers: 0x300 control, 0x304 descriptor address, 0x308 alpha, 0x350 bit 0
  holds updates until released (they take effect at the next frame).
- Hardware upscaling of that layer (kernel patch 0019,
  `/sys/bus/platform/devices/1883a000.framebuffer/scale`) uses HiChip's
  upscale filter table, the one the sf3k-hacking project ran on an SF3000
  (github.com/SiarheiVolkau/sf3k-hacking). Confirmed on the R36SX (X7 Game
  dev-46883ac): by hand and with RetroArch.
- The CPU writes the buffer uncached; the 74K's "uncached accelerated"
  attribute (write gathering) can be switched on for programs' mappings
  (patch 0018). Measured on the R36SX with x7-fbspeed: a full 640x480 16-bit
  frame takes 4.19 ms uncached, 0.89 ms write-combined, all pixels correct.
- Page flipping (kernel patch 0020): in RGB565 the buffer holds two
  640x480 pages; a flip builds the new page's descriptor in a second block
  and points GMA_DMBA at it under the hold bit, so it takes effect between
  two frames (HiChip's driver flips the same way). 0x1883ab04 is taken to
  show the latched descriptor address (to be confirmed: if it never matches,
  the driver stops waiting for flips and logs it).

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

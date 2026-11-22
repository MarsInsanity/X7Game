# Stock board files

The console manufacturer's own board description files (flattened device
trees), unmodified, from the stock firmware:

| Folder | Firmware | Source |
|---|---|---|
| `v2.6/` | R36SX V2.6 (0712), unencrypted boot files | "R36SX V2.6 (0712) Minimal Backup", `cubegm/` |
| `v2.7/` | R36SX V2.7, "bootloader protected" | "R36SX V2.7 Minimal Backup", `cubegm/` (same hashes NZEUS Deck documents for its console) |

The factory bootloader reads them at power-on (they set up the LCD panel,
whose init sequence differs between V2.6 and V2.7, and the memory map) and
the stock Linux used `Bubbles.scr` as its device tree. `dtb.bin` is the same
tree with seven memory addresses moved up by 128 MiB. X7 Game's own kernel
does NOT use them: it carries its own board description
(`../x7game-r36sx.dts`). They remain the manufacturer's; `SHA256SUMS` lists
their hashes.

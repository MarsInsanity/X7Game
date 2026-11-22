X7 Game - a small Linux for the R36SX / R36S V2.6 / R36S V2.7 (HiChip E3100)
=============================================================================

This drive (X7GAME) is the console's boot partition:

  cubegm\      the files the console's bootloader loads at power-on:
               the X7 Game kernel (advapi32.dll, vmlinux.uImage), a stand-in
               for the AVP co-processor firmware (ApplicationFrame.dll,
               avp.uImage), the console's own board files (Bubbles.scr,
               dtb.bin) and the power-on picture (xgame-logo.bmp).
               Don't rename or delete them.
  x7game\      x7game.cfg  your settings (open it with Notepad)
               logs\       boot.log of the last start, for bug reports

The X7 Game system itself sits on the card after this partition (Windows
doesn't show it). Don't format, shrink or move this partition.

USB shell: connect the console's OTG port to a PC. Windows 10/11 shows a new
"USB Serial Device (COMx)". In PuTTY choose Connection type "Serial", that
COM port, any speed, then press Enter.

Source code, licences and bug reports: https://github.com/MarsInsanity/X7Game

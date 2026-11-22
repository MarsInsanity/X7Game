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

Your files go on the second drive, X7DATA (made at the first start): roms\,
bios\, saves\, music\, videos\, photos\ ... - see README.txt there.

Updates: copy an x7game-...x7update file into X7DATA and switch the console
on. It installs itself and restarts; your files and settings stay.
previous\ holds the kernel files of the system that ran before the last
update (to go back: copy them into cubegm\, or x7-update --rollback).

USB shell: connect the console's OTG port to a PC. Windows 10/11 shows a new
"USB Serial Device (COMx)" in Device Manager. In PuTTY, on the Session page
(top of the tree) choose Connection type "Serial", Serial line COMx, Speed
115200, click Open, then press Enter. (Setting only the Connection > Serial
page is not enough: with "SSH" still selected, Open does nothing.)

logs\last-session.log is written when you switch the console off with the
POWER button: what happened in that session (events, USB shell, logs).

Source code, licences and bug reports: https://github.com/MarsInsanity/X7Game

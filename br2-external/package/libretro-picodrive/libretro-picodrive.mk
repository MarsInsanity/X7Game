################################################################################
#
# libretro-picodrive
#
################################################################################

LIBRETRO_PICODRIVE_VERSION = 1890c2932234c9d30f4cd3851d02228baae8f09e
# git, not the GitHub tarball: the build needs the submodules (libchdr for
# CD images, emu2413 for the SMS FM sound, dr_libs for MP3 CD audio)
LIBRETRO_PICODRIVE_SITE = https://github.com/libretro/picodrive.git
LIBRETRO_PICODRIVE_SITE_METHOD = git
LIBRETRO_PICODRIVE_GIT_SUBMODULES = YES
LIBRETRO_PICODRIVE_LICENSE = PicoDrive non-commercial, MAME non-commercial (SH2 core), BSD-3-Clause (libchdr), MIT (emu2413), Zlib (zlib)
LIBRETRO_PICODRIVE_LICENSE_FILES = COPYING pico/cd/libchdr/LICENSE.txt pico/sound/emu2413/LICENSE

# ARCH=mipsel (upstream would ask "$(CC) -dumpmachine", same answer, but
# be explicit): the C 68000 (FAME) and Z80 (CZ80) cores and the SH2
# recompiler, which includes cpu/drc/emit_mips.c for __mips__. The ARM asm
# parts and Cyclone/DrZ80 are only used for ARCH=arm.
# PLATFORM_TREMOR=1: the bundled Vorbis decoder, instead of linking
# libvorbis whenever its headers happen to be in staging.
# GIT_REVISION: git would report the X7 Game checkout around output/.
LIBRETRO_PICODRIVE_MAKE_OPTS = \
	ARCH=mipsel \
	use_fame=1 \
	use_cz80=1 \
	use_sh2drc=1 \
	PLATFORM_TREMOR=1 \
	GIT_REVISION=-$(shell echo $(LIBRETRO_PICODRIVE_VERSION) | cut -c1-7)

define LIBRETRO_PICODRIVE_BUILD_CMDS
	$(call X7_LIBRETRO_MAKE,$(@D),Makefile.libretro,$(LIBRETRO_PICODRIVE_MAKE_OPTS))
endef

define LIBRETRO_PICODRIVE_INSTALL_TARGET_CMDS
	$(call X7_LIBRETRO_INSTALL,$(@D)/picodrive_libretro.so,picodrive)
endef

$(eval $(generic-package))

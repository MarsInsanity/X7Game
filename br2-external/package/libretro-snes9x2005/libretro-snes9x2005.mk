################################################################################
#
# libretro-snes9x2005
#
################################################################################

LIBRETRO_SNES9X2005_VERSION = a79dfe9047e7fec58808aefe48ad2bf499c7af11
LIBRETRO_SNES9X2005_SITE = $(call github,libretro,snes9x2005,$(LIBRETRO_SNES9X2005_VERSION))
LIBRETRO_SNES9X2005_LICENSE = Snes9x non-commercial
LIBRETRO_SNES9X2005_LICENSE_FILES = copyright

# Plain C, no arch detection (source/tile.c turns on its own MIPS
# little-endian asm from __MIPSEL). USE_BLARGG_APU stays 0: the faster
# core, built as snes9x2005_libretro.so (1 would make the "_plus" one).
# GIT_VERSION: git would report the X7 Game checkout around output/.
LIBRETRO_SNES9X2005_MAKE_OPTS = \
	USE_BLARGG_APU=0 \
	GIT_VERSION='" $(shell echo $(LIBRETRO_SNES9X2005_VERSION) | cut -c1-7)"'

define LIBRETRO_SNES9X2005_BUILD_CMDS
	$(call X7_LIBRETRO_MAKE,$(@D),Makefile,$(LIBRETRO_SNES9X2005_MAKE_OPTS))
endef

define LIBRETRO_SNES9X2005_INSTALL_TARGET_CMDS
	$(call X7_LIBRETRO_INSTALL,$(@D)/snes9x2005_libretro.so,snes9x2005)
endef

$(eval $(generic-package))

################################################################################
#
# libretro-beetle-pce-fast
#
################################################################################

LIBRETRO_BEETLE_PCE_FAST_VERSION = 4cf066e22533186d0cfad85a0fec2aced93e4e29
LIBRETRO_BEETLE_PCE_FAST_SITE = $(call github,libretro,beetle-pce-fast-libretro,$(LIBRETRO_BEETLE_PCE_FAST_VERSION))
LIBRETRO_BEETLE_PCE_FAST_LICENSE = GPL-2.0-or-later
LIBRETRO_BEETLE_PCE_FAST_LICENSE_FILES = COPYING

# HAVE_CDROM=0: the makefile turns on physical CD-ROM drive access when the
# build host runs Linux; the console has no drive (CD images still work).
# CHD support uses the bundled libchdr/zlib/zstd/lzma (no system libs).
# Linked with g++. GIT_VERSION: git would report the X7 Game checkout.
LIBRETRO_BEETLE_PCE_FAST_MAKE_OPTS = \
	HAVE_CDROM=0 \
	GIT_VERSION='" $(shell echo $(LIBRETRO_BEETLE_PCE_FAST_VERSION) | cut -c1-7)"'

define LIBRETRO_BEETLE_PCE_FAST_BUILD_CMDS
	$(call X7_LIBRETRO_MAKE,$(@D),Makefile,$(LIBRETRO_BEETLE_PCE_FAST_MAKE_OPTS))
endef

define LIBRETRO_BEETLE_PCE_FAST_INSTALL_TARGET_CMDS
	$(call X7_LIBRETRO_INSTALL,$(@D)/mednafen_pce_fast_libretro.so,mednafen_pce_fast)
endef

$(eval $(generic-package))

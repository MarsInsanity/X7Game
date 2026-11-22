################################################################################
#
# libretro-handy
#
################################################################################

LIBRETRO_HANDY_VERSION = bc55d462f0b2d6b073ea93dc552ebd73cec60fd1
LIBRETRO_HANDY_SITE = $(call github,libretro,libretro-handy,$(LIBRETRO_HANDY_VERSION))
LIBRETRO_HANDY_LICENSE = Zlib, LGPL-2.1-or-later (Blip_Buffer)
LIBRETRO_HANDY_LICENSE_FILES = lynx/license.txt

# C++, no arch detection. GIT_VERSION: git would report the X7 Game
# checkout around output/. FRONTEND_SUPPORTS_XRGB8888=0: 16-bit (RGB565)
# frames, what the x7fb video driver shows without converting.
LIBRETRO_HANDY_MAKE_OPTS = \
	FRONTEND_SUPPORTS_XRGB8888=0 \
	GIT_VERSION='" $(shell echo $(LIBRETRO_HANDY_VERSION) | cut -c1-7)"'

define LIBRETRO_HANDY_BUILD_CMDS
	$(call X7_LIBRETRO_MAKE,$(@D),Makefile,$(LIBRETRO_HANDY_MAKE_OPTS))
endef

define LIBRETRO_HANDY_INSTALL_TARGET_CMDS
	$(call X7_LIBRETRO_INSTALL,$(@D)/handy_libretro.so,handy)
endef

$(eval $(generic-package))

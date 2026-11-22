################################################################################
#
# libretro-beetle-wswan
#
################################################################################

LIBRETRO_BEETLE_WSWAN_VERSION = 4b01295838ea89e3f1355bbe4cb5cf98aa6108cd
LIBRETRO_BEETLE_WSWAN_SITE = $(call github,libretro,beetle-wswan-libretro,$(LIBRETRO_BEETLE_WSWAN_VERSION))
LIBRETRO_BEETLE_WSWAN_LICENSE = GPL-2.0-or-later
LIBRETRO_BEETLE_WSWAN_LICENSE_FILES = COPYING

# Plain C (linked with gcc), no arch detection. GIT_VERSION: git would
# report the X7 Game checkout around output/.
LIBRETRO_BEETLE_WSWAN_MAKE_OPTS = \
	GIT_VERSION='" $(shell echo $(LIBRETRO_BEETLE_WSWAN_VERSION) | cut -c1-7)"'

define LIBRETRO_BEETLE_WSWAN_BUILD_CMDS
	$(call X7_LIBRETRO_MAKE,$(@D),Makefile,$(LIBRETRO_BEETLE_WSWAN_MAKE_OPTS))
endef

define LIBRETRO_BEETLE_WSWAN_INSTALL_TARGET_CMDS
	$(call X7_LIBRETRO_INSTALL,$(@D)/mednafen_wswan_libretro.so,mednafen_wswan)
endef

$(eval $(generic-package))

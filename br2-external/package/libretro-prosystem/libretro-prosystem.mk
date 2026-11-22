################################################################################
#
# libretro-prosystem
#
################################################################################

LIBRETRO_PROSYSTEM_VERSION = 8a88014287c7a01cd568067e5a557d0a2b2a051f
LIBRETRO_PROSYSTEM_SITE = $(call github,libretro,prosystem-libretro,$(LIBRETRO_PROSYSTEM_VERSION))
LIBRETRO_PROSYSTEM_LICENSE = GPL-2.0-or-later, Zlib (bupboop)
LIBRETRO_PROSYSTEM_LICENSE_FILES = License.txt bupboop/License.txt

# Plain C, no arch detection (the unix target already adds -fsigned-char).
# GIT_VERSION: git would report the X7 Game checkout around output/.
LIBRETRO_PROSYSTEM_MAKE_OPTS = \
	GIT_VERSION='" $(shell echo $(LIBRETRO_PROSYSTEM_VERSION) | cut -c1-7)"'

define LIBRETRO_PROSYSTEM_BUILD_CMDS
	$(call X7_LIBRETRO_MAKE,$(@D),Makefile,$(LIBRETRO_PROSYSTEM_MAKE_OPTS))
endef

define LIBRETRO_PROSYSTEM_INSTALL_TARGET_CMDS
	$(call X7_LIBRETRO_INSTALL,$(@D)/prosystem_libretro.so,prosystem)
endef

$(eval $(generic-package))

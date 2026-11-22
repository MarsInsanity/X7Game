################################################################################
#
# libretro-race
#
################################################################################

LIBRETRO_RACE_VERSION = c660d9ab5aafb47aefff90182ca90d319ad9b077
LIBRETRO_RACE_SITE = $(call github,libretro,RACE,$(LIBRETRO_RACE_VERSION))
LIBRETRO_RACE_LICENSE = GPL-2.0-or-later
LIBRETRO_RACE_LICENSE_FILES = license.txt

# Plain C. The Z80 is the C core CZ80 (the default; DRZ80=1 would pick the
# ARM asm DrZ80). GIT_VERSION: git would report the X7 Game checkout.
LIBRETRO_RACE_MAKE_OPTS = \
	GIT_VERSION='" $(shell echo $(LIBRETRO_RACE_VERSION) | cut -c1-7)"'

define LIBRETRO_RACE_BUILD_CMDS
	$(call X7_LIBRETRO_MAKE,$(@D),Makefile,$(LIBRETRO_RACE_MAKE_OPTS))
endef

define LIBRETRO_RACE_INSTALL_TARGET_CMDS
	$(call X7_LIBRETRO_INSTALL,$(@D)/race_libretro.so,race)
endef

$(eval $(generic-package))

################################################################################
#
# libretro-stella2014
#
################################################################################

LIBRETRO_STELLA2014_VERSION = 7d1361e407e63f29e52892655069e5fb4096e691
LIBRETRO_STELLA2014_SITE = $(call github,libretro,stella2014-libretro,$(LIBRETRO_STELLA2014_VERSION))
LIBRETRO_STELLA2014_LICENSE = GPL-2.0
LIBRETRO_STELLA2014_LICENSE_FILES = stella/license.txt

# C++, no arch detection. GIT_VERSION: git would report the X7 Game
# checkout around output/.
LIBRETRO_STELLA2014_MAKE_OPTS = \
	GIT_VERSION='" $(shell echo $(LIBRETRO_STELLA2014_VERSION) | cut -c1-7)"'

define LIBRETRO_STELLA2014_BUILD_CMDS
	$(call X7_LIBRETRO_MAKE,$(@D),Makefile,$(LIBRETRO_STELLA2014_MAKE_OPTS))
endef

define LIBRETRO_STELLA2014_INSTALL_TARGET_CMDS
	$(call X7_LIBRETRO_INSTALL,$(@D)/stella2014_libretro.so,stella2014)
endef

$(eval $(generic-package))

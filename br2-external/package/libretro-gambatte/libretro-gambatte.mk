################################################################################
#
# libretro-gambatte
#
################################################################################

LIBRETRO_GAMBATTE_VERSION = 138bcbbf311300a271896bf93a76370c72cab339
LIBRETRO_GAMBATTE_SITE = $(call github,libretro,gambatte-libretro,$(LIBRETRO_GAMBATTE_VERSION))
LIBRETRO_GAMBATTE_LICENSE = GPL-2.0
LIBRETRO_GAMBATTE_LICENSE_FILES = COPYING

# C++ (-std=c++98), no arch detection. GIT_VERSION: git would report the
# X7 Game checkout around output/, so pass the core's own hash.
LIBRETRO_GAMBATTE_MAKE_OPTS = \
	GIT_VERSION='" $(shell echo $(LIBRETRO_GAMBATTE_VERSION) | cut -c1-7)"'

define LIBRETRO_GAMBATTE_BUILD_CMDS
	$(call X7_LIBRETRO_MAKE,$(@D),Makefile.libretro,$(LIBRETRO_GAMBATTE_MAKE_OPTS))
endef

define LIBRETRO_GAMBATTE_INSTALL_TARGET_CMDS
	$(call X7_LIBRETRO_INSTALL,$(@D)/gambatte_libretro.so,gambatte)
endef

$(eval $(generic-package))

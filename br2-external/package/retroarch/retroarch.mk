################################################################################
#
# retroarch
#
# Slim build for X7 Game (Makefile.r36sx and the x7fb video driver come from
# 0001-x7fb-video-driver-and-Makefile.r36sx.patch).
#
################################################################################

RETROARCH_VERSION = v1.22.2
RETROARCH_SITE = $(call github,libretro,RetroArch,$(RETROARCH_VERSION))
RETROARCH_LICENSE = GPL-3.0+
RETROARCH_LICENSE_FILES = COPYING
RETROARCH_DEPENDENCIES = alsa-lib libudev-zero

define RETROARCH_BUILD_CMDS
	$(TARGET_MAKE_ENV) $(MAKE) -C $(@D) -f Makefile.r36sx \
		CC="$(TARGET_CC)" CXX="$(TARGET_CXX)" STRIP="$(TARGET_STRIP)"
endef

define RETROARCH_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/retroarch $(TARGET_DIR)/usr/bin/retroarch
endef

$(eval $(generic-package))

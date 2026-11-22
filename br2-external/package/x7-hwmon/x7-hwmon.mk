################################################################################
#
# x7-hwmon
#
################################################################################

X7_HWMON_VERSION = 1.0
X7_HWMON_SITE = $(BR2_EXTERNAL_X7GAME_PATH)/package/x7-hwmon/src
X7_HWMON_SITE_METHOD = local
X7_HWMON_LICENSE = GPL-3.0-or-later

define X7_HWMON_BUILD_CMDS
	$(TARGET_MAKE_ENV) $(MAKE) -C $(@D) CC="$(TARGET_CC)" \
		CFLAGS="$(TARGET_CFLAGS)" LDFLAGS="$(TARGET_LDFLAGS)"
endef

define X7_HWMON_INSTALL_TARGET_CMDS
	$(TARGET_MAKE_ENV) $(MAKE) -C $(@D) DESTDIR="$(TARGET_DIR)" PREFIX=/usr install
endef

$(eval $(generic-package))

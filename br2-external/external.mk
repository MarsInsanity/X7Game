################################################################################
#
# Helpers for the libretro core packages (package/libretro-*)
#
# Cores are built with their own libretro makefile, platform=unix, and the
# Buildroot cross toolchain. CFLAGS are NOT overridden on the make command
# line (that would wipe the core makefile's own -D/-I flags): the toolchain
# already defaults to MIPS32r2 / hard-float FPXX; the extra flags go into CC
# and CXX instead.
#
#   define LIBRETRO_FOO_BUILD_CMDS
#   	$(call X7_LIBRETRO_MAKE,$(@D),Makefile.libretro,ARCH=mips SOME_OPT=1)
#   endef
#   define LIBRETRO_FOO_INSTALL_TARGET_CMDS
#   	$(call X7_LIBRETRO_INSTALL,$(@D)/foo_libretro.so,foo)
#   endef
#
################################################################################

# GCC 14 turned several old-C warnings into errors that older cores trip on
X7_LIBRETRO_CC_FLAGS = -mtune=74kf2_1 -fcommon \
	-Wno-error=implicit-function-declaration -Wno-error=incompatible-pointer-types \
	-Wno-error=int-conversion -Wno-error=implicit-int -Wno-error=return-mismatch
X7_LIBRETRO_CXX_FLAGS = -mtune=74kf2_1

# $(1) = directory to run make in, $(2) = makefile, $(3) = extra make arguments
X7_LIBRETRO_MAKE = $(TARGET_MAKE_ENV) $(MAKE) -C $(1) -f $(2) platform=unix \
	CC="$(TARGET_CC) $(X7_LIBRETRO_CC_FLAGS)" \
	CXX="$(TARGET_CXX) $(X7_LIBRETRO_CXX_FLAGS)" \
	AR="$(TARGET_AR)" STRIP="$(TARGET_STRIP)" $(3)

# $(1) = the built core, $(2) = its name: installed as
# /usr/lib/libretro/$(2)_libretro.so (what the launcher passes to RetroArch)
X7_LIBRETRO_INSTALL = $(INSTALL) -D -m 0755 $(1) $(TARGET_DIR)/usr/lib/libretro/$(2)_libretro.so

include $(sort $(wildcard $(BR2_EXTERNAL_X7GAME_PATH)/package/*/*.mk))

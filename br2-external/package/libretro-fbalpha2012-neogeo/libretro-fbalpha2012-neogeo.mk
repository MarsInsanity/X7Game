################################################################################
#
# libretro-fbalpha2012-neogeo
#
################################################################################

LIBRETRO_FBALPHA2012_NEOGEO_VERSION = e092097037d494c50d17c5144a2758d68538061b
LIBRETRO_FBALPHA2012_NEOGEO_SITE = $(call github,libretro,fbalpha2012_neogeo,$(LIBRETRO_FBALPHA2012_NEOGEO_VERSION))
LIBRETRO_FBALPHA2012_NEOGEO_LICENSE = FB Alpha non-commercial, MAME non-commercial
LIBRETRO_FBALPHA2012_NEOGEO_LICENSE_FILES = src/license.txt

# The old FB Alpha code type-puns heavily: add -fno-strict-aliasing (and
# -fsigned-char, already the MIPS default, to be explicit). The makefile
# has no variable for extra flags in both CFLAGS and CXXFLAGS, so CC/CXX
# are given again with them (the last CC= on the make command line wins).
# Musashi (C) is the 68000 core, zlib and 7z support are bundled, and the
# little-endian default is right. GIT_VERSION: git would report the X7 Game
# checkout around output/.
LIBRETRO_FBALPHA2012_NEOGEO_MAKE_OPTS = \
	CC="$(TARGET_CC) $(X7_LIBRETRO_CC_FLAGS) -fsigned-char -fno-strict-aliasing" \
	CXX="$(TARGET_CXX) $(X7_LIBRETRO_CXX_FLAGS) -fsigned-char -fno-strict-aliasing -Wno-narrowing" \
	GIT_VERSION='" $(shell echo $(LIBRETRO_FBALPHA2012_NEOGEO_VERSION) | cut -c1-7)"'

define LIBRETRO_FBALPHA2012_NEOGEO_BUILD_CMDS
	$(call X7_LIBRETRO_MAKE,$(@D),makefile.libretro,$(LIBRETRO_FBALPHA2012_NEOGEO_MAKE_OPTS))
endef

define LIBRETRO_FBALPHA2012_NEOGEO_INSTALL_TARGET_CMDS
	$(call X7_LIBRETRO_INSTALL,$(@D)/fbalpha2012_neogeo_libretro.so,fbalpha2012_neogeo)
endef

$(eval $(generic-package))

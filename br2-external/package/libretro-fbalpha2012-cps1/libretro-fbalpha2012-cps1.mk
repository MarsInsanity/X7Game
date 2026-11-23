################################################################################
#
# libretro-fbalpha2012-cps1
#
################################################################################

LIBRETRO_FBALPHA2012_CPS1_VERSION = 5542c1848ef81e92db311193b01dc349bc29d7cc
LIBRETRO_FBALPHA2012_CPS1_SITE = $(call github,libretro,fbalpha2012_cps1,$(LIBRETRO_FBALPHA2012_CPS1_VERSION))
LIBRETRO_FBALPHA2012_CPS1_LICENSE = FB Alpha non-commercial, MAME non-commercial, Zlib (zlib, minizip)
LIBRETRO_FBALPHA2012_CPS1_LICENSE_FILES = src/license.txt src/dep/libs/zlib/zlib.h

# The old FB Alpha code type-puns heavily: add -fno-strict-aliasing (and
# -fsigned-char, already the MIPS default, to be explicit). The makefile
# has no variable for extra flags in both CFLAGS and CXXFLAGS, so CC/CXX
# are given again with them (the last CC= on the make command line wins).
# Musashi (C) is the 68000 core, the generated files are in the repo, and
# the little-endian default is right (only a "ppc" host would change it).
# -Wno-narrowing: 2012 C++ built as gcc 14's default C++17.
LIBRETRO_FBALPHA2012_CPS1_MAKE_OPTS = \
	CC="$(TARGET_CC) $(X7_LIBRETRO_CC_FLAGS) -fsigned-char -fno-strict-aliasing" \
	CXX="$(TARGET_CXX) $(X7_LIBRETRO_CXX_FLAGS) -fsigned-char -fno-strict-aliasing -Wno-narrowing"

define LIBRETRO_FBALPHA2012_CPS1_BUILD_CMDS
	$(call X7_LIBRETRO_MAKE,$(@D),makefile.libretro,$(LIBRETRO_FBALPHA2012_CPS1_MAKE_OPTS))
endef

define LIBRETRO_FBALPHA2012_CPS1_INSTALL_TARGET_CMDS
	$(call X7_LIBRETRO_INSTALL,$(@D)/fbalpha2012_cps1_libretro.so,fbalpha2012_cps1)
endef

$(eval $(generic-package))

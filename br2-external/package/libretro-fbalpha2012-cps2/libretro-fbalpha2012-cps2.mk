################################################################################
#
# libretro-fbalpha2012-cps2
#
################################################################################

LIBRETRO_FBALPHA2012_CPS2_VERSION = e3f3ae46f120228b74d41e2b2862f1fbf1d7eb5b
LIBRETRO_FBALPHA2012_CPS2_SITE = $(call github,libretro,fbalpha2012_cps2,$(LIBRETRO_FBALPHA2012_CPS2_VERSION))
LIBRETRO_FBALPHA2012_CPS2_LICENSE = FB Alpha non-commercial, MAME non-commercial
LIBRETRO_FBALPHA2012_CPS2_LICENSE_FILES = src/license.txt

# The old FB Alpha code type-puns heavily: add -fno-strict-aliasing (and
# -fsigned-char, already the MIPS default, to be explicit). The makefile
# has no variable for extra flags in both CFLAGS and CXXFLAGS, so CC/CXX
# are given again with them (the last CC= on the make command line wins).
# Musashi (C) is the 68000 core, the generated files are in the repo, and
# the little-endian default is right (only a "ppc" host would change it).
LIBRETRO_FBALPHA2012_CPS2_MAKE_OPTS = \
	CC="$(TARGET_CC) $(X7_LIBRETRO_CC_FLAGS) -fsigned-char -fno-strict-aliasing" \
	CXX="$(TARGET_CXX) $(X7_LIBRETRO_CXX_FLAGS) -fsigned-char -fno-strict-aliasing -Wno-narrowing"

define LIBRETRO_FBALPHA2012_CPS2_BUILD_CMDS
	$(call X7_LIBRETRO_MAKE,$(@D),makefile.libretro,$(LIBRETRO_FBALPHA2012_CPS2_MAKE_OPTS))
endef

define LIBRETRO_FBALPHA2012_CPS2_INSTALL_TARGET_CMDS
	$(call X7_LIBRETRO_INSTALL,$(@D)/fbalpha2012_cps2_libretro.so,fbalpha2012_cps2)
endef

$(eval $(generic-package))

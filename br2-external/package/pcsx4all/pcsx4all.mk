################################################################################
#
# pcsx4all
#
# gameblabla's PCSX4ALL fork for the RG350 with the X7 Game port
# (Makefile.r36sx and src/port/r36sx come from 0004-*.patch).
#
################################################################################

PCSX4ALL_VERSION = 3fa93ee29d22a2666ba1ec370a0dbd00583699d6
PCSX4ALL_SITE = $(call github,gameblabla,pcsx4all_rs97_rg350,$(PCSX4ALL_VERSION))
# pcsx4all: GPL-2.0+ file headers (gpl.txt holds the GPLv3 text); the MIPS
# dynarec is MIT, minizip Zlib, libchdr BSD-3-Clause, the LZMA SDK public
# domain
PCSX4ALL_LICENSE = GPL-2.0+, MIT (MIPS dynarec), Zlib (minizip), BSD-3-Clause (libchdr), Public Domain (LZMA SDK)
PCSX4ALL_LICENSE_FILES = gpl.txt src/external_lib/LICENSE.minizip src/libchdr/LICENSE.txt
PCSX4ALL_DEPENDENCIES = alsa-lib zlib

# libchdr (CHD images) is the git submodule src/libchdr: empty in the GitHub
# archive. A git download with submodules does not work either (a stray
# top-level "libchdr" gitlink has no .gitmodules entry, so "git submodule
# update --init" fails), so libchdr comes as its own archive, at the commit
# the submodule points to.
PCSX4ALL_LIBCHDR_VERSION = 15ff8d67554f8651f4c971f4d42176214b96ce7b
PCSX4ALL_LIBCHDR_SOURCE = libchdr-$(PCSX4ALL_LIBCHDR_VERSION).tar.gz
PCSX4ALL_EXTRA_DOWNLOADS = \
	https://github.com/rtissera/libchdr/archive/$(PCSX4ALL_LIBCHDR_VERSION)/$(PCSX4ALL_LIBCHDR_SOURCE)

define PCSX4ALL_EXTRACT_LIBCHDR
	mkdir -p $(@D)/src/libchdr
	$(call suitable-extractor,$(PCSX4ALL_LIBCHDR_SOURCE)) \
		$(PCSX4ALL_DL_DIR)/$(PCSX4ALL_LIBCHDR_SOURCE) | \
		$(TAR) --strip-components=1 -C $(@D)/src/libchdr $(TAR_OPTIONS) -
endef
PCSX4ALL_POST_EXTRACT_HOOKS += PCSX4ALL_EXTRACT_LIBCHDR

# Makefile.r36sx sets its own CFLAGS (MIPS32r2, -mtune=74kc, the GCC 14
# relaxations); only the cross compilers and the optimisation come from
# here: -O3 (the SF3000 build of the same emulator uses -Ofast); the GPU
# renderer and the GTE gain most from it
define PCSX4ALL_BUILD_CMDS
	$(TARGET_MAKE_ENV) $(MAKE) -C $(@D) -f Makefile.r36sx \
		CC="$(TARGET_CC)" CXX="$(TARGET_CXX)" OPT="-O3"
endef

define PCSX4ALL_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/pcsx4all $(TARGET_DIR)/usr/bin/pcsx4all
endef

$(eval $(generic-package))

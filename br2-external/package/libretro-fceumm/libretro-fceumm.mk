################################################################################
#
# libretro-fceumm
#
################################################################################

LIBRETRO_FCEUMM_VERSION = fb919fb6fa881aaa6279b765d480220579e5c606
LIBRETRO_FCEUMM_SITE = $(call github,libretro,libretro-fceumm,$(LIBRETRO_FCEUMM_VERSION))
LIBRETRO_FCEUMM_LICENSE = GPL-2.0-or-later
LIBRETRO_FCEUMM_LICENSE_FILES = Copying

# Plain C, no arch detection. The makefile asks git for the version hash;
# output/ can sit inside the X7 Game checkout (CI), where git would report
# our hash, so pass the core's own. WANT_32BPP=0: 16-bit (RGB565) frames,
# what the x7fb video driver shows without converting. HAVE_HDPACK=0: an HD
# pack would switch to large 32-bit frames, far too slow here.
LIBRETRO_FCEUMM_MAKE_OPTS = \
	WANT_32BPP=0 \
	HAVE_HDPACK=0 \
	GIT_VERSION='" $(shell echo $(LIBRETRO_FCEUMM_VERSION) | cut -c1-7)"'

define LIBRETRO_FCEUMM_BUILD_CMDS
	$(call X7_LIBRETRO_MAKE,$(@D),Makefile.libretro,$(LIBRETRO_FCEUMM_MAKE_OPTS))
endef

define LIBRETRO_FCEUMM_INSTALL_TARGET_CMDS
	$(call X7_LIBRETRO_INSTALL,$(@D)/fceumm_libretro.so,fceumm)
endef

$(eval $(generic-package))

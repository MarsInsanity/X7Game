################################################################################
#
# libretro-gpsp
#
################################################################################

LIBRETRO_GPSP_VERSION = 5819380c2ffb0900219d700a382ee68c464ebb99
LIBRETRO_GPSP_SITE = $(call github,libretro,gpsp,$(LIBRETRO_GPSP_VERSION))
LIBRETRO_GPSP_LICENSE = GPL-2.0-or-later
LIBRETRO_GPSP_LICENSE_FILES = COPYING

# platform=unix looks at the build host (uname -a): on x86_64 it would pick
# the x86 dynarec. Force the MIPS one instead:
#  - CPU_ARCH=mips HAVE_DYNAREC=1: mips/mips_stub.S + the MIPS emitter
#  - MMAP_JIT_CACHE=1: the translation cache is mmap()ed RWX next to the
#    core's code (same 256 MB segment, needed for MIPS j/jal)
#  - fpic=-fPIC -DPIC: the stub and the emitted code call C functions
#    through $t9 only when PIC is defined, as the PIC ABI of a shared
#    object needs (the upstream mips32/gcw0 targets do the same)
#  - CODE_DEFINES=-DMIPS_HAS_R2_INSTS: the 74Kc is MIPS32r2 (ext/ins/seb,
#    and synci after patching code); CODE_DEFINES only feeds CFLAGS
#  - FORCE_32BIT_ARCH=0: never add the x86 -m32
# The C++ files use no libstdc++ runtime, so linking with gcc is fine.
# GIT_VERSION: git would report the X7 Game checkout around output/.
LIBRETRO_GPSP_MAKE_OPTS = \
	CPU_ARCH=mips \
	HAVE_DYNAREC=1 \
	MMAP_JIT_CACHE=1 \
	FORCE_32BIT_ARCH=0 \
	fpic="-fPIC -DPIC" \
	CODE_DEFINES=-DMIPS_HAS_R2_INSTS \
	GIT_VERSION='"$(shell echo $(LIBRETRO_GPSP_VERSION) | cut -c1-7)"'

# memmap.c calls the 3-parameter validate_addr_section_mips() with only two
# arguments (a compile error, reached only with MIPS_ARCH + MMAP_JIT_CACHE).
# The third argument is unused for MIPS; add it. No-op once fixed upstream.
define LIBRETRO_GPSP_FIX_MIPS_JIT_MAP
	$(SED) 's/validate_addr_section_mips(ptr, size)/validate_addr_section_mips(ptr, size, 256)/' \
		$(@D)/memmap.c
endef
LIBRETRO_GPSP_POST_PATCH_HOOKS += LIBRETRO_GPSP_FIX_MIPS_JIT_MAP

define LIBRETRO_GPSP_BUILD_CMDS
	$(call X7_LIBRETRO_MAKE,$(@D),Makefile,$(LIBRETRO_GPSP_MAKE_OPTS))
endef

define LIBRETRO_GPSP_INSTALL_TARGET_CMDS
	$(call X7_LIBRETRO_INSTALL,$(@D)/gpsp_libretro.so,gpsp)
endef

$(eval $(generic-package))

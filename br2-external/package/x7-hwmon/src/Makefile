# x7-hwmon, x7-tf2-probe, x7-datapart and x7-bench3d (built by Buildroot
# with the target toolchain)
CFLAGS ?= -O2
CFLAGS += -Wall -Wextra -Wno-unused-parameter -std=gnu11
PREFIX ?= /usr

PROGRAMS = x7-hwmon x7-tf2-probe x7-datapart x7-bench3d

all: $(PROGRAMS)

x7-bench3d: x7-bench3d.c
	$(CC) $(CFLAGS) $(LDFLAGS) -o $@ $< -lm

%: %.c
	$(CC) $(CFLAGS) $(LDFLAGS) -o $@ $<

install: $(PROGRAMS)
	install -D -m 0755 x7-hwmon $(DESTDIR)$(PREFIX)/bin/x7-hwmon
	install -D -m 0755 x7-tf2-probe $(DESTDIR)$(PREFIX)/bin/x7-tf2-probe
	install -D -m 0755 x7-bench3d $(DESTDIR)$(PREFIX)/bin/x7-bench3d
	install -D -m 0755 x7-datapart $(DESTDIR)$(PREFIX)/sbin/x7-datapart

clean:
	rm -f $(PROGRAMS)

.PHONY: all install clean

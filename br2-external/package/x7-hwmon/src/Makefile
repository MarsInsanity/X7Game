# x7-hwmon, x7-tf2-probe, x7-datapart, x7-padd and x7-browser (built by
# Buildroot with the target toolchain)
CFLAGS ?= -O2
# override: Buildroot passes CFLAGS on the command line, which would drop a
# plain += (these are added after its flags)
override CFLAGS += -Wall -Wextra -Wno-unused-parameter -std=gnu11
PREFIX ?= /usr

PROGRAMS = x7-hwmon x7-tf2-probe x7-datapart x7-padd x7-browser

all: $(PROGRAMS)

%: %.c
	$(CC) $(CFLAGS) $(LDFLAGS) -o $@ $<

install: $(PROGRAMS)
	install -D -m 0755 x7-hwmon $(DESTDIR)$(PREFIX)/bin/x7-hwmon
	install -D -m 0755 x7-tf2-probe $(DESTDIR)$(PREFIX)/bin/x7-tf2-probe
	install -D -m 0755 x7-datapart $(DESTDIR)$(PREFIX)/sbin/x7-datapart
	install -D -m 0755 x7-padd $(DESTDIR)$(PREFIX)/sbin/x7-padd
	install -D -m 0755 x7-browser $(DESTDIR)$(PREFIX)/bin/x7-browser

clean:
	rm -f $(PROGRAMS)

.PHONY: all install clean

# x7-hwmon and x7-tf2-probe (built by Buildroot with the target toolchain)
CFLAGS ?= -O2
CFLAGS += -Wall -Wextra -Wno-unused-parameter -std=gnu11
PREFIX ?= /usr

PROGRAMS = x7-hwmon x7-tf2-probe x7-datapart

all: $(PROGRAMS)

%: %.c
	$(CC) $(CFLAGS) $(LDFLAGS) -o $@ $<

install: $(PROGRAMS)
	install -D -m 0755 x7-hwmon $(DESTDIR)$(PREFIX)/bin/x7-hwmon
	install -D -m 0755 x7-tf2-probe $(DESTDIR)$(PREFIX)/bin/x7-tf2-probe
	install -D -m 0755 x7-datapart $(DESTDIR)$(PREFIX)/sbin/x7-datapart

clean:
	rm -f $(PROGRAMS)

.PHONY: all install clean

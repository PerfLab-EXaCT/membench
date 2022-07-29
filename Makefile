SHELL := /bin/bash
SUBDIRS := $(wildcard */.)

all: $(SUBDIRS)

$(SUBDIRS):
	$(MAKE) -C $@

clean:
	for dir in [ $(SUBDIRS) ]; $(MAKE) -C clean $(dir)

.PHONY: all clean $(SUBDIRS)
SHELL := /bin/bash
SUBDIRS := $(wildcard */.)

all: $(SUBDIRS)	

$(SUBDIRS):
	@if [[ "$(@D)" == "sw4lite" ]]; then \
	$(MAKE) -C $@ ckernel=yes openmp=yes; \
	elif [[ "$(@D)" == "NPB3.4-OMP" ]]; then \
	$(MAKE) -C $@ suite; \
	else \
	$(MAKE) -C $@; \
	fi

clean:
	for dir in [ $(SUBDIRS) ]; $(MAKE) -C clean $(dir)

.PHONY: all clean $(SUBDIRS)
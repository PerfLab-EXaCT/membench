CC=gcc
CFLAGS=-fopenmp

all: omp-test

omp-test: omp-test.c
	$(CC) $(CFLAGS) -o $@ $^

clean:
	rm -rf omp-test

.PHONY: all clean
# Intel® Memory Latency Checker

## Usage

### Sequential access bandwidth

```sh
# Write (1:1), PMEM (via file system)
./mlc 0-47 -W5 seq -b 10000 pmem /pmem1
```
  
### Random access bandwidth/dram

```sh
# Read-only, DRAM
./mlc 0-47 -R -U -b 10000 dram 2
```
 
### Idle latency

```sh
./mlc -idle_latency -r  # use to validate ripples
```

## References

- https://www.intel.com/content/www/us/en/developer/articles/tool/intelr-memory-latency-checker.html
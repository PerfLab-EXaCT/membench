# GPU Memory Tracker

## Project

GPU Memory Tracker is a tool to capture memory traces from a GPU (CUDA) program. These traces can further be utilized to perform memory analysis. For more details about the project refer to the project [wiki page](https://gitlab.pnnl.gov/perf-lab/membench/-/wikis/GpuMemoryTracker).

## Prerequisites

- GCC (>10)
- CUDA Toolkit (>11)

## Build

> Set `CUDA_PATH` to approriate location in the Makefile.

```sh
$ make all
```

## Usage

> Set `OUT_FILE_NAME` and `MEM_ACCESS_SIZE` in `GpuMemTrack`

```sh
$ GpuMemTrack <target-cuda-program>
```

## Tests

The test cases for this project is taken from the Nvidia's [Cuda Samples](https://docs.nvidia.com/cuda/cuda-samples/index.html) repository. For more details about this see [test/cuda-samples/README.md](test/cuda-samples/README.md)

## TODOs

- [x] Capture memory access traces
- [ ] Capture time data for the traces
- [ ] Periodic capture of traces (samples) (instead of just capturing a set prefix) with in a stream
- [ ] Revisit `SANITIZER_INSTRUCTION_MEMCPY_ASYNC` with latest CUDA version.
- [ ] Proper bash parsing in `GpuMemTrack` script

## Known Issues

- Some workloads,
    - don't generate any memory traces. (Ex: jacobi, OpenMP, etc.)
    - generate errors (only when GpuMemTrack is used).

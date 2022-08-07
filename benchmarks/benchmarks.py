#!/usr/bin/python
import argparse
import csv
import os
import subprocess
import tqdm
from datetime import datetime

dtnow = lambda: datetime.now().strftime("%m_%d_%Y-%H_%M_%S")
OMP_AFFINITY = None
USE_DEFAULT_OMP_POLICY = False
RESULTS_FOLDER = f'results_{dtnow()}'
omp_threads = [1] + [x for x in range(2, 17, 2)]
cpuid = list(range(0, 15, 2)) + list(range(16, 24))

def get_omp_places(t, policy):
    bitmap = [0 for _ in range(16)]
    if policy == 'close':
        for i in range(t):
            bitmap[i] = 1
    elif policy == 'spread': 
        aligned = 16 - (16%t)
        for i in range(0, aligned, aligned//t):
            bitmap[i] = 1
    elif policy == 'P-spread':
        if (t<=8):
            aligned = 8 - (8%t)
            for i in range(0, aligned, aligned//t):
                bitmap[i] = 1
        else:
            return get_omp_places(t, 'close')
    elif policy == 'E-spread':
        if (t<=8):
            aligned = 8 - (8%t)
            for i in range(0, aligned, aligned//t):
                bitmap[8+i] = 1
        else:
            for i in range(8, 16):
                bitmap[i] = 1
            for i in range(0,t-8):
                bitmap[i] = 1
    places = []
    for i in range(len(bitmap)):
        if bitmap[i] == 1:
            places.append(cpuid[i])
    return ','.join(['{'+str(x)+'}' for x in places])

def print_all_places():
    policies = ['spread', 'close', 'P-spread', 'E-spread']
    for p in policies:
        print('Policy:', p)
        for t in omp_threads:
            print('  OMP_NUM_THREADS=', t, '\t', get_omp_places(t,p))
        print()

def amg():
    print('Running AMG:')
    BIN_PATH = 'amg/test/amg'
    sizes = [x for x in range(256, 513, 64)]
    # problems = [1, 2]
    with open(f'{RESULTS_FOLDER}/{OMP_AFFINITY}/amg-{dtnow()}.csv', 'w', encoding='UTF8') as f:
        writer = csv.writer(f)
        writer.writerow(['problem', 'omp_threads', 'size', 'solve_time(seconds)'])
        pbar_thrds = tqdm.tqdm(omp_threads, ncols=100)
        pbar_sizes = tqdm.tqdm(sizes, ncols=80)
        for omp_thd in pbar_thrds:
            pbar_thrds.set_description(f'[AMG] OMP Threads (current={omp_thd})')
            env = {
                'OMP_NUM_THREADS': str(omp_thd),
            };
            if USE_DEFAULT_OMP_POLICY or OMP_AFFINITY == 'false':
                env['OMP_PROC_BIND'] = OMP_AFFINITY
            else:
                env['OMP_PLACES'] = get_omp_places(omp_thd, OMP_AFFINITY)
            for sz in pbar_sizes:
                # for pb in problem:
                pbar_sizes.set_description(f'[AMG] Running with n={sz}')
                output = subprocess.Popen(
                    [ 
                        BIN_PATH,
                        '-n', str(sz), str(sz), str(sz)
                    ], 
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                output.wait()
                times = []
                for line in output.stdout.readlines():
                    if 'wall clock time' in str(line):
                        splits = line.split()
                        times.append(float(splits[4]))
                solve_time = times[-1]
                writer.writerow([1,omp_thd,sz,solve_time])

def darknet():
    # TODO implement
    pass

def gapbs():
    print('Running GAPBS:')
    BIN_DIR = 'gapbs'
    bins = ['cc', 'pr']
    sizes = [x for x in range(20, 26)]
    pbar_bins = tqdm.tqdm(bins, ncols=50)
    for b in pbar_bins:
        pbar_bins.set_description(f'[GAPBS] Running {b}')
        with open(f'{RESULTS_FOLDER}/{OMP_AFFINITY}/{BIN_DIR}_{b}-{dtnow()}.csv', 'w', encoding='UTF8') as f:
            writer = csv.writer(f)
            writer.writerow(['omp_threads', 'size', 'solve_time(seconds)'])
            pbar_thrds = tqdm.tqdm(omp_threads, ncols=100)
            pbar_sizes = tqdm.tqdm(sizes, ncols=80)
            for omp_thd in pbar_thrds:
                pbar_thrds.set_description(f'[GAPBS/{b}] OMP Threads (current={omp_thd})')
                env = {
                    'OMP_NUM_THREADS': str(omp_thd),
                };
                if USE_DEFAULT_OMP_POLICY or OMP_AFFINITY == 'false':
                    env['OMP_PROC_BIND'] = OMP_AFFINITY
                else:
                    env['OMP_PLACES'] = get_omp_places(omp_thd, OMP_AFFINITY)
                for sz in pbar_sizes:
                    # for pb in problem:
                    pbar_sizes.set_description(f'[GAPBS/{b}] Running with n={sz}')
                    output = subprocess.Popen(
                        [f'{BIN_DIR}/{b}','-g', str(sz)], 
                        env=env,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
                    output.wait()
                    lines = output.stdout.readlines()
                    avg_time = float(lines[-1].strip().split()[-1])
                    writer.writerow([omp_thd,sz,avg_time])

def minivite_x():
    print('Running miniVite-x:')
    BIN_PATH = 'minivite-x/miniVite-v3'
    IN_PATH = 'minivite-x/inputs/arabic-2005.bin'
    # sizes = [x for x in range(300000, 600001, 100000)]   
    with open(f'{RESULTS_FOLDER}/{OMP_AFFINITY}/minivite_x-{dtnow()}.csv', 'w', encoding='UTF8') as f:
        writer = csv.writer(f)
        writer.writerow(['omp_threads', 'size', 'solve_time(seconds)'])
        pbar_thrds = tqdm.tqdm(omp_threads, ncols=100)
        # pbar_sizes = tqdm.tqdm(sizes, ncols=80)
        for omp_thd in pbar_thrds:
            pbar_thrds.set_description(f'[miniVite-x] OMP Threads (current={omp_thd})')
            env = {
                'OMP_NUM_THREADS': str(omp_thd),
            };
            if USE_DEFAULT_OMP_POLICY or OMP_AFFINITY == 'false':
                env['OMP_PROC_BIND'] = OMP_AFFINITY
            else:
                env['OMP_PLACES'] = get_omp_places(omp_thd, OMP_AFFINITY)
            # for sz in pbar_sizes:
                # for pb in problem:
                # pbar_sizes.set_description(f'[miniVite-x] Running with n={sz}')
            output = subprocess.Popen(
                [BIN_PATH,'add','-f', IN_PATH], 
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            output.wait()
            lines = output.stdout.readlines()
            avg_time = float(lines[-2].strip().split()[-1])
            writer.writerow([omp_thd,avg_time])

def sw4lite():
    print('Running sw4lite:')
    BIN_PATH = 'sw4lite/optimize_mp_c/sw4lite'
    with open(f'{RESULTS_FOLDER}/{OMP_AFFINITY}/sw4lite-{dtnow()}.csv', 'w', encoding='UTF8') as f:
        writer = csv.writer(f)
        writer.writerow(['omp_threads', 'solve_time(seconds)'])
        pbar_thrds = tqdm.tqdm(omp_threads, ncols=100)
        for omp_thd in pbar_thrds:
            env = {
                'OMP_NUM_THREADS': str(omp_thd),
            }
            if USE_DEFAULT_OMP_POLICY or OMP_AFFINITY == 'false':
                env['OMP_PROC_BIND'] = OMP_AFFINITY
            else:
                env['OMP_PLACES'] = get_omp_places(omp_thd, OMP_AFFINITY)
            pbar_thrds.set_description(f'[sw4lite] OMP Threads (current={omp_thd})')
            output = subprocess.Popen(
                ['mpirun','-np', '1', BIN_PATH,'sw4lite/tests/pointsource/pointsource.in'], 
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            output.wait()
            lines = output.stdout.readlines()
            time = float(lines[-5].strip().split()[0])
            writer.writerow([omp_thd,time])

def nbp():
    print('Running NAS Benchmarks:')
    BIN_DIR = 'NPB3.4-OMP/bin'
    bins = ['bt.C.x', 'ft.C.x', 'lu.C.x', 'sp.C.x' ]
    pbar_bins = tqdm.tqdm(bins, ncols=50)
    for b in pbar_bins:
        pbar_bins.set_description(f'[NPB] Running {b}')
        with open(f'{RESULTS_FOLDER}/{OMP_AFFINITY}/NPB_{b.replace(".","_")}-{dtnow()}.csv', 'w', encoding='UTF8') as f:
            writer = csv.writer(f)
            writer.writerow(['omp_threads', 'solve_time(seconds)'])
            pbar_thrds = tqdm.tqdm(omp_threads, ncols=100)
            for omp_thd in pbar_thrds:
                pbar_thrds.set_description(f'[NPB/{b}] OMP Threads (current={omp_thd})')
                env = {
                    'OMP_NUM_THREADS': str(omp_thd),
                };
                if USE_DEFAULT_OMP_POLICY or OMP_AFFINITY == 'false':
                    env['OMP_PROC_BIND'] = OMP_AFFINITY
                else:
                    env['OMP_PLACES'] = get_omp_places(omp_thd, OMP_AFFINITY)
                output = subprocess.Popen(
                    [f'{BIN_DIR}/{b}'], 
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                output.wait()
                lines = output.stdout.readlines()
                avg_time = float(lines[-26].strip().split()[-1])
                writer.writerow([omp_thd,avg_time])

def stream():
    print('Running STREAM:')
    BIN_PATH = 'STREAM/stream_c.exe'
    with open(f'{RESULTS_FOLDER}/{OMP_AFFINITY}/STREAM-{dtnow()}.csv', 'w', encoding='UTF8') as f:
        writer = csv.writer(f)
        writer.writerow(['omp_threads', 'function', 'bandwidth', 'avg_time', 'min_time', 'max_time'])
        pbar_thrds = tqdm.tqdm(omp_threads, ncols=100)
        for omp_thd in pbar_thrds:
            env = {
                'OMP_NUM_THREADS': str(omp_thd),
            };
            if USE_DEFAULT_OMP_POLICY or OMP_AFFINITY == 'false':
                env['OMP_PROC_BIND'] = OMP_AFFINITY
            else:
                env['OMP_PLACES'] = get_omp_places(omp_thd, OMP_AFFINITY)
            pbar_thrds.set_description(f'[STREAM] OMP Threads (current={omp_thd})')
            output = subprocess.Popen(
                [BIN_PATH], 
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            output.wait()
            lines = output.stdout.readlines()
            for line in lines[-7:-3]:
                splits = line.strip().split()
                writer.writerow([omp_thd]+[splits[0].decode("utf-8").replace(':','')]+[float(x) for x in splits[1:]])

def run_benchmarks():
    for i in range(3):
        print(f'Running complete benchmark suite (iteration={i})')
        amg()
        darknet()
        gapbs()
        minivite_x()
        sw4lite()
        nbp()
        stream()

def run_mlc():
    print('Running IntelMLC:')
    BIN_PATH = 'IntelMLC/mlc'
    os.makedirs(f'{RESULTS_FOLDER}/IntelMLC', exist_ok=True)
    inputs = ['randR', 'randW5', 'seqR', 'seqW5']
    pbar_itrs = tqdm.tqdm(range(3), ncols=100)
    for i in pbar_itrs:
        pbar_itrs.set_description(f'[IntelMLC] Running iteration = {i}')
        pbar_inps = tqdm.tqdm(inputs, ncols=80)
        for inp in pbar_inps:
            pbar_inps.set_description(f'[IntelMLC] Running with config={inp}.config')
            with open(f'{RESULTS_FOLDER}/IntelMLC/{inp}_{dtnow()}.out', 'wb') as out:
                subprocess.Popen(
                    ['sudo', BIN_PATH, '--loaded_latency', f'-oIntelMLC/configs/{inp}.config'], 
                    stdout=out,
                    stderr=out
                ).wait()

def init():
    os.makedirs(f'{RESULTS_FOLDER}/{OMP_AFFINITY}', exist_ok=True)

def run():
    run_mlc()
    global OMP_AFFINITY
    affinities = ['spread', 'close', 'false']
    if not USE_DEFAULT_OMP_POLICY:
        affinities += ['P-spread', 'E-spread']
    for affinity in affinities:
        OMP_AFFINITY = affinity
        init()
        run_benchmarks()

def use_default():
    global USE_DEFAULT_OMP_POLICY
    USE_DEFAULT_OMP_POLICY = True

def print_all_benchmarks():
    print(
"""
    amg
    darknet (TODO)
    gapbs
    minivite_x
    sw4lite
    nbp
    stream
"""
    )

def main():
    parser = argparse.ArgumentParser(
        prog='benchmarks.py',
        description='A simple script for running benchmarks'
    )
    group = parser.add_mutually_exclusive_group()
    parser.add_argument('-d', '--default', action='store_true', help='Use default OMP spread/close policies (Ignores P/E-spread policies)')
    group.add_argument('-l', '--list', action='store_true', required=False, help='list all benchmarks')
    group.add_argument('-p', '--places', action='store_true', required=False, help='list all OMP places')
    group.add_argument('-r', '--run', action='store_true', required=False, help='run the benchmarks')
    args = parser.parse_args()

    if args.default:
        global USE_DEFAULT_OMP_POLICY
        USE_DEFAULT_OMP_POLICY = False

    if args.list:
        print_all_benchmarks()
    elif args.places:
        print_all_places()
    elif args.run:
        run()
    else:
        parser.print_help()
    
if __name__ == '__main__':
    # TODO: Handle USE_CUSTOM_AFFINITY from CLI args
    main()
#!/usr/bin/python
import csv
import os
import subprocess
import tqdm
from datetime import datetime

dtnow = lambda: datetime.now().strftime("%m_%d_%Y-%H_%M_%S")
OMP_AFFINITY = None
USE_CUSTOM_AFFINITY = True
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
            if USE_CUSTOM_AFFINITY:
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
                times = []
                for line in output.stdout:
                    if 'wall clock time' in str(line):
                        splits = line.split()
                        times.append(float(splits[4]))
                solve_time = times[-1]
                writer.writerow([1,omp_thd,sz,solve_time])

def darknet():
    # TODO implement
    pass

def gapbs():
    print('Running GAPBS/cc:')
    BIN_PATH = 'gapbs/cc'
    sizes = [x for x in range(20, 26)]    
    with open(f'{RESULTS_FOLDER}/{OMP_AFFINITY}/gapbs_cc-{dtnow()}.csv', 'w', encoding='UTF8') as f:
        writer = csv.writer(f)
        writer.writerow(['omp_threads', 'size', 'solve_time(seconds)'])
        pbar_thrds = tqdm.tqdm(omp_threads, ncols=100)
        pbar_sizes = tqdm.tqdm(sizes, ncols=80)
        for omp_thd in pbar_thrds:
            pbar_thrds.set_description(f'[GAPBS/cc] OMP Threads (current={omp_thd})')
            env = {
                'OMP_NUM_THREADS': str(omp_thd),
            };
            if USE_CUSTOM_AFFINITY:
                env['OMP_PROC_BIND'] = OMP_AFFINITY
            else:
                env['OMP_PLACES'] = get_omp_places(omp_thd, OMP_AFFINITY)
            for sz in pbar_sizes:
                # for pb in problem:
                pbar_sizes.set_description(f'[GAPBS/cc] Running with n={sz}')
                output = subprocess.Popen(
                    [BIN_PATH,'-g', str(sz)], 
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                lines = output.stdout.readlines()
                avg_time = float(lines[-1].strip().split()[-1])
                writer.writerow([omp_thd,sz,avg_time])

def minivite_x():
    print('Running miniVite-x:')
    BIN_PATH = 'minivite-x/miniVite-v3'
    sizes = [x for x in range(300000, 600001, 100000)]    
    with open(f'{RESULTS_FOLDER}/{OMP_AFFINITY}/minivite_x-{dtnow()}.csv', 'w', encoding='UTF8') as f:
        writer = csv.writer(f)
        writer.writerow(['omp_threads', 'size', 'solve_time(seconds)'])
        pbar_thrds = tqdm.tqdm(omp_threads, ncols=100)
        pbar_sizes = tqdm.tqdm(sizes, ncols=80)
        for omp_thd in pbar_thrds:
            pbar_thrds.set_description(f'[miniVite-x] OMP Threads (current={omp_thd})')
            env = {
                'OMP_NUM_THREADS': str(omp_thd),
            };
            if USE_CUSTOM_AFFINITY:
                env['OMP_PROC_BIND'] = OMP_AFFINITY
            else:
                env['OMP_PLACES'] = get_omp_places(omp_thd, OMP_AFFINITY)
            for sz in pbar_sizes:
                # for pb in problem:
                pbar_sizes.set_description(f'[miniVite-x] Running with n={sz}')
                output = subprocess.Popen(
                    [BIN_PATH,'add','-n', str(sz)], 
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                lines = output.stdout.readlines()
                avg_time = float(lines[-2].strip().split()[-1])
                writer.writerow([omp_thd,sz,avg_time])

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
            };
            if USE_CUSTOM_AFFINITY:
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
            lines = output.stdout.readlines()
            time = float(lines[-5].strip().split()[0])
            writer.writerow([omp_thd,time])

def run_benchmarks():
    for i in range(3):
        print(f'Running complete benchmark suite (iteration={i})')
        amg()
        darknet()
        gapbs()
        minivite_x()
        sw4lite()

def init():
    os.makedirs(f'{RESULTS_FOLDER}/{OMP_AFFINITY}', exist_ok=True)

def main():
    global OMP_AFFINITY
    affinities = ['spread', 'close']
    if USE_CUSTOM_AFFINITY:
        affinities += ['P-spread', 'E-spread']
    for affinity in affinities:
        OMP_AFFINITY = affinity
        init()
        run_benchmarks()

if __name__ == '__main__':
    # TODO: Handle USE_CUSTOM_AFFINITY from CLI args
    main()
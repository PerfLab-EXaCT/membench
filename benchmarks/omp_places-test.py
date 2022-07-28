#!/usr/bin/python
import csv
import os
import subprocess
import tqdm
from datetime import datetime

dtnow = lambda: datetime.now().strftime("%m_%d_%Y-%H_%M_%S")
omp_threads = [1] + [x for x in range(2, 17, 2)]
cpuid = list(range(0, 15, 2)) + list(range(16, 24))

RESULTS_FOLDER = f'results_{dtnow()}'
OMP_AFFINITY = None

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

# def test():
#     affinities = ['spread', 'close', 'P-spread', 'E-spread']
#     for affinity in affinities: 
#         print(affinity)
#         for t in omp_threads:
#             print(t, '\t', get_omp_places(t, affinity))


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
            pbar_thrds.set_description(f'[AMG] OMP Threads (current={omp_thd})')
            for sz in pbar_sizes:
                # for pb in problem:
                pbar_sizes.set_description(f'[AMG] Running with n={sz}')
                output = subprocess.Popen(
                    [BIN_PATH,'-g', str(sz)], 
                    env={
                        'OMP_NUM_THREADS': str(omp_thd),
                        'OMP_PLACES': get_omp_places(omp_thd, OMP_AFFINITY)
                    },
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                lines = output.stdout.readlines()
                avg_time = float(lines[-1].strip().split()[-1])
                writer.writerow([omp_thd,sz,avg_time])

def init():
    os.makedirs(f'{RESULTS_FOLDER}/{OMP_AFFINITY}', exist_ok=True)

def main():
    global OMP_AFFINITY
    affinities = ['spread', 'close', 'P-spread', 'E-spread']
    for affinity in affinities:
        OMP_AFFINITY = affinity
        init()
        gapbs()

if __name__ == '__main__':
    # test()
    main()
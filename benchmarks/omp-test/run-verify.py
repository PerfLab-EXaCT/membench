#! /usr/bin/python

import os
import subprocess

BIN='./omp-test'

omp_threads = [1] + [x for x in range(2, 17, 2)]
affinities = ['spread', 'close', 'P-spread', 'E-spread']
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

def verify(thrds, aff):
    with open(f'results/{thrds}-{aff}.out', 'r', encoding='latin-1') as out:
        lines = out.readlines()
        places = get_omp_places(thrds, aff)
        cpus = []
        for line in lines:
            if 'cpuset' in line:
                cpus.append(int(line.strip().split()[-1]))
        cpus.sort()
        passed = places == ','.join(['{'+str(x)+'}' for x in cpus])
        return 'PASS' if passed else 'FAIL'

def main():
    os.makedirs('results', exist_ok=True)
    for omp_thd in omp_threads:
        for aff in affinities:
            env = {
                'OMP_NUM_THREADS': str(omp_thd),
                'OMP_PLACES': get_omp_places(omp_thd, aff)
            }
            with open(f'results/{omp_thd}-{aff}.out', 'w') as out:
                subprocess.Popen([BIN], env=env, stdout=out).wait()
            print(f'{omp_thd}_{aff}: {verify(omp_thd, aff)}')

if __name__ == '__main__':
    main()
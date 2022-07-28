import os
import csv

TRACES_PATH = 'traces/'
OUTPUT_PATH = 'output/'

tests = [
    '/people/velu585/gpu-memory-tracker/output1/matrixMul_2022-07-12_11-33-40.csv'
]

traces = {}

def main():
    os.makedirs(TRACES_PATH, exist_ok=True)
    for t in tests:
        with open(t) as csvfile:
            csvreader = csv.reader(csvfile)
            part = 0
            for row in csvreader:
                if part not in traces.keys():
                    traces[part] = []
                if '0x' in row[0]:
                    traces[part].append(f'{row[0]} {row[-2]} 0 0 {part+1}')
                elif 'ProgramCounter' not in row[0]:
                    part += 1
    print('Total samples', len(traces.keys()))
    with open(f'{TRACES_PATH}/matMul.trace', 'w') as tf:
        for key in traces.keys():
            sample = traces[key]
            for row in sample:
                tf.write(row + '\n')
    print('Writing traces to file...\nDone.')
                    
if __name__ == '__main__':
    main()
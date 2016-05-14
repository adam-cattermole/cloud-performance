import gzip
import bz2
import lzma

import os
from datetime import datetime
import re

DATA_FIELDS = { 'label': 0,
                'price': 1,
                'time': 2,
                'type': 3,
                'os': 4,
                'region': 5}

def main():
    path = 'data/'
    for root, subdirs, files in os.walk(path):
        if len(files) > 0:
            for filename in files:
                filepath = os.path.join(root, filename)
                if filepath.endswith('.gz'):
                    process_gz(filepath)
                elif filepath.endswith('.bz2'):
                    process_bz2(filepath)
                elif filepath.endswith('.xz'):
                    process_xz(filepath)
                elif filepath.endswith('.txt'):
                    process_txt(filepath)
                else:
                    print(filepath)
                # print('root: {}, subdir: {}, file: {}'.format(root, subdirs, files))
    # for yeardir in os.listdir(path):
    #     for filename in os.listdir(filepath):
    #         filepath += filename
    #         if filename.endswith("gz"):
    #             process_gz(filename)



def process_txt(filepath):
    f = open(filepath, 'r')
    for line in f.readlines()[1:]:
        output = line.replace('\n', '').split('\t')
        if len(output) == len(DATA_FIELDS):
        # print(output[DATA_FIELDS['time']])
            # print(output)
            output[DATA_FIELDS['time']] = calculate_epoch(output[DATA_FIELDS['time']])
            # date = datetime.strptime(output[DATA_FIELDS['time']], '%Y-%m-%dT%H:%M:%S+0100')
            # output[DATA_FIELDS['time']] = (date - datetime(1970,1,1)).total_seconds()
            print(output)
            # print(date)


    f.close()
    print("txt")


def process_gz(filepath):
    #TODO: Process gz files
    print("gz")

def process_bz2(filepath):
    #TODO: Process bz2 files
    print("bz2")

def process_xz(filepath):
    #TODO: Process xz files
    print("xz")


def calculate_epoch(time):
    date = datetime.strptime(time, '%Y-%m-%dT%H:%M:%S+0100')
    return (date - datetime(1970,1,1)).total_seconds()


if __name__ == '__main__':
    main()

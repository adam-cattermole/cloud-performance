import gzip
import bz2
import lzma

import os
from datetime import datetime
import re

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
    for line in f.readlines():
        output = line.split('\t')
        print(output)


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





if __name__ == '__main__':
    main()

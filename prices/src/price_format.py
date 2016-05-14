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
                'platform': 4,
                'region': 5}

def main():
    path = 'data/'
    out_path = 'out/price_info.txt'
    f_clear = open(out_path, 'w')
    f_clear.close()
    with open('out/price_info.txt', 'a') as outfile:
        for root, subdirs, files in os.walk(path):
            if len(files) > 0:
                for filename in files:
                    filepath = os.path.join(root, filename)
                    if filepath.endswith('.gz'):
                        output = process_gz(filepath, outfile)
                    elif filepath.endswith('.bz2'):
                        output = process_bz2(filepath, outfile)
                    elif filepath.endswith('.xz'):
                        output = process_xz(filepath, outfile)
                    elif filepath.endswith('.txt'):
                        output = process_txt(filepath, outfile)
                    else:
                        output = None
                        print(filepath)

                    if output:
                        write_output(output, outfile)
                    # print('root: {}, subdir: {}, file: {}'.format(root, subdirs, files))
        # for yeardir in os.listdir(path):
        #     for filename in os.listdir(filepath):
        #         filepath += filename
        #         if filename.endswith("gz"):
        #             process_gz(filename)



def process_txt(filepath, outfile):
    with open(filepath, 'r') as f:
        output = []
        for line in f.readlines()[1:]:
            line_data = line.replace('\n', '').split('\t')
            if len(line_data) == len(DATA_FIELDS):
            # print(output[DATA_FIELDS['time']])
                # print(output)
                line_data[DATA_FIELDS['time']] = calculate_epoch(line_data[DATA_FIELDS['time']])
                output.append(line_data)
                # date = datetime.strptime(output[DATA_FIELDS['time']], '%Y-%m-%dT%H:%M:%S+0100')
                # output[DATA_FIELDS['time']] = (date - datetime(1970,1,1)).total_seconds()

                # print(date)
        f.close()
        print("txt")
        return output


def process_gz(filepath, outfile):
    #TODO: Process gz files
    print("gz")

def process_bz2(filepath, outfile):
    #TODO: Process bz2 files
    print("bz2")

def process_xz(filepath, outfile):
    #TODO: Process xz files
    print("xz")


def write_output(output, outfile):
    for data_item in sorted(output, key = lambda x: x[DATA_FIELDS['time']]):
        outfile.write('{},{},{},{},{}\n'.format(data_item[DATA_FIELDS['time']],
                                                data_item[DATA_FIELDS['price']],
                                                data_item[DATA_FIELDS['type']],
                                                data_item[DATA_FIELDS['region']],
                                                data_item[DATA_FIELDS['platform']]))


def calculate_epoch(time):
    date = datetime.strptime(time, '%Y-%m-%dT%H:%M:%S+0100')
    return (date - datetime(1970,1,1)).total_seconds()


if __name__ == '__main__':
    main()

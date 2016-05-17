import gzip
import bz2
import lzma

import os
import threading
import time
from datetime import datetime
from dateutil import tz
import re

DATA_FIELDS = { 'label': 0,
                'price': 1,
                'time': 2,
                'type': 3,
                'platform': 4,
                'region': 5}


POLL_RATE = 15
MAX_THREADS = 20

# output = []

thread_pool = {}
pool_lock = threading.Lock()

def main():
    path = 'data/'
    out_path = 'out/price_info.txt'
    f_clear = open(out_path, 'w')
    f_clear.close()
    with open('out/price_info.txt', 'a') as outfile:
        output = []
        for root, subdirs, files in os.walk(path):
            if len(files) > 0 and 'obsolete'not in root:
                print(root)
                for filename in files:
                    # success = False
                    # while not success:
                    #     if len(thread_pool) < MAX_THREADS:
                            filepath = os.path.join(root, filename)
                            thread_pool[filename] = ProcessFileThread(filename, filepath, output)
                            thread_pool[filename].start()
                            success = True
                        # else:
                        #     time.sleep(POLL_RATE)
                while len(thread_pool) > 0:
                    time.sleep(POLL_RATE)
                if output:
                    write_output(output, outfile)
                    output.clear()


class ProcessFileThread(threading.Thread):
    def __init__(self, name, filepath, output):
        threading.Thread.__init__(self)
        self.name = name
        self.filepath = filepath
        self.output = output

    def run(self):
        print('\t{}.Start'.format(self.name))
        if self.filepath.endswith('.txt.gz'):
            self.output.append(process_gzip(self.filepath))
        elif self.filepath.endswith('.txt.bz2'):
            self.output.append(process_bz2(self.filepath))
        elif self.filepath.endswith('.txt.xz'):
            self.output.append(process_xz(self.filepath))
        elif self.filepath.endswith('.txt'):
            self.output.append(process_txt(self.filepath))
        else:
            # output = None
            print('\tINVALID: {}'.format(self.name))
        print('\t{}.Complete'.format(self.name))
        clear_thread(self.name)




        # for line in f.readlines()[1:]:
        #     line_data = line.replace('\n', '').split('\t')
        #     if len(line_data) == len(DATA_FIELDS):
        #     # print(output[DATA_FIELDS['time']])
        #         # print(output)
        #         line_data[DATA_FIELDS['time']] = calculate_epoch(line_data[DATA_FIELDS['time']])
        #         output.append(line_data)
        #         # date = datetime.strptime(output[DATA_FIELDS['time']], '%Y-%m-%dT%H:%M:%S+0100')
        #         # output[DATA_FIELDS['time']] = (date - datetime(1970,1,1)).total_seconds()
        #
        #         # print(date)
        # f.close()
        # print("txt")
        # return output

def process_txt(filepath):
    with open(filepath, 'r') as f:
        content = f.readlines()
    return process_content(content)

def process_gzip(filepath):
    with gzip.open(filepath, 'rt', encoding='utf-8') as f:
        content = f.readlines()
    return process_content(content)

def process_bz2(filepath):
    with bz2.open(filepath, 'rt', encoding='utf-8') as f:
        content = f.readlines()
    return process_content(content)

def process_xz(filepath):
    with lzma.open(filepath, 'rt', encoding='utf-8') as f:
        content = f.readlines()
    return process_content(content)


def process_content(content):
    file_data = []
    for line in content[1:]:
        line_data = line.replace('\n', '').split('\t')
        if len(line_data) == len(DATA_FIELDS):
            line_data[DATA_FIELDS['time']] = calculate_epoch(line_data[DATA_FIELDS['time']])
            file_data.append(line_data)
            # print(line_data)
    return file_data

def write_output(output, outfile):
    # remove_duplicates()
    output = list({tuple(y) for x in output for y in x})
    for data_item in sorted(output, key = lambda x: x[DATA_FIELDS['time']]):
        outfile.write('{},{},{},{},{}\n'.format(data_item[DATA_FIELDS['time']],
                                                data_item[DATA_FIELDS['price']],
                                                data_item[DATA_FIELDS['type']],
                                                data_item[DATA_FIELDS['region']],
                                                data_item[DATA_FIELDS['platform']]))

def remove_duplicates():
    # output = set()
    # for f in data:
    #     for line in f:
    #         output.add(tuple(line))
    output = list({tuple(y) for x in output for y in x})
    # return list(output)


def calculate_epoch(time):
    date = datetime.strptime(time, '%Y-%m-%dT%H:%M:%S%z')
    return (date - datetime(1970,1,1, tzinfo=tz.tzutc())).total_seconds()

def clear_thread(name):
    with pool_lock:
        thread_pool.pop(name)


if __name__ == '__main__':
    main()

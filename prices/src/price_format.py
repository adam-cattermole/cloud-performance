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
MAX_THREADS = 1000 # (disabled)

thread_pool = {}
pool_lock = threading.Lock()

def main():
    path = 'data/'
    out_path = 'out/price_info.csv'
    f_clear = open(out_path, 'w')
    f_clear.close()
    with open(out_path, 'a') as outfile:
        output = []
        for root, subdirs, files in os.walk(path):
            if len(files) > 0 and 'obsolete'not in root:
                print(root)
                for filename in files:
                    success = False
                    while not success:
                        if len(thread_pool) < MAX_THREADS:
                            filepath = os.path.join(root, filename)
                            thread_pool[filename] = ProcessFileThread(filename, filepath, output)
                            thread_pool[filename].start()
                            success = True
                        else:
                            time.sleep(POLL_RATE)
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


    def tPrint(self, string):
        print('\t{}: {} ({})'.format(datetime.time(datetime.now()), string, self.name))

    def run(self):
        self.tPrint('Start')
        if self.filepath.endswith('.txt.gz') or self.filepath.endswith('.sorted.gz'):
            self.output.append(process_gzip(self.filepath))
        elif self.filepath.endswith('.txt.bz2'):
            self.output.append(process_bz2(self.filepath))
        elif self.filepath.endswith('.txt.xz'):
            self.output.append(process_xz(self.filepath))
        elif self.filepath.endswith('.txt'):
            self.output.append(process_txt(self.filepath))
        else:
            # output = None
            self.tPrint('INVALID')
        self.tPrint('Complete')
        clear_thread(self.name)


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
            str_output = '{},{},{},{},{}\n'.format(line_data[DATA_FIELDS['time']],
                                                 line_data[DATA_FIELDS['price']],
                                                 line_data[DATA_FIELDS['type']],
                                                 line_data[DATA_FIELDS['region']],
                                                 line_data[DATA_FIELDS['platform']])
            file_data.append(str_output)
            # print(line_data)
    return file_data

def write_output(output, outfile):
    output = list({y for x in output for y in x})
    outfile.writelines(sorted(output))

def calculate_epoch(time):
    date = datetime.strptime(time, '%Y-%m-%dT%H:%M:%S%z')
    return (date - datetime(1970,1,1, tzinfo=tz.tzutc())).total_seconds()

def clear_thread(name):
    with pool_lock:
        thread_pool.pop(name)

if __name__ == '__main__':
    main()

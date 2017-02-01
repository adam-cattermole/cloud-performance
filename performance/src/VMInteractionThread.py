import threading
import datetime


class VMInteractionThread(threading.Thread):

    def __init__(self, name, size, mem, iteration):
        threading.Thread.__init__(self)
        self.name = name
        self.size = size
        self.mem = mem
        self.iteration = iteration
        self.complete = False

    def tPrint(self, string):
        print('{}: Thread {}: {}'.format(
            datetime.datetime.time(datetime.datetime.now()),
            self.name, string))

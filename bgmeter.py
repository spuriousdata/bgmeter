#!/usr/bin/env python
import serial
import re
import os
import atexit
import readline
import logging

from cmd import Cmd

import matplotlib.pyplot as plt

from meters import Meter

history_file = os.path.join(os.path.expanduser("~"), ".bgmeter_history")
try:
    readline.read_history_file(history_file)
except IOError:
    pass

atexit.register(readline.write_history_file, history_file)

logging.basicConfig(level=logging.DEBUG)

class BgMeterCLI(Cmd, Meter):
    intro = "BGMeter command line interface"
    prompt = "bgmeter> "

    def __init__(self, *args, **kwargs):
        Cmd.__init__(self, *args, **kwargs) # Not a new-style object?
        self._setup_db()
        self._detect_meter()

    def do_update(self, x):
        self._update()
        print "done"

    def do_plot(self, x):
        r = self._get_graph_data()
        plt.plot([x[0] for x in r], [x[1] for x in r], 'bo-')
        plt.ylabel('Blood Glucose')
        plt.xlabel('Date')
        plt.axis([
            min([x[0] for x in r]), 
            max([x[0] for x in r]), 
            min([x[1] for x in r])-50,
            max([x[1] for x in r])+50
        ])
        plt.axes().yaxis.grid()
        plt.show()


    def do_version(self, x):
        print self.device.version()

    def do_exit(self, x):
        "exit" 
        return True

    def do_quit(self, x):
        "exit" 
        return True

    def do_bye(self, x):
        "exit" 
        return True

    def do_q(self, x):
        "exit" 
        return True

def main():
    BgMeterCLI().cmdloop()

if __name__ == '__main__':
    main()

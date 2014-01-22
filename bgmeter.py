#!/usr/bin/env python
import serial
import re
import os
import atexit
import readline
import logging

from cmd import Cmd

import matplotlib.pyplot as plt
from dateutil import parser

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

    """
    ot = OneTouchUltra2()
    r,c = ot.records()
    plt.plot([x['date'] for x in r], [x['bg'] for x in r], 'bo-')
    plt.ylabel('Blood Glucose')
    plt.xlabel('Date')
    plt.axis([
        min([x['date'] for x in r]), 
        max([x['date'] for x in r]), 
        min([x['bg'] for x in r])-50,
        max([x['bg'] for x in r])+50
    ])
    plt.axes().yaxis.grid()
    plt.show()
    """


if __name__ == '__main__':
    main()

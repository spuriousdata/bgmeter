#!/usr/bin/env python
import serial
import re
import matplotlib.pyplot as plt

from dateutil import parser


class Meter(object):
    def __init__(self, device, speed, bits, stop, parity, timeout=1):
        self.device = serial.Serial(device, speed, bits, stop, parity, timeout=timeout)

    def _cmd(self, cmd):
        self.device.write(cmd)

class OneTouchUltra2(Meter):
    record_header = re.compile(r'P (\d\d\d),"([^"]+)","([^"]+) "')
    record_row = re.compile(r'P "(\w+)","([\w\/]+)","([\w:]+)   ","([\s\d]+)","([NBA])","(\d+)".*')
    FLAGS = {
        'N': "None",
        'B': "Before Meal",
        'A': "After Meal",
    }
    COMMENTS = [
        'No Comment',
        'Not Enough Food',
        'Too Much Food',
        'Mild Exercise',
        'Hard Exercise',
        'Medication',
        'Stress',
        'Illness',
        'Feel Hypo',
        'Menses',
        'Vacation',
        'Other',
    ]
    def __init__(self, device='/dev/ttyUSB0'):
        super(OneTouchUltra2, self).__init__(device, 9600, 8, 'N', 1, timeout=20)

    def _cmd(self, cmd):
        super(OneTouchUltra2, self)._cmd("\x11\r%s" % cmd)

    def _readline(self):
        return self._checksum(self.device.readline())

    def _checksum(self, data):
        last_space = data.rfind(' ')
        resp = data[:last_space]
        theirs = data[last_space+1:].strip()
        ours = "%0.4X" % (sum([ord(x) for x in resp]) & 0xFFFF)
        if ours != theirs:
            raise Exception("Checksum mismatch")
        return resp
        
    def version(self):
        self._cmd('DM?')
        return self._readline()

    def serial(self):
        self._cmd('DM@')
        return self._readline()

    def datetime(self):
        self._cmd('DMF')
        return self._readline()

    def records(self):
        self._cmd('DMP')
        rows, sn, units = OneTouchUltra2.record_header.search(self._readline()).groups()
        rows = int(rows)
        records = []
        control_records = []
        for x in xrange(0, rows):
            row = self._readline()
            #record_row = re.compile(r'P "(\w+)","([\w\/]+)","([\w:]+)   ","([\s\d]+)","([NBA])","(\d+)".*')
            day, date, time, bg, flag, comment = OneTouchUltra2.record_row.search(row).groups()
            record = {
                'date': parser.parse("%s %s" % (date,time)),
                'bg': int(bg),
                'flag': OneTouchUltra2.FLAGS[flag],
                'comment': OneTouchUltra2.COMMENTS[int(comment)],
                'units': units,
            }
            if bg.startswith('C'):
                control_records.append(record)
            else:
                records.append(record)

        return records, control_records


    def units(self):
        self._cmd('DMSU?')
        return self._readline()

    def timeformat(self):
        self._cmd('DMST?')
        return self._readline()


def main():
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


if __name__ == '__main__':
    main()

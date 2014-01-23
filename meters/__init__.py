import os
import sqlite3
import logging
import importlib

from serial.tools import list_ports
from dateutil import parser

class Meter(object):

    def _setup_db(self):
        self.db = sqlite3.connect(os.path.join(os.path.expanduser("~"),".bgmeter.db"))
        cur = self.db.cursor()
        cur.execute("""
            SELECT name 
            FROM sqlite_master 
            WHERE type='table' AND name='schema_version'
        """)
        if cur.fetchone() is None:
            cur.execute("CREATE TABLE schema_version (version integer)")
            cur.execute("""
                CREATE TABLE bg_record (
                    device_id text,
                    datetime text,
                    bg real,
                    flag text,
                    comment text,
                    notes text,
                    units text
                )
            """)
            cur.execute("INSERT INTO schema_version VALUES (1)")
            self.db.commit()
        else:
            logging.info("Found existing db")
            """
            In the future we can select version from schema_version and
            upgrade the schema accordingly if necessary
            """
            pass
    
    def _detect_meter(self):
        try:
            ports = list_ports.comports()
        except:
            logging.warning("Cannot autodetect serial ports, perhaps you are"
                    " running a pre-2.7 version of pyserial. We'll try the default"
                    " device (/dev/ttyUSB0)")
        vendor_device = {
            'Prolific Technology, Inc. PL2303 Serial Port ':
                ("meters.otultra2", "OneTouchUltra2"),
        }
        try:
            device, vendor = [(x[0],x[1]) for x in ports if x[1] in vendor_device.keys()][0]
            module = importlib.import_module(vendor_device[vendor][0])
            cls = getattr(module, vendor_device[vendor][1])
        except:
            logging.warning("Can't find supported device")
            raise SystemExit
        self.device = cls(device=device)

    def _update(self):
        records, control_records = self.device.records()
        sn = self.device.device_id()
        cur = self.db.cursor()
        for r in records:
            cur.execute("SELECT device_id FROM bg_record WHERE device_id = ? AND datetime = ?", 
                    (sn, r['date']))
            if cur.fetchone() is None:
                cur.execute("""
                    INSERT INTO bg_record (device_id, datetime, bg, flag, comment, units)
                    VALUES (?, ?, ?, ?, ?, ?)""", (sn, r['date'], r['bg'], r['flag'], 
                    r['comment'], r['units']))
        self.db.commit()

    def _get_graph_data(self):
        cur = self.db.cursor()
        cur.execute("SELECT datetime, bg FROM bg_record ORDER BY datetime")
        return [(parser.parse(x[0]),x[1]) for x in cur.fetchall()]

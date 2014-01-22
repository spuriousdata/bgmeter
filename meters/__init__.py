import os
import sqlite3
import logging
import importlib

from serial.tools import list_ports

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
                CREATE TABLE devices (
                    id text,
                    name text,
                    patient_name text
                )
            """)
            cur.execute("""
                CREATE TABLE bg_record (
                    device_id text,
                    datetime text,
                    flag text,
                    commment text,
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
        device, vendor = [(x[0],x[1]) for x in ports if x[1] in vendor_device.keys()][0]
        try:
            module = importlib.import_module(vendor_device[vendor][0])
            cls = getattr(module, vendor_device[vendor][1])
        except:
            logging.warning("Can't find supported device")
            logging.debug('\n'.join(repr([x for x in ports])))
            raise
        self.device = cls(device=device)

#!/usr/bin/env python3
import argparse
import time
import signal
import sys

from adafruit_blinka.agnostic import board_id

from ui import Ui

parser = argparse.ArgumentParser()
parser.add_argument('--delay', type=float, default=2.0, help='Delay, in seconds, between readings')

args = parser.parse_args()

def clean_exit(signum, frame):
    sys.exit(0)

ui = Ui()
ui.start_drawing()
signal.signal(signal.SIGTERM, clean_exit)

print("Knight Nurse on {}".format(board_id))
try:
    while True:
        time.sleep(args.delay)
except KeyboardInterrupt:
    pass
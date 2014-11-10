import argparse
import os
import glob
import time
import sys


os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
out_file = base_dir + '28-000004986b1c/w1_slave'
in_file = base_dir + '28-000004988572/w1_slave'


def read_temp_raw(file):
    f = open(file, 'r')
    lines = f.readlines()
    f.close()
    return lines


def read_temp(thermometer):

    if thermometer in ("internal", "INTERNAL", "IN", "in"):
        filee = in_file
    elif thermometer in ("external", "EXTERNAL", "OUT", "out"):
	filee = out_file
    else:
	    raise ValueError("Thermometer missing [out|in]")

    lines = read_temp_raw(filee)
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw(filee)
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return float(temp_c)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Read temperatures')
    parser.add_argument('thermometer', metavar='t', type=str,
        help='The thermometer to read from, possible values: in|out')
    args = parser.parse_args()

    print(float(read_temp(args.thermometer)[0]))
    exit(0)

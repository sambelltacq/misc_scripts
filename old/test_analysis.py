#!/usr/bin/env python3

import argparse
import os
import acq400_hapi
import user_apps.special.run_AquadB_movement as AM
import user_apps.analysis.host_demux as HD
from prettytable import PrettyTable as PT
import numpy as np
import sys



"""
    example cmd
    ./test_analysis.py --max_gap=10000 --pses=0:-1:10 --plot=1 --run_test=yes acq2106_355
"""

wrapper_args = None

def main(args):
    global wrapper_args
    wrapper_args = args

    if args.run_test:
        am_args = aqua_move_args()
        blockPrint()
        AM.main(am_args)

    enablePrint()
    hd_args = host_demux_args()
    blockPrint()
    HD.run_main(hd_args)

def aqua_move_args():
    parser = AM.get_parser()
    args = parser.parse_known_args()[0]

    args.force_delete = 1
    args.root = "/home/dt100/DATA"
    args.stim = 'acq2106_274'
    args.dwg = 'dat_files/wiggle.2x32'
    args.verbose = 2
    prYellow("Running AquadB_movement: stim={} dwg={}".format(args.stim,args.dwg))
    return args

def host_demux_args():
    parser = HD.get_parser()
    args = parser.parse_known_args()[0]
    args.src = "/home/dt100/DATA"
    args.pcfg = "PCFG/ansto.pcfg"
    args.pses = "0:-1:1"
    #args.plot = 1
    args.callback = homecoming
    prYellow("Running Host_Demux: pses={} pcfg={}".format(args.pses,args.pcfg))
    return args

def blockPrint():
    sys.stdout = open(os.devnull, 'w')

def enablePrint():
    sys.stdout = sys.__stdout__

def print_numpy_arrays(data):
    keys = data.keys()
    for key in keys:
        print("\033[93m{}\033[00m: {} \033[93m Length: {}\033[00m".format(key,data[key],len(data[key])))

def get_events(data):
    lower = data['DI6'][0]
    arr_len = len(data['DI6'])
    consecutive = False
    events = []
    for i in range(arr_len):
        if data['DI6'][i] > lower:
            if not consecutive:
                consecutive = True
                events.append(i)
        else:
            consecutive = False
    if len(events) == 0:
        prRed("ERROR: NO EVENTS FOUND")
        return []
    prPurple("DI6: {}-{}".format(lower,data['DI6'][events[0]]))
    return events

def build_table(events,data):
    events = demarcate(events)
    t = PT()
    t.add_column('event',events)
    for arr in data:
        if arr != 'DI6':
            new_column = []
            for ev in events:
                if ev == '-' or ev == '~':
                    new_column.append(ev)
                    continue
                value = data[arr][ev]
                value = round(value, 2)
                new_column.append(value)
            t.add_column(arr,new_column)
    t.align = 'r'
    print(t)

def demarcate(events):
    max_gap = wrapper_args.max_gap
    prBlue("demarcation gap = {}".format(max_gap))
    pre = events[0]
    output = []
    for num in events:
        if num - pre > max_gap:
            output.append('-')
        output.append(num)
        pre = num
    if output[1] != '-':
        output.insert(1,'-')
    return output
    
def homecoming(data):
    enablePrint()
    prGreen('homecoming')
    print_numpy_arrays(data)
    events = get_events(data)
    if len(events) == 0:
        return
    build_table(events,data)

def prRed(skk): print("\033[91m{}\033[00m" .format(skk))
def prGreen(skk): print("\033[92m{}\033[00m" .format(skk)) 
def prYellow(skk): print("\033[93m{}\033[00m" .format(skk)) 
def prPurple(skk): print("\033[95m{}\033[00m" .format(skk)) 
def prCyan(skk): print("\033[96m{}\033[00m" .format(skk)) 
def prBlue(skk): print("\033[94m{}\033[00m" .format(skk)) 

def get_parser():
    parser = argparse.ArgumentParser(description='??')
    parser.add_argument('--run_test', default=0, help="max gap between events")
    parser.add_argument('--max_gap', default=10000, type=int, help="max gap between events")
    parser.add_argument('uut', help='uut - for auto configuration data_type, nchan, egu or just a label')
    return parser

if __name__ == '__main__':
    main(get_parser().parse_known_args()[0])
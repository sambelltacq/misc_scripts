#!/usr/bin/env python
"""Starts transient and continuous runs then aborts and checks the UUT returns to IDLE
"""

import argparse
import time

from acq400_hapi import factory, acq400_logger, pv

uut = None
log = None

def run_main(args):
    global uut, log
    level = 20
    if args.debug: level = 0
    log = acq400_logger('abort_thrash', level=level , logfile='abort_thrash.log')
    log.add_new_level('success', 21, color="\033[92m")
    log.add_new_level('failure', 22, color="\033[31m")
    log.info(f"Starting thrash test on {args.uut}")
    uut = factory(args.uut)
    uut.s0.set_abort
    wait_tstate('IDLE') and wait_cstate('IDLE')
    print('Ready\n')

    tests = [
        post_abort_arm,
        post_abort_run,
        prepost_abort_runpre,
        stream_abort_arm,
        stream_abort_run,
        stream_abort_run_30s
    ]

    results = {}

    for test in tests:
        testname = test.__name__
        log.info(f"\nTesting {testname}")
        results[testname] = {'runs': 0, 'fails': 0}

        for loop in range(1, args.loops+1):
            log.info(f"\nLoop {loop}")
            results[testname]['runs'] += 1
            gstate = test()
            abort()
            if not gstate:
                log.error(f"{testname} incorrect state skipping to next")
                results[testname]['fails'] += 1
                break
            if wait_tstate('IDLE') and wait_cstate('IDLE'):
                log.success("Reached IDLE after abort")
            else:
                log.failure(f"Did not reach IDLE after abort")
                results[testname]['fails'] += 1
        log.info(f"Total Runs {results[testname]['runs']} Fails: {results[testname]['fails']}")

    log.info("\nResults")
    for testname in results:
        log.info(f"{testname}\t\t Runs: {results[testname]['runs']} Fails {results[testname]['fails']}")
    

def post_abort_arm():
    """Aborts during post arm"""
    uut.s0.transient = f"PRE=0 POST=100000 SOFT_TRIGGER=1"
    uut.s1.trg = '1,0,1'
    uut.s0.set_arm
    return wait_tstate('ARM')

def post_abort_run():
    """Aborts during post run"""
    uut.s0.transient = f"PRE=0 POST=100000 SOFT_TRIGGER=1"
    uut.s1.trg = '1,1,1'
    uut.s0.set_arm
    return wait_tstate('RUN') #480 is too fast

def prepost_abort_runpre():
    """Aborts during prepost runpre"""
    uut.s0.transient = f"PRE=50000 POST=50000 SOFT_TRIGGER=1"
    uut.s1.trg = '1,1,1'
    uut.s1.event0 = '1,0,1'
    uut.s0.set_arm
    return wait_tstate('RUN_PRE')

def stream_abort_arm():
    """Aborts during steam arm"""
    uut.s1.trg = '1,0,1'
    uut.s0.streamtonowhered
    return wait_cstate('ARM')

def stream_abort_run():
    """Aborts during steam arm"""
    uut.s1.trg = '1,1,1'
    uut.s0.streamtonowhered
    return wait_cstate('RUN')

def stream_abort_run_30s():
    """Aborts during steam arm"""
    uut.s1.trg = '1,1,1'
    uut.s0.streamtonowhered
    notimeout = wait_cstate('RUN')
    time.sleep(30)
    return notimeout

def abort():
    log.info('Aborting')
    uut.s0.set_abort

def wait_tstate(target, timeout=10):
    t0 = time.time()
    tc = 0
    log.info(f"Waiting for {target}")
    while tc < timeout:
        state = pv(uut.s0.TRANS_ACT_STATE)
        tc = int(time.time() - t0)
        log.debug(f"tstate: {state} Target: {target} Wait {tc}")
        if target == state:
            log.info(f"tstate = {state}")
            return True
        time.sleep(1)
    log.info(f"Timeout")
    return False

def wait_cstate(target, timeout=20):
    t0 = time.time()
    tc = 0
    log.info(f"Waiting for {target}")
    while tc < timeout:
        state = pv(uut.s0.CONTINUOUS_STATE)
        tc = int(time.time() - t0)
        log.debug(f"cstate: {state} Target: {target} Wait {tc}")
        if target == state:
            log.info(f"cstate =  {state}")
            return True
        time.sleep(1)
    log.info(f"Timeout")
    return False

def get_parser():
    parser = argparse.ArgumentParser(description='abort thrash loop')
    parser.add_argument('--loops', default=100, type=int, help="total loops per type")
    parser.add_argument('--debug', default=0, type=int, help="enable debug")
    parser.add_argument('uut',help="uut")
    return parser

if __name__ == '__main__':
    run_main(get_parser().parse_args())
#!/usr/bin/env python3

"""
Usage:

    ./usb_handler.py --mount                mounts all
    ./usb_handler.py --unmount 1            unmounts dev 1
    ./usb_handler.py --stream 2             starts stream on dev 1
    ./usb_handler.py --format=vfat 2        format dev 2 to vfat
    ./usb_handler.py --erase 2              erases dev 2    
"""

import argparse
import time
import os
from os.path import join, basename, exists, dirname
from glob import glob
from subprocess import Popen, run, PIPE
import signal

devdir = "/sys/bus/usb/devices/1-1.{}"
mount_path = "/media/disk_{}"
sproc = None

def run_main(args):
    #print(args)
    enable_usb()
    
    devs = [d[-1] for d in glob(devdir.format('?'))]
    for dev in devs:
        devnum = int(dev[-1])
        if args.devnum and devnum not in args.devnum:
            print(f"Skipping {devnum} {devnum not in args.devnum}")
            continue
        
        print(f"Device {devnum}")
        
        if args.enable:
            enabled_device(devnum)
            
        if args.disable:
            disable_device(devnum)
            
        if args.format:
            format_device(devnum, args.format)
            
        if args.mount:
            mount_device(devnum)
            
        if args.unmount:
            unmount_device(devnum)
            
        if args.erase:
            erase_device(devnum)
            
    if args.stream:
        if args.devnum:
            devs = args.devnum
        stream_to_device(devs, args.nbuffers, args.concat, args.filesdir)
        try:
            wait_stream(args.secs)
        except KeyboardInterrupt:
            stop_stream()

def enable_usb():
    if len(os.listdir(dirname(devdir))) > 0: return
    print('Enable usbs')
    os.system("/usr/local/CARE/enable_usb > /dev/null")
    time.sleep(2)
        
def get_device_node(devnum):
    #block if at
    #/sys/bus/usb/devices/1-1.1/1-1.1:1.0/host0/target0:0:0/0:0:0:0/block/sda
    enabled_device(devnum)
    node_dir = []
    while len(node_dir) == 0:
        path = join(devdir.format(devnum), "1-1.*/host*/target*/*:*/block/*")
        node_dir = glob(path)
        time.sleep(1)
    node = basename(node_dir[0])
    node = f"/dev/{node}"
    partitions = glob(f"{node}?")
    return node, partitions

def is_mounted(dev_node):
    return not bool(os.system(f"mount | grep {dev_node} > /dev/null"))
    
def mount_device(devnum):
    enabled_device(devnum)
    node, partitions = get_device_node(devnum)
    dev_node = node if len(partitions) == 0 else partitions[0]
    mount_point = mount_path.format(devnum)
    os.makedirs(mount_point, mode=0o777, exist_ok=True)
    
    if is_mounted(dev_node):
        print(f"[mount] Device {devnum} already mounted")
        return
    cmd = f"mount {dev_node} {mount_point}"
    print(f"cmd {cmd}")
    success = not bool(os.system(cmd))
    if success: print(f"[mount] Device {devnum} mounted to {mount_point}")
    else: print(f"[mount] Device {devnum} error")
    
def unmount_device(devnum):
    mount_point = mount_path.format(devnum)
    if not is_mounted(mount_point): 
        print(f"[unmount] Device {devnum} not mounted")
        return
    print('unmounting')
    success = not bool(os.system(f"sync;sync;umount {mount_point}"))
    if success: print(f"[unmount] Device {devnum} unmounted")
    else: print(f"[unmount] Device {devnum} error")

def enabled_device(devnum):
    configfile = os.path.join(devdir.format(devnum), "bConfigurationValue")
    with open(configfile, 'r+') as fp:
        enabled = bool(fp.read().strip())
        if not enabled:
            fp.write("1")
            print(f"[enable] Device {devnum} enabled")
            time.sleep(0.5)
        else:
            print(f"[enable] Device {devnum} already enabled")

def disable_device(devnum):
    configfile = os.path.join(devdir.format(devnum), "bConfigurationValue")
    with open(configfile, 'r+') as fp:
        enabled = bool(fp.read().strip())
        if enabled:
            fp.write("0")
            print(f"[disable] Device {devnum} disabled")
        else:
            print(f"[enable] Device {devnum} already disabled")

def erase_device(devnum):
    if not exists(mount_path.format(devnum)): return
    cmd = "rm -rf {}".format(join(mount_path.format(devnum), '*'))
    print(f"[erase] Device {devnum} {cmd}")
    os.system(cmd)
    print(os.listdir(mount_path.format(devnum)))
    
def format_device(devnum, ftype):
    unmount_device(devnum)
    cmd_map = {
        'vfat': 'mkdosfs -v',
        #'ext3': 'mkfs.ext3', #very slow do not use
        #'ext4': 'mkfs.ext4',
    }
    node, partitions = get_device_node(devnum)
    dev_node = node if len(partitions) == 0 else partitions[0]
    cmd = "{} {}".format(cmd_map[ftype], dev_node)
    print(f"[format] Device {devnum} starting format")
    os.system(cmd)
    print(f"[format] Device {devnum} formatted to {ftype}")
    
def get_usage(devnum):
    stat = os.statvfs(mount_path.format(devnum))
    _bytes = stat.f_frsize * (stat.f_blocks - stat.f_bfree)
    return round(_bytes / (1024 * 1024), 1)

def run_cmd(cmd):
    proc = run(cmd, shell=True, check=True, stdout=PIPE, stderr=PIPE, text=True)
    return proc.stdout.strip()
    
def stream_to_device(devs, nbuffers, concat, filesdir):
    global sproc
    devnum = devs[0]
    mount_device(devnum)
    erase_device(devnum)
    print('starting stream')
    bufferlen = int(run_cmd('get.site 0 bufferlen'))
    cmd = "acq400_streamd {site} | acq400_stream_disk {maxbuff} {mount}"
    bufferlen = int(bufferlen)
    env = {
        'BUFFERLEN': str(bufferlen),
        'EXTENSION': '.dat',
        'FILESDIR': str(filesdir),
        'CONCATFILES': str(concat),
        'MAXSTREAMBUF': str(nbuffers),
        'LD_LIBRARY_PATH': '/usr/local/lib',
        'PATH': "/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin"
    }
    cmd = cmd.format(site=0, maxbuff=nbuffers, mount=mount_path.format(devnum))
    print(f"Stream cmd: {cmd}")
    sproc = Popen(cmd, shell=True, env=env)
    sproc.dev = devnum
    print(f"[stream] started stream to Device {devnum}")
    
def wait_stream(secs):
    LINE_UP = '\033[1A'
    ERASE_LINE = '\033[2K'
    time_start = time.time()
    print()
    print()
    while sproc:
        sproc.runtime = int(time.time() - time_start)
        samples = run_cmd("get.site 0 CONTINUOUS:SC").split(" ")[-1]
        print(LINE_UP + ERASE_LINE, end="")
        print(f"[STREAM] Dev {sproc.dev} {sproc.runtime}s {samples} samples")
        
        if secs and sproc.runtime > secs:
            print(f"Stream reached time limit")
            
            os.kill(os.getpid(), signal.SIGINT)
            break
        if sproc.poll() is not None:
            print(f"Stream finished")
            os.kill(os.getpid(), signal.SIGINT)
            break
        time.sleep(1)
    

def stop_stream():
    print('Stopping stream')
    sproc.kill()
    run_cmd('get.site 0 CONTINUOUS stop')
    run_cmd('set_abort')
    usage = get_usage(sproc.dev)
    mean = round(usage / sproc.runtime, 1)
    print(f"Mean rate: {mean}MB/s Total {usage}MB")

def list_of_ints(arg):
    return list(map(int, arg.split(',')))

def get_parser():
    parser = argparse.ArgumentParser(description='handle usb')
    
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--mount', action='store_true', help=f"mount device")
    group.add_argument('--unmount', action='store_true', help=f"unmount device")
    
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--enable', action='store_true', help=f"enable device")
    group.add_argument('--disable', action='store_true', help=f"disable device")
    
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--secs', type=int, help=f"stream max runtime")
    group.add_argument('--nbuffers', type=int, default=9999999, help=f"stream max buffers")
    
    parser.add_argument('--format', choices=['vfat'], help=f"format device")
    parser.add_argument('--erase', action='store_true', help=f"erase disk")
    parser.add_argument('--stream', action='store_true', help=f"start stream")
    parser.add_argument('--concat', default=1, type=int, help=f"stream file concat")
    parser.add_argument('--filesdir', default=100, type=int, help=f"files per dir")
    
    parser.add_argument('devnum', nargs='?', type=list_of_ints, help='target devices 1 2 3 empty for all')
    return parser

if __name__ == '__main__':
    run_main(get_parser().parse_args())
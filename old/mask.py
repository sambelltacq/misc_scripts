#!/usr/bin/env python3

import argparse



def main():
    prGreen("start")
    #s = open("wave_2.dat", 'r').read()
    #s = open("wave_1.dat", 'r').read()
    #s = open("LINE1.dat", 'r').read()
    #s = open("line_2.dat", 'r').read()
    s = open("wave_1.dat", 'r').read()
    #1.2400 y top
    #-1.0800 y bottom
    # y is up
    arr = s.split(',')
    largest_y = 0
    smallest_y = 0
    largest_x = 0
    smallest_x = 0

    for i,num in enumerate(arr):
        i += 1
        if i % 2 == 0:
            if float(num) > float(largest_y):
                largest_y = num
            if float(num) < float(smallest_y):
                smallest_y = num
            prYellow(num)
            pass
        else:
            if float(num) > float(largest_x):
                largest_x = num
            if float(num) < float(smallest_x):
                smallest_x = num
            print("\033[96m{}\033[00m" .format(float(num)),end=" ")
        if i >= 99999999:
            break
    print("Y smallest: {} largest: {}".format(smallest_y, largest_y))
    print("X smallest: {} largest: {}".format(smallest_x, largest_x))

def cutter():
    s = open("wave_2.dat", 'r').read()
    s = s.strip()
    arr = s.split(',')
    arr_len = len(arr)

    orphans = {}
    orphan_buffer = []
    continuous = False
    current = 0
    print(arr_len)
    for i in range(arr_len):
        j = i + 1
        if j % 2 == 0:
            if float(arr[i]) > -1.0800:
                prRed("less")
                if not continuous:
                    print('new Orphan')
                    continuous = True
                    orphans[current] = []
                    orphans[current].append(arr[i])

                arr[i] = str(-1.0800)
            else:
                arr[i] = str(arr[i])
    print(orphans)
    exit()
    new_string = ','.join(arr)
    text_file = open("bottom_orphan.txt", "w")
    n = text_file.write(new_string)
    text_file.close()

def mask_cutter(args.file):
    #add cmd line args here and file auto getter



    exit()






    masks = []
    masks.append(open("wave_2.dat", 'r').read())
    for mask in masks:
        mask = mask.strip()
        mask = mask.split(',')
        temp_mask = []
        mask_len = len(mask)
        for i in range(0, mask_len, 2):
            first = mask[i]
            second = mask[i+1]
            temp_mask.append([first, second])
        mask = temp_mask

        up_l = -1.0800
        orphan_arr = {}
        orphan_buffer = []
        continuous = None
        current = 0
        for coord in mask:
            if float(coord[1]) > up_l:
                if continuous == None:
                    print('first orphan value')
                    continuous = True
                orphan_buffer.append(coord)
            else:
                if continuous:
                    break

        print(orphan_buffer)
        orphan_arr = orphan_buffer
        output = ""
        for item in orphan_arr:
            output += item[0]
            output += ','
            output += item[1]
            output += ','
        print(output)
        text_file = open("bottom_orphan1.txt", "w")
        n = text_file.write(output)
        text_file.close()

def get_parser():
    parser = argparse.ArgumentParser(description='??')
    parser.add_argument('--size', default=0, help="how much to cut from middle")
    parser.add_argument('uut', help='uut - for auto configuration data_type, nchan, egu or just a label')
    return parser

if __name__ == '__main__':
    mask_cutter(get_parser().parse_known_args()[0])

def prRed(skk): print("\033[91m{}\033[00m" .format(skk))
def prGreen(skk): print("\033[92m{}\033[00m" .format(skk)) 
def prYellow(skk): print("\033[93m{}\033[00m" .format(skk)) 
def prPurple(skk): print("\033[95m{}\033[00m" .format(skk)) 
def prCyan(skk): print("\033[96m{}\033[00m" .format(skk)) 
def prBlue(skk): print("\033[94m{}\033[00m" .format(skk)) 

#mask_cutter()
#cutter()
#main()
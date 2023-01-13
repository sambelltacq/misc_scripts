#!/usr/bin/env python3

import argparse
from wakeonlan import send_magic_packet
import paramiko
import getpass

"""
check if wol enabled
    sudo ethtool eno1
        Wake-on: g = enabled
get mac address
    cat /sys/class/net/enp5s0/address
sleep cmd
     systemctl start systemd-suspend.service
"""


def main(args):
    actions = {
                '1': {
                    'title' : 'Wake',
                    'action': 'ON',
                },
                '2': {
                    'title' : 'Sleep',
                    'action': 'OFF',
                    'cmd'   : 'sudo systemctl suspend',
                },
                '3': {
                    'title' : 'Shutdown',
                    'action': 'OFF',
                    'cmd'   : 'sudo shutdown',
                },
                '99': {
                    'title' : 'PLACEHOLDER',
                    'action': 'ACTIONTYPE',
                    'cmd'   : 'REMOTECMD',
                },
                'q' : {
                    'title' : 'Quit',
                    'quit' : True,
                },
            }
    hosts = {
                '1' : {
                    'title' : 'Kamino',
                    'hostname' : 'kamino',
                    'mac' : '00:00:00:00:00:00',
                    'user' : 'dt100',
                },
                '2' : {
                    'title' : 'Roger740-TODO',
                    'hostname' : 'roger740',
                    'mac' : '00:00:00:00:00:00',
                    'user' : 'dt100',
                },
                '3' : {
                    'title' : 'OrCAD2-TODO',
                    'hostname' : 'orcad2',
                    'mac' : '00:00:00:00:00:00',
                    'user' : 'dt100',
                },
                '98' : {
                    'title' : 'humla',
                    'hostname' : 'humla',
                    'mac' : '00:00:00:00:00:00',
                    'user' : 'sam'
                },
                '99' : {
                    'title' : 'PLACEHOLDER',
                    'hostname' : 'HOSTNAME',
                    'mac' : '00:00:00:00:00:00',
                    'user' : 'USERNAME'
                },
                'q' : {
                    'title' : 'Quit',
                    'quit' : True,
                },
            }

    question = 'Action :'
    action = actions[ask_question(question,actions)]
    
    question = 'Host :'
    host = hosts[ask_question(question,hosts)]

    if action['action'] == 'ON':
        print('Wake {} at {}'.format(host['title'],host['mac']))
        send_magic_packet(host['mac'])
        return

    if action['action'] == 'OFF':
        hostname = host['hostname']
        user = host['user']
        cmd = action['cmd']
        print('Username: {}'.format(user))
        password = getpass.getpass()
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname, username=user, password=password)
            stdin, stdout, stderr = ssh.exec_command(cmd, timeout=10)
            stdin.write('{}\n'.format(password))
            stdin.flush()
            stdout.channel.close()
            print("Asking {} to {}".format(hostname,action['title']))
        except paramiko.ssh_exception.NoValidConnectionsError as error:
            print("Failed to connect to {} host offline".format(hostname))
        return

def ask_question(question,options):
    while True:
        print("\033[1m{}\033[0m".format(question))
        for option in options:
            print('\r\033[1m[{}]\033[0m: {}'.format(option,options[option]['title']))
        response = input(': ')
        if response == 'q':
            exit('Exiting')
        if response in options:
            print("\033[1m{}\033[0m\n".format(options[response]['title']))
            return response
        print('Invalid Choice')

def get_parser():
    parser = argparse.ArgumentParser(description='<PLACEHOLDER>')
    parser.add_argument('--arg', default='none', type=str, help='cmd line argument')
    return parser

if __name__ == '__main__':
    main(get_parser().parse_args())
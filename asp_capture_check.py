#!/usr/bin/env python3

# To get a logger for the script
import logging

import re
import shlex
import subprocess
import time

from pyats import aetest
from pyats.log.utils import banner

from typing import List

# Genie Imports
from genie.conf import Genie

# To handle errors with connections to devices
from unicon.core import errors

import argparse
from pyats.topology import loader

# Get your logger for your script
global log
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

import anyconnect_test

class MyCommonSetup(aetest.CommonSetup):
    """
    CommonSetup class to prepare for testcases
    Establishes connections to all devices in testbed
    """
    pass

'''
vpn_status_command = '/opt/cisco/anyconnect/bin/vpn status'
vpn_disconnect_command = '/opt/cisco/anyconnect/bin/vpn disconnect'
vpn_connect_command = '/home/admin/pyats/vpn_connect.sh'


def react_output_connect(output_lines: List) -> bool:
    connection_successful = True

    for line in output_lines:
        if line:
            if re.search('error:', line):
                log.error(banner(f'Error has occured: {line}'))
                connection_successful = False

    return connection_successful


def ac_run_command(command: str) -> List:
    log.debug(f'running command: {command}')

    command = shlex.split(command)

    pipe = subprocess.Popen(command, stdout=subprocess.PIPE)
    stdout = pipe.communicate()[0]
    log.debug(f"stdout: {stdout.decode('utf-8')}")

    output_lines = re.split('\\n|\\r+|  >> |VPN> ', stdout.decode('utf-8'))

    log.debug(f"output_lines: {output_lines}")

    return output_lines


def react_output_status(output_lines: List) -> bool:
    connection_successful = True

    for line in output_lines:
        if line:
            if re.search('state: Disconnected', line):
                log.debug(f'Anyconnect is disconnected: {line}')
                connection_successful = False

    return connection_successful
'''

class VerifyASPCapture(anyconnect_test.VerifyAnyconnect):
    """
    VerifyASPCapture Testcase - connect to VPNFW and check VPN connection is not dropped by firewall
    """

class MyCommonCleanup(anyconnect_test.MyCommonCleanup):
    """
    CommonCleanup class to disconnect Anyconnect after the tests
    """



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--testbed', dest='testbed',
                        type=loader.load)

    args, unknown = parser.parse_known_args()

    aetest.main(**vars(args))


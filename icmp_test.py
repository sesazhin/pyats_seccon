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


class MyCommonSetup(aetest.CommonSetup):
    """
    CommonSetup class to prepare for testcases
    Establishes connections to all devices in testbed
    """
    pass


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

    log.info(stdout.decode('utf-8'))    
 
    # output_lines = re.split('\\n|\\r+|  >> |VPN> ', stdout.decode('utf-8'))

    # log.debug(f"output_lines: {output_lines}")

    return stdout.decode('utf-8')


def react_output_status(output_lines: List) -> bool:
    connection_successful = True

    for line in output_lines:
        if line:
            if re.search('state: Disconnected', line):
                log.debug(f'Anyconnect is disconnected: {line}')
                connection_successful = False

    return connection_successful


class VerifyAnyconnect(aetest.Testcase):
    """
    VerifyAnyconnect Testcase - connect to VPNFW with Anyconnect and
    check connection establishes successfully and isn't interrupted afterwards.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.connection_successful = False
        self.vpn_connect_command = 'ping 8.8.8.8 -c 4'
        self.vpn_status_command = '/opt/cisco/anyconnect/bin/vpn status'

    @aetest.test
    def anyconnect_test(self):

        log.info(banner('Trying to establish Anyconnect to VPNFW. Please hold on...'))

        output_lines = ac_run_command(self.vpn_connect_command)
        
        print(output_lines)
        '''
        self.connection_successful = react_output_connect(output_lines)
        if self.connection_successful:
            log.info(banner('VPN connection has been established successfully'))
        else:
            aetest.skip.affix(section=VerifyAnyconnect.anyconnect_stable_test,
                              reason="Skipping 'anyconnect_stable_test' since VPN connection hasn't been established")

            self.failed('Unable to establish VPN connection')
        '''
    '''
    @aetest.test
    def anyconnect_stable_test(self):

        log.info(banner('Going standby for 45 seconds to check Anyconnect state afterwards'))
        time.sleep(2)

        output_lines = ac_run_command(self.vpn_status_command)
        connection_status = react_output_status(output_lines)

        if connection_status:
            log.info(banner('VPN connection is stable'))
        else:
            self.failed('VPN connection has been established but then failed')
    '''

class MyCommonCleanup(aetest.CommonCleanup):
    """
    CommonCleanup class to disconnect Anyconnect after the tests
    """

    pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--testbed', dest='testbed',
                        type=loader.load)

    args, unknown = parser.parse_known_args()

    aetest.main(**vars(args))


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

# icmp_test should only work only after VPN is established and during sleep test ...


class VerifyConnectivity(aetest.Testcase):
    """
    VerifyConnectivity Testcase - check stable connectivity via ICMP to the remote host
    """
    def ping_run_command(self) -> str:
        log.debug(f'running command: {self.command}')

        self.command = shlex.split(self.command)

        pipe = subprocess.Popen(self.command, stdout=subprocess.PIPE)
        stdout = pipe.communicate()[0]
        log.debug(f"stdout: {stdout.decode('utf-8')}")

        log.info(stdout.decode('utf-8'))

        return stdout.decode('utf-8')

    def get_ping_drop_rate(self, ping_output: str) -> None:
        ping_output_list = ping_output.splitlines()
        match_drop_rate = None

        for line in ping_output_list:
            match_drop_rate = re.match(r'.*(?P<rate>\d+)% packet loss.*', line)

            if match_drop_rate:
                drop_rate = match_drop_rate.group('rate')

                if int(drop_rate) < 20:
                    self.passed(f'Ping loss rate {drop_rate}%')
                else:
                    self.failed(f'Ping loss rate {drop_rate}%')
            else:
                continue

        if not match_drop_rate:
            self.failed("Drop string hasn't been found in the ping output.")

    @aetest.setup
    def prepare_for_ping(self, remote_host) -> None:
        self.command = f'ping {remote_host} -c 10'
        log.info(banner(f'Running command: {self.command}'))

    @aetest.test
    def icmp_test(self):
        log.info(banner('Trying to establish Anyconnect to VPNFW. Please hold on...'))

        ping_output = ping_run_command(self.command)
        
        self.get_ping_drop_rate(ping_output)


class MyCommonCleanup(aetest.CommonCleanup):
    """
    CommonCleanup class to cleanup after the tests
    """
    pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--testbed', dest='testbed',
                        type=loader.load)
    parser.add_argument('--host', dest='remote_host')

    args = parser.parse_known_args()[0]

    aetest.main(**vars(args))


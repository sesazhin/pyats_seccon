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
import packet_tracer_test


class MyCommonSetup(packet_tracer_test.MyCommonSetup):
    """
    CommonSetup class to prepare for testcases
    Establishes connections to all devices in testbed
    """
    pass


class VerifyASPCapture(anyconnect_test.VerifyAnyconnect):
    """
    VerifyASPCapture Testcase - connect to VPNFW and check VPN connection is not dropped by firewall
    """

    def get_asp_drop_reason(self, show_capture_output: str) -> str:
        capture_output_list = show_capture_output.splitlines()
        asp_drop_reason = ''

        for line in capture_output_list:
            log.debug(banner(f'line = {line}'))
            match_asp_drop = re.match(r'.*(Drop-reason: )\((.*)\) (.*)', line)

            if match_asp_drop:
                drop_code = match_asp_drop.group(2)
                drop_reason = match_asp_drop.group(3)
                asp_drop_reason = f'Drop code: "{drop_code}". Drop reason: "{drop_reason}".'
                break

            else:
                asp_drop_reason = "Drop string hasn't been found in the capture."

        return asp_drop_reason

    @aetest.setup
    def enable_capture(self):
        self.command = f'capture asp-tcp-o type asp-drop match tcp host 198.18.31.192 eq 443 host 10.207.195.220'
        log.info(banner(f'Running command: {self.command}'))

        self.edgefw = self.parent.parameters['testbed'].devices['EdgeFW']
        command_output = self.edgefw.execute(self.command, log_stdout=True)
        log.info(command_output)

    @aetest.test
    def check_asp_has_to_run(self):
        if self.connection_successful:
            aetest.skip.affix(section=VerifyASPCapture.get_capture_output,
                              reason="Skipping 'get_capture_output' test since VPN connection has been established")

    @aetest.test
    def get_capture_output(self):
        self.command = f'show capture asp-tcp-o packet-number 1'
        log.info(banner(f'Running command: {self.command}'))

        show_capture_output = self.edgefw.execute(self.command, log_stdout=True)
        log.debug(show_capture_output)
        
        asp_drop_reason = self.get_asp_drop_reason(show_capture_output)
        log.info(banner(asp_drop_reason))

    @aetest.cleanup
    def disable_capture(self):
        self.command = f'no capture asp-tcp-o'
        log.info(banner(f'Running command: {self.command}'))

        command_output = self.edgefw.execute(self.command, log_stdout=True)
        log.info(command_output)


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


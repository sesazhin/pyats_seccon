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

    @aetest.setup
    def enable_capture(self):
        self.command = f'capture asp-tcp-o type asp-drop match tcp host 198.18.31.192 eq 443 host 10.207.195.220'
        log.info(banner(f'Running command: {self.command}'))

        edgefw = self.parent.parameters['testbed'].devices['EdgeFW']
        log.info(edgefw)
        packet_tracer_output = edgefw.execute(self.command, log_stdout=True)
        log.info(packet_tracer_output)

    @aetest.cleanup
    def disable_capture(self):
        self.command = f'no capture asp-tcp-o'
        log.info(banner(f'Running command: {self.command}'))

        edgefw = self.parent.parameters['testbed'].devices['EdgeFW']
        log.info(edgefw)
        packet_tracer_output = edgefw.execute(self.command, log_stdout=True)
        log.info(packet_tracer_output)
        

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


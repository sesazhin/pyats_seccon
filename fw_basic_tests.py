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
from typing import Tuple

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

from fw_routes_test import MyCommonSetup

class ServicePolicyCommonSetup(MyCommonSetup):
    """
    CommonSetup class to prepare for testcases
    Establishes connections to all devices in testbed
    """
    pass


class VerifyFWBasics(aetest.Testcase):
    """
    VerifyServicePolicy Testcase - run basic checks on firewalls
    """

    def check_anyconnect_load_output(self, run_command):
        anyconnect_load = '0.0'
        try:
            anyconnect_load = self.output[run_command]['summary']['VPN Session']['device_load']
        except KeyError:
            self.failed(
                banner('Unable to get Anyconnect load from output. Please check it conforms to the required format.'))

        if float(anyconnect_load) > 70.0:
            self.failed(banner(f'Number of Anyconnect sessions on the device approaching the device limit. '
                        f'Anyconnect load: {anyconnect_load}'))
        else:
            self.passed(banner('Number of Anyconnect sessions on the device is far below the device limit.'))

    def check_interface_summary_output(self, run_command):
        interfaces = {}
        try:
            interfaces = self.output[run_command]['interfaces']
        except KeyError:
            self.failed(
                banner('Unable to parse "show interface summary" output. '
                       'Please check it conforms to the required format.'))

        for interface in interfaces:
            try:
                interface_state = bool(interfaces[interface]['interface_state'])
                interface_link_status = bool(interfaces[interface]['link_status'])
                interface_line_protocol = bool(interfaces[interface]['line_protocol'])
                if not (interface_state and interface_link_status and interface_line_protocol):
                    self.failed(banner(f'Interface {interface} state is not up.'))
            except KeyError:
                self.failed(
                    banner(f'Unable to parse details of {interface} in "show interface summary" output. '
                           'Please check it conforms to the required format.'))

        self.passed(banner(f'All non-admin down interfaces on '
                           f'{self.parent.parameters["device_name"]} are in up state'))

    def check_asp_drop_output(self, run_command):
        expected_drop_reasons = ['sp-security-failed', 'rpf-violated', 'acl-drop', 'tcp-not-syn', 'tcp-3whs-failed',
                                 'tcp-rstfin-ooo', 'l2_acl', 'tcp-not-syn', 'last_clearing']

        asp_drops = {}
        non_expected_asp_drops = {}
        try:
            asp_drops = self.output[run_command]['frame_drop']
        except KeyError:
            self.failed(
                banner('Unable to parse "show asp drop" output. '
                       'Please check it conforms to the required format.'))

        for asp_drop_reason in asp_drops:
            if asp_drop_reason not in expected_drop_reasons:
                non_expected_asp_drops.update({asp_drop_reason: asp_drops[asp_drop_reason]})

        if len(non_expected_asp_drops) > 0:
            log.error(banner(f'The following non-expected asp drops has been found:'))
            log.error(banner(f'Drop reason: Drop count'))
            for asp_drop_reason in non_expected_asp_drops.keys():
                log.error(banner(f'"{asp_drop_reason}": {non_expected_asp_drops[asp_drop_reason]}'))
            self.failed(banner(f'Please double-check these asp drops on '
                  f'"{self.parent.parameters["device_name"]}" are not critical and expected.'))
        else:
            self.passed(banner(f'All asp drops on "{self.parent.parameters["device_name"]}" are expected'))

    @aetest.setup
    def prepare_for_basic_checks(self) -> None:
        self.output = {}
        self.command = [f'show vpn-sessiondb summary', f'show interface summary', f'show asp drop']
        self.device_to_connect = self.parent.parameters['dev']
        log.debug(self.device_to_connect)

        for run_command in self.command:
            self.output[run_command] = self.device_to_connect.parse(run_command)
            log.debug(f'command = {run_command}')

        log.debug(self.output)

    @aetest.test
    def check_anyconnect_load(self) -> None:
        run_command = "show vpn-sessiondb summary"
        self.check_anyconnect_load_output(run_command)

    @aetest.test
    def check_interface_summary(self) -> None:
        run_command = "show interface summary"
        self.check_interface_summary_output(run_command)

    @aetest.test
    def check_asp_drop(self) -> None:
        run_command = "show asp drop"
        self.check_asp_drop_output(run_command)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--testbed', dest='testbed',
                        type=loader.load)
    parser.add_argument('--device', dest='device_name')

    args = parser.parse_known_args()[0]

    aetest.main(**vars(args))


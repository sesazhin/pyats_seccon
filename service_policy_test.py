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


# golden_routes = {'198.18.31.0/24': {'next_hop': '198.18.33.194', 'outgoing_interface': 'vpn'}}



class VerifyServicePolicy(aetest.Testcase):
    """
    VerifyServicePolicy Testcase - check no drops in service-policy
    """

    def check_anyconnect_load_output(self, run_command):
        anyconnect_load = '0.0'
        try:
            anyconnect_load = self.output[run_command]['summary']['VPN Session']['device_load']
        except KeyError:
            self.failed(
                banner('Unable to get Anyconnect load from output. Please check it conforms to the required format.'))

            if float(anyconnect_load) > 70.0:
                self.failed(
                    f'Number of Anyconnect sessions on the device approaching the device limit. '
                    f'Anyconnect load: {anyconnect_load}')
            else:
                self.passed('Number of Anyconnect sessions on the device is far below the device limit.')

    def check_interface_summary_output(self, run_command):
        pass

    def check_asp_drop_output(self, run_command):
        pass

    @aetest.setup
    def prepare_for_basic_checks(self) -> None:
        self.command = [f'show vpn-sessiondb summary', f'show interface summary', f'show asp drop']
        self.device_to_connect = self.parent.parameters['dev']
        log.debug(self.device_to_connect)

        for run_command in self.command:
            self.output[run_command] = self.device_to_connect.parse(run_command)
            log.info(f'command = {run_command}')

        log.info(output)

    @aetest.test
    def check_anyconnect_load(self) -> None:
        run_command = "show vpn-sessiondb summary"
        check_anyconnect_load_output(self, run_command)

    @aetest.test
    def check_interface_summary(self) -> None:
        run_command = "show interface summary"
        check_interface_summary_output(self, run_command)

    @aetest.test
    def check_asp_drop(self) -> None:
        run_command = "show asp drop"
        ccheck_asp_drop_output(self, run_command)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--testbed', dest='testbed',
                        type=loader.load)
    parser.add_argument('--device', dest='device_name')

    args = parser.parse_known_args()[0]

    aetest.main(**vars(args))


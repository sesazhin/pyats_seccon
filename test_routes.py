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

import xml.etree.ElementTree


class MyCommonSetup(aetest.CommonSetup):
    """
    CommonSetup class to prepare for testcases
    Establishes connections to all devices in testbed
    """

    @aetest.subsection
    def establish_connections(self, testbed):
        """
        Establishes connections to all devices in testbed
        :param testbed:
        :return:
        """

        genie_testbed = Genie.init(testbed)
        self.parent.parameters['testbed'] = genie_testbed
        device_list = []
        for device in genie_testbed.devices.values():
            log.info(banner(
                f"Connect to device '{device.name}'"))
            try:
                device.connect(log_stdout=False)
            except errors.ConnectionError:
                self.failed(banner(f"Failed to establish "
                                   f"connection to '{device.name}'"))
            device_list.append(device)
        # Pass list of devices to testcases
        self.parent.parameters.update(dev=device_list)


golden_routes = {'198.18.31.0/24': {next_hop: '198.18.33.194', outgoing_interface: 'vpn'}}

class VerifyPacketTracer(aetest.Testcase):
    """
    VerifyPacketTracer Testcase - connect to VPNFW and check whether simulated connection flows fine via firewall
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.command = f'show route'
        log.info(banner(f'Running command: {self.command}'))

    @aetest.test
    def check_routes(self):

        edgefw = self.parent.parameters['testbed'].devices['EdgeFW']
        log.info(edgefw)

        output = edgefw.parse('show route')
        rib = output['vrf']['default']['address_family']['ipv4']['routes']

        for route in golden_routes.keys():
            if route not in rib:
                self.failed(f'{route} is not found')
            else:
                output_next_hop = rib[route]['next_hop']['next_hop_list'][1]['next_hop']
                output_outgoing_interface = rib[route]['next_hop']['next_hop_list'][1]['outgoing_interface_name']

                if golden_routes[route]['next_hop'] == output_next_hop and golden_routes[route][
                    'outgoing_interface'] == output_outgoing_interface:
                    log.info(banner('all good'))
                else:
                    self.failed(banner('failed'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--testbed', dest='testbed',
                        type=loader.load)

    args = parser.parse_known_args()[0]

    aetest.main(**vars(args))


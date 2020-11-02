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
    def establish_connections(self, testbed, device_name):
        """
        Establishes connection to the required device
        :param testbed:
        :return:
        """
        device_to_connect = None

        genie_testbed = Genie.init(testbed)
        self.parent.parameters['testbed'] = genie_testbed

        try:
            log.info(f'device_name = {device_name}')
            device_to_connect = self.parent.parameters['testbed'].devices[device_name]
            self.parent.parameters['dev'] = device_to_connect
        except KeyError:
            self.failed(banner(
                f'Unable to find specified device: {device_name} in the topology.'))


        '''
        devices = genie_testbed.devices.values()
        
        for device in devices:
            if device.name == device_name:
                device_to_connect = device
                self.parent.parameters['device'] = device
        
        if not device_to_connect:
            self.failed(banner(f'Unable to find specified device: {device_name} in the topology. Using default device instead.'))
        '''

        log.info(banner(f'Connect to device "{device_name}"'))
        try:
            device_to_connect.connect(log_stdout=False)
        except errors.ConnectionError:
            self.failed(banner(f"Failed to establish "
                               f"connection to '{device_to_connect.name}'"))

        '''
        if device not in genie_testbed.devices.values():
            log.error(f'Unable to find specified device: {device} in the topology. Using default device instead.')
            self.parent.parameters['device'] = 'EdgeFW'
        else:
            self.parent.parameters['device'] = device
        '''

golden_routes = {'198.18.31.0/24': {'next_hop': '198.18.33.194', 'outgoing_interface': 'vpn'}}

class VerifyGoldenRoutes(aetest.Testcase):
    """
    VerifyPacketTracer Testcase - connect to VPNFW and check whether simulated connection flows fine via firewall
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.command = f'show route'
        log.info(banner(f'Running command: {self.command}'))

    @aetest.test
    def check_routes(self):
        rib = {}
        # edgefw = self.parent.parameters['testbed'].devices[device_name']

        device_to_connect = self.parent.parameters['dev']
        log.info(device_to_connect)

        output = device_to_connect.parse(self.command)
        try:
            rib = output['vrf']['default']['address_family']['ipv4']['routes']
        except KeyError:
            self.failed(banner('Unable to get routes from output. Please check it conforms to the required format.'))

        for route in golden_routes.keys():
            if route not in rib:
                self.failed(f'{route} is not found')
            else:
                output_next_hop = rib[route]['next_hop']['next_hop_list'][1]['next_hop']
                output_outgoing_interface = rib[route]['next_hop']['next_hop_list'][1]['outgoing_interface_name']

                if golden_routes[route]['next_hop'] == output_next_hop and golden_routes[route][
                    'outgoing_interface'] == output_outgoing_interface:
                    log.info(banner(f'Routing information for {route} on "{device_to_connect.name}" is correct.'))
                else:
                    self.failed(banner('Routing information for {route} on "{device_to_connect.name}" has been changed.}'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--testbed', dest='testbed',
                        type=loader.load)
    parser.add_argument('--device', dest='device_name')

    args = parser.parse_known_args()[0]

    aetest.main(**vars(args))


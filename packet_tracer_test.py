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


'''
parameters = {
    'interface': 'inet',
    'source_ip': '10.207.195.220',
    'destination_ip': '198.18.31.192'
}
'''


class VerifyPacketTracer(aetest.Testcase):
    """
    VerifyLogging Testcase - connect to VPNFW with Anyconnect and
    check connection establishes successfully and isn't interrupted afterwards.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.command = f'packet-tracer input {self.parent.parameters["interface"]} {self.parent.parameters["protocol"]} {self.parent.parameters["source_ip"]} 6500 {self.parent.parameters["destination_ip"]} 443 xml'
        log.info(banner(f'Running packet-tracer command: {self.command}'))

    def get_action_allow(self, rootxml) -> bool:
        result_action = rootxml.find('./result/action')

        if result_action.text is not None:
            if result_action.text.lower() == 'allow':
                return True
            else:
                return False
        else:
            raise ValueError('Packet-tracer output lacks result action')

    def get_drop_phase(self, rootxml) -> Tuple:
        phase_id_text = ''
        phase_type_text = ''
        phase_subtype_text = ''
        phase_config_text = ''
        phase_extra_text = ''
        for phase in rootxml:
            log.debug(phase.tag)

            phase_result = phase.find('./result')
            if phase_result.text is not None:
                log.debug(phase_result.text)
                if phase_result.text.lower() == 'drop':

                    phase_id = phase.find('./id')
                    if phase_id.text is not None:
                        phase_id_text = phase_id.text.replace('\n', '')

                    phase_type = phase.find('./type')
                    if phase_type.text is not None:
                        phase_type_text = phase_type.text.replace('\n', '')

                    phase_subtype = phase.find('./subtype')
                    if phase_subtype.text is not None:
                        phase_subtype_text = phase_subtype.text.replace('\n', '')

                    phase_config = phase.find('./config')
                    if phase_config.text is not None:
                        phase_config_text = phase_config.text.replace('\n', '')

                    phase_extra = phase.find('./extra')
                    if phase_extra.text is not None:
                        phase_extra_text = phase_extra.text.replace('\n', '')

                    break

        return phase_id_text, phase_type_text, phase_subtype_text, phase_config_text, phase_extra_text

    def get_drop_details(self, drop_details) -> str:
        print_drop_notification = 'Connection has been dropped:\n'
        print_stage_id = f'Drop on stage: #{drop_details[0]}.'
        print_stage_type = f' Drop stage: "{drop_details[1]}".'

        if drop_details[2]:
            print_stage_subtype = f' Drop substage: "{drop_details[2]}".'
        else:
            print_stage_subtype = ''

        if drop_details[3]:
            print_stage_config = f' FW configuration: "{drop_details[3]}".'
        else:
            print_stage_config = ''

        if drop_details[4]:
            print_stage_extra = f' Additional information: "{drop_details[4]}".'
        else:
            print_stage_extra = ''

        print_drop_details = print_drop_notification + print_stage_id + print_stage_type + \
                             print_stage_subtype + print_stage_config + print_stage_extra

        return print_drop_details

    @aetest.test
    def packet_tracer_test(self):
        # devices = self.parent.parameters['dev']['EdgeFW']
        edgefw = self.parent.parameters['testbed'].devices['EdgeFW']
        log.debug(edgefw)
        packet_tracer_output = edgefw.execute(self.command, log_stdout=True)
        log.debug(packet_tracer_output)

        try:
            packet_tracer_output = f'<packet-tracer>\n{packet_tracer_output}\n</packet-tracer>'
            root = xml.etree.ElementTree.fromstring(packet_tracer_output)
            if not self.get_action_allow(root):
                drop_details = self.get_drop_phase(root)
                self.failed(banner(self.get_drop_details(drop_details)))

            else:
                log.info(banner('Connection has been allowed.'))

        except ValueError as e:
            self.failed(banner(e))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--testbed', dest='testbed',
                        type=loader.load)
    parser.add_argument('--iface', dest='interface')
    parser.add_argument('--sip', dest='source_ip')
    parser.add_argument('--dip', dest='destination_ip')
    parser.add_argument('--proto', dest='protocol')

    args = parser.parse_known_args()[0]

    aetest.main(**vars(args))


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

from icmp_test import VerifyConnectivity

class MyCommonSetup(aetest.CommonSetup):
    """
    CommonSetup class to prepare for testcases
    Establishes connections to all devices in testbed
    """
    @aetest.subsection
    def prepare_test(self):
        if not self.parent.parameters.get('remote_host'):
            default_host = '172.16.53.120'
            self.parent.parameters.update(remote_host=default_host)
            log.debug(banner(f'host is not specified, using default: {default_host}'))
        else:
            log.debug(f'host is specified, using provided: {self.parent.parameters.get("remote_host")}')


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


class VerifyAnyconnect(aetest.Testcase):
    """
    VerifyAnyconnect Testcase - connect to VPNFW with Anyconnect and
    check connection establishes successfully and isn't interrupted afterwards.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.connection_successful = False
        self.vpn_connect_command = '/home/admin/pyats/vpn_connect.sh'
        self.vpn_status_command = '/opt/cisco/anyconnect/bin/vpn status'

    @aetest.test
    def anyconnect_test(self):

        log.info(banner('Trying to establish Anyconnect to VPNFW. Please hold on...'))

        output_lines = ac_run_command(self.vpn_connect_command)
        self.connection_successful = react_output_connect(output_lines)
        if self.connection_successful:
            log.info(banner('VPN connection has been established successfully'))
        else:
            aetest.skip.affix(section=VerifyAnyconnect.anyconnect_stable_test,
                              reason="Skipping 'anyconnect_stable_test' since VPN connection hasn't been established")
            aetest.skip.affix(section=VerifyConnectivity.prepare_for_ping,
                              reason="Skipping 'prepare_for_ping' since VPN connection hasn't been established")
            aetest.skip.affix(section=VerifyConnectivity.icmp_test,
                              reason="Skipping 'icmp_test' since VPN connection hasn't been established")

            self.failed('Unable to establish VPN connection')

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


class AnyconnectVerifyConnectivity(VerifyConnectivity):
    pass


vpn_status_command = '/opt/cisco/anyconnect/bin/vpn status'


@aetest.processors.noreport
def skip_if_vpn():
    output_lines = ac_run_command(self.vpn_status_command)
    connection_status = react_output_status(output_lines)

    return connection_status


class VerifyAnyconnectStability(aetest.Testcase):
    @aetest.processors.pre(skip_if_vpn)
    @aetest.test
    def anyconnect_stable_test(self):
        vpn_status_command = '/opt/cisco/anyconnect/bin/vpn status'

        log.info(banner('Going standby for 30 seconds to check Anyconnect state afterwards'))
        time.sleep(2)

        output_lines = ac_run_command(vpn_status_command)
        connection_status = react_output_status(output_lines)

        if connection_status:
            log.info(banner('VPN connection is stable'))
        else:
            self.failed('VPN connection has been established but then failed')


@aetest.processors.noreport
def skip_if_vpn_not_established():
    log.info(f'self.parent.parameters[connection_status]: {self.parent.parameters[connection_status]}')

class MyCommonCleanup(aetest.CommonCleanup):
    """
    CommonCleanup class to disconnect Anyconnect after the tests
    """

    @aetest.subsection
    def ac_disconnect(self):
        vpn_status_command = '/opt/cisco/anyconnect/bin/vpn status'
        vpn_disconnect_command = '/opt/cisco/anyconnect/bin/vpn disconnect'
        output_lines = ac_run_command(vpn_status_command)
        connection_status = react_output_status(output_lines)

        if connection_status:
            output_lines = ac_run_command(vpn_disconnect_command)
            connection_status = react_output_status(output_lines)

            if connection_status:
                log.error(banner('Unable to disconnect VPN connection'))
            else:
                log.info(banner('VPN connection has been disconnected successfully'))

    @aetest.subsection
    def wait_before_send_email(self):
        log.debug(banner('Waiting for 2 seconds to allow Anyconnect to disconnect to send email after'))
        time.sleep(2)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--testbed', dest='testbed',
                        type=loader.load)
    parser.add_argument('--host', dest='remote_host')

    args, unknown = parser.parse_known_args()

    aetest.main(**vars(args))


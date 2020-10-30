#!/usr/bin/env python3

# To get a logger for the script
import logging

from pyats import aetest
from pyats.log.utils import banner

# Genie Imports
from genie.conf import Genie

# To handle errors with connections to devices
from unicon.core import errors

import argparse
from pyats.topology import loader

# Get your logger for your script
global log
log = logging.getLogger(__name__)
log.level = logging.ERROR


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
                self.failed(f"Failed to establish "
                            f"connection to '{device.name}'")
            device_list.append(device)
        # Pass list of devices to testcases
        self.parent.parameters.update(dev=device_list)


class VerifyAnyconnect(aetest.Testcase):
    """
    VerifyLogging Testcase - connect to VPNFW with Anyconnect and
    check connection establishes successfully and isn't interrupted afterwards.
    """

    @aetest.setup
    def setup(self):
        pass

    def react_output_connect(self, output_lines: str) -> bool:
        connection_successful = True

        for line in output_lines:
            if line:
                if re.search('error:', line):
                    log.error(f'Error has occured: {line}')
                    connection_successful = False
    
        return connection_successful

    def react_output_status(self, output_lines: str) -> bool:
        connection_successful = True

        for line in output_lines:
            if line:
                if re.search('state: Disconnected', line):
                    log.debug(f'Anyconnect is disconnected: {line}')
                    connection_successful = False

        return connection_successful

    def ac_run_command(self, command: str) -> str:
        log.info(f'running command: {command}')

        command = shlex.split(command)

        pipe = subprocess.Popen(command, stdout=subprocess.PIPE)
        stdout = pipe.communicate()[0]
        log.debug(f"stdout: {stdout.decode('utf-8')}")

        output_lines = re.split('\\n|\\r+|  >> |VPN> ', stdout.decode('utf-8'))

        log.debug(f"output_lines: {output_lines}")

        return output_lines


    @aetest.test
    def anyconnect_test(self):
        vpn_connect_command = '/home/admin/pyats/vpn_connect.sh'
        vpn_status_command = '/opt/cisco/anyconnect/bin/vpn status'
        vpn_disconnect_command = '/opt/cisco/anyconnect/bin/vpn disconnect'

        output_lines = self.ac_run_command(vpn_connect_command)
        connection_successful = self.react_output_connect(output_lines)
        if connection_successful:
            log.info('VPN connection has been established successfully')
        else:
            self.failed('Unable to establish VPN connection')
            log.error('Unable to establish VPN connection')

        if connection_successful:
            time.sleep(45)
            output_lines = self.ac_run_command(vpn_status_command)
            connection_status = self.react_output_status(output_lines)

            if connection_status:
                log.info('VPN connection is stable')

                output_lines = self.ac_run_command(vpn_disconnect_command)
                connection_status = self.react_output_status(output_lines)

                if connection_status:
                    log.error('Unable to disconnect VPN connection')
                else:
                    log.info('VPN connection has been disconnected succesfully')
            else:
                self.failed('VPN connection has been established but then failed')
                log.error('VPN connection has been established but then failed')


class VerifyLogging(aetest.Testcase):
    """
    VerifyLogging Testcase - collect show logging information from devices
    Verify that all devices do not have 'ERROR|WARN' messages in logs
    """

    @aetest.setup
    def setup(self):
        pass

    @aetest.test
    def error_logs(self):
        any_device = self.parent.parameters['dev'][0]
        any_device.log_user(enable=True)
        output = any_device.execute('show logging | i ERROR|WARN')

        if len(output) > 0:
            self.failed('Found ERROR in log, review logs first')
        else:
            pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--testbed', dest='testbed',
                        type=loader.load)

    args, unknown = parser.parse_known_args()

    aetest.main(**vars(args))


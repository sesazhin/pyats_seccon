#!/usr/bin/env python3

# To get a logger for the script
import logging

# Import of PyATS library
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
log.setLevel(logging.INFO)


class common_setup(aetest.CommonSetup):
    @aetest.subsection
    def establish_connections(self, testbed):
        # Load testbed file which is passed as command-line argument
        genie_testbed = Genie.init(testbed)
        # Load all devices from testbed file and try to connect to them
        device = genie_testbed.devices['vpnfw']
        log.info(banner(f"Connect to device '{device.name}'"))
        try:
            device.connect(log_stdout=False)
        except errors.ConnectionError:
            self.failed(f"Failed to establish "
                        f"connection to '{device.name}'")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--testbed', dest='testbed',
                        type=loader.load)

    args = parser.parse_known_args()[0]

    aetest.main(**vars(args))


import os
from ats.easypy import run


def main():
    # Find the location of the script in relation to the job file
    packet_tracer_tests = os.path.join('packet_tracer_test.py')

    # Execute the testscript
    run(testscript = packet_tracer_tests, testbed = 'testbed.yaml', interface = 'inet', protocol = 'udp', source_ip = '10.207.195.220', destination_ip = '10.207.195.231')
    run(testscript = packet_tracer_tests, testbed = 'testbed.yaml', interface = 'inet', protocol = 'tcp', source_ip = '10.207.195.220', destination_ip = '10.207.195.231')


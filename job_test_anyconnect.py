import os
from ats.easypy import run


def main(runtime):
    runtime.mailbot.mailto = ['sesazhin@cisco.com']
    runtime.mailbot.subject = 'Anyconnect Test: PyATS SecCon'
    runtime.mailbot.from_addrs = 'sesazhin@cisco.com'

    # Find the location of the script in relation to the job file
    anyconnect_tests = 'anyconnect_test.py'

    # Execute the testscript
    run(testscript = anyconnect_tests, testbed = 'testbed.yaml', remote_host = '172.16.53.120', wait_time = 2)


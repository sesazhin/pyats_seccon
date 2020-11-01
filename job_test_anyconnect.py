import os
from ats.easypy import run


def main(runtime):
    mail_list = ['sesazhin@cisco.com']
    runtime.mailbot.mailto = mail_list
    
    # Find the location of the script in relation to the job file
    anyconnect_tests = os.path.join('anyconnect_test.py')

    # Execute the testscript
    run(testscript = anyconnect_tests, testbed = 'testbed.yaml')


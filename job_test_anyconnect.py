import os
from ats.easypy import run


def main():
    # Find the location of the script in relation to the job file
    anyconnect_tests = os.path.join('./anyconnect_test.py')

    # Execute the testscript
    run(testscript=anyconnect_tests)


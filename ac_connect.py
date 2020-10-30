#!/usr/bin/env python3

import logging
import logging.handlers
import os
from pprint import pprint
import re
import shlex
import subprocess
import sys

def init_logging() -> None:
    global logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    log_formatter_console = logging.Formatter('%(filename)s: %(message)s')
    format = '%(asctime)s %(levelname)s %(filename)s(%(lineno)d) %(message)s'
    log_formatter_file = logging.Formatter(format)

    console = logging.StreamHandler()
    console.setFormatter(log_formatter_console)
    console.setLevel(logging.INFO)

    file_handler = \
        logging.handlers.RotatingFileHandler('/var/tmp/pyats_lab.log',
                                             maxBytes=(1048576 * 10),
                                             backupCount=10,
                                             encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(log_formatter_file)

    logger.addHandler(console)
    logger.addHandler(file_handler)


def main() -> None:
    devnull = open(os.devnull, 'w')

    vpn_server_hostname = 'vpn.sec.lab'
    logger.info('Connecting to VPN')
    command_run = '/home/admin/pyats/vpn_connect.sh'
    logger.info(f'running command: {command_run}')

    pipe = subprocess.Popen(command_run, stdout=subprocess.PIPE)
    stdout = pipe.communicate()[0]
    pprint(stdout.decode('utf-8'))   
    #stdout_str = stdout.decode('utf-8')
    output_lines = re.split('\\n|\\r+|  >> |VPN> ', stdout.decode('utf-8'))

    for line in output_lines:
        if line:
            if re.search('error:',line):
                logger.error(f'Error has occured: {line}')


if __name__ == '__main__':
    init_logging()
    main()
    


#!/usr/bin/env python3.7

import logging
import logging.handlers
import os
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


    code = subprocess.call(command_run, shell=True, stdin=devnull, stdout=devnull , stderr=devnull)
    
    # code = subprocess.call(command_run, shell=True, stderr=devnull)

    logger.info(code)


if __name__ == '__main__':
    init_logging()
    main()
    


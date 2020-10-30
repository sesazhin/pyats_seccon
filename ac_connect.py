#!/usr/bin/env python3

import logging
import logging.handlers
import os
from pprint import pprint
import re
import shlex
import subprocess
import sys
import time

def init_logging() -> None:
    global logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    log_formatter_console = logging.Formatter('%(levelname)s %(filename)s: %(message)s (%(lineno)d)')
    format = '%(asctime)s %(levelname)s %(filename)s (%(lineno)d %(message)s'
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


def react_output_connect(output_lines: str) -> None:
    connection_successful = True

    for line in output_lines:
        if line:
            if re.search('error:', line):
                logger.error(f'Error has occured: {line}')
                connection_successful = False
    
    return connection_successful

def react_output_status(output_lines: str) -> bool:
    connection_successful = True

    for line in output_lines:
        if line:
            if re.search('state: Disconnected', line):
                logger.debug(f'Anyconnect is disconnected: {line}')
                connection_successful = False

    return connection_successful


def ac_run_command(command: str) -> None:
    logger.info(f'running command: {command}')
    
    command = shlex.split(command)

    pipe = subprocess.Popen(command, stdout=subprocess.PIPE)
    stdout = pipe.communicate()[0]
    logger.debug(f"stdout: {stdout.decode('utf-8')}")
    
    output_lines = re.split('\\n|\\r+|  >> |VPN> ', stdout.decode('utf-8'))

    logger.debug(f"output_lines: {output_lines}")
    
    return output_lines
    

def main() -> None:
    devnull = open(os.devnull, 'w')

    # vpn_server_hostname = 'vpn.sec.lab'
    vpn_connect_command = '/home/admin/pyats/vpn_connect.sh'
    vpn_status_command = '/opt/cisco/anyconnect/bin/vpn status'
    vpn_disconnect_command = '/opt/cisco/anyconnect/bin/vpn disconnect'
  
    output_lines = ac_run_command(vpn_connect_command)
    connection_successful = react_output_connect(output_lines)
    if connection_successful:
        logger.info('VPN connection has been established successfully')
    else:
        logger.error('Unable to establish VPN connection')

    if connection_successful:
        time.sleep(45)
        output_lines = ac_run_command(vpn_status_command)
        connection_status = react_output_status(output_lines)

        if connection_status:
            logger.info('VPN connection is stable')

            output_lines = ac_run_command(vpn_disconnect_command)
            connection_status = react_output_status(output_lines)
            
            if connection_status:
                logger.error('Unable to disconnect VPN connection')
            else:
                logger.info('VPN connection has been disconnected succesfully')


        else:
            logger.error('VPN connection has been established but then failed')
    
    '''
    if connection_status:
        output_lines = ac_run_command(vpn_disconnect_command)
        connection_status = react_output_status(output_lines)
        
        if connection_status:
            logger.error('Unable to disconnect VPN connection')
        else:
            logger.info('VPN connection has been disconnected succesfully')
    else:
        logger.warn('VPN is not conneted, no need to disconnect')
    '''

if __name__ == '__main__':
    init_logging()
    main()
    


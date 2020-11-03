from fw_routes_test import MyCommonSetup

class ServicePolicyCommonSetup(MyCommonSetup):
    """
    CommonSetup class to prepare for testcases
    Establishes connections to all devices in testbed
    """
    pass


# golden_routes = {'198.18.31.0/24': {'next_hop': '198.18.33.194', 'outgoing_interface': 'vpn'}}


class VerifyServicePolicy(aetest.Testcase):
    """
    VerifyServicePolicy Testcase - check no drops in service-policy
    """

    @aetest.setup
    def prepare_for_check_service_policy(self) -> None:
        self.command = f'show service-policy'
        log.info(banner(f'Running command: {self.command}'))

    @aetest.test
    def check_service_policy_drops(self) -> None:
        # rib = {}
        device_to_connect = self.parent.parameters['dev']
        # output_next_hop = ''
        log.debug(device_to_connect)

        output = device_to_connect.parse(self.command)

        log.info(output)

        '''
        try:
            rib = output['vrf']['default']['address_family']['ipv4']['routes']
        except KeyError:
            self.failed(banner('Unable to get routes from output. Please check it conforms to the required format.'))

        for route in golden_routes.keys():
            if route not in rib:
                self.failed(f'{route} is not found')
            else:
                try:
                    output_next_hop = rib[route]['next_hop']['next_hop_list'][1]['next_hop']
                except KeyError:
                    self.failed(banner(f"Route {route} doesn't exist in routing table of {device_to_connect.name}"))

                output_outgoing_interface = rib[route]['next_hop']['next_hop_list'][1]['outgoing_interface_name']

                expected_next_hop = golden_routes[route]['next_hop']
                expected_outgoing_interface = golden_routes[route]['outgoing_interface']

                if expected_next_hop == output_next_hop and expected_outgoing_interface == output_outgoing_interface:
                    log.info(banner(f'Routing information for {route} on "{device_to_connect.name}" is correct.'))
                else:
                    self.failed(
                        banner(f'Routing information for {route} on "{device_to_connect.name}" has been changed.\n'
                               f'Expected next_hop: {expected_next_hop}. '
                               f'Got next_hop: {output_next_hop}.\n'
                               f'Expected outgoing_interface: "{expected_outgoing_interface}". '
                               f'Got outgoing_interface: "{output_outgoing_interface}".'))
        '''


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--testbed', dest='testbed',
                        type=loader.load)
    parser.add_argument('--device', dest='device_name')

    args = parser.parse_known_args()[0]

    aetest.main(**vars(args))


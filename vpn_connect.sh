$ vim vpn_connect.sh
#!/bin/bash

VPN_SERVER="vpn.sec.lab"

echo "Connecting to VPN.."
/opt/cisco/anyconnect/bin/vpn -s  < ~/.vpn_creds connect ${VPN_SERVER}

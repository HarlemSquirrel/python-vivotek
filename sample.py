#!/usr/bin/env python3

import keyring
from libpyvivotek import VivotekCamera

cam = VivotekCamera(host='192.168.2.184', port=80, usr='root',
                    pwd=keyring.get_password('camera', 'root'),
                    sec_lvl="admin")

print(f"Camera model:  {cam.model_name}")
print(f"Firmware:      {cam.get_param('system_info_firmwareversion')}")
print(f"Network info:  {cam.get_param('status_eth_i0')}")
print(f"RTSP port:     {cam.get_param('network_rtsp_port')}")
print(f"Serial number: {cam.get_serial()}")
print(f"MAC address:   {cam.get_mac()}")
print(f"Date & time:   {cam.get_param('system_date')} {cam.get_param('system_time')}")
print(f"Status:        {cam.get_param('status_vi_i0')}")

#!/usr/bin/env python3

import asyncio
import keyring

from libpyvivotek import VivotekCamera

async def main() -> None:
    cam = VivotekCamera(host='192.168.2.184', port=80, usr='root',
                        pwd=keyring.get_password('camera', 'root'),
                        sec_lvl="admin")
    await cam.set_device_info()
    print(f"Camera model:  {cam.model_name}")
    print(f"Firmware:      {await cam.get_firmware_version()}")
    print(f"Network info:  {await cam.get_param('status_eth_i0')}")
    print(f"RTSP port:     {await cam.get_param('network_rtsp_port')}")
    print(f"Serial number: {await cam.get_serial()}")
    print(f"MAC address:   {await cam.get_mac()}")
    print(f"Date & time:   {await cam.get_param('system_date')} {await cam.get_param('system_time')}")
    print(f"Status:        {await cam.get_param('status_vi_i0')}")

    await cam.close()


if __name__ == "__main__":
    asyncio.run(main())

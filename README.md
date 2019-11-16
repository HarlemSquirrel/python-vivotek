# python-vivotek

[![Build Status](https://travis-ci.org/HarlemSquirrel/python-vivotek.svg?branch=master)](https://travis-ci.org/HarlemSquirrel/python-vivotek)

A Python library for Vivotek IP cameras.

## Getting Started

### Install

This library currently supports Python 3.4 and up.

```sh
pip3 install libpyvivotek

# Or for only the current user
pip3 install --user libpyvivotek
```

### Usage

```py
from libpyvivotek import VivotekCamera

cam = VivotekCamera(host='192.168.1.123', port=443, usr='user', pwd='passw0rd',
                    ssl=True, verify_ssl=True, sec_lvl='admin')
print("Camera model is %s" % cam.model_name)
# Camera model is IB8369A
```

#### Security Level

Four security levels are currently supported:
- anonymous
- viewer
- operator
- admin

Using the `anonymous` security level does not require a user or password. The `operator` or `admin` security level is required to set parameters.

### Load password from Keyring

We can use [Python Keyring](https://pypi.org/project/keyring/) to load the password rather than from a string.

```sh
# Install the package
pip install --user keyring

# Set the password using the command-line interface.
python -m keyring set camera user passw0rd
```

```py
import keyring
from libpyvivotek import VivotekCamera

cam = VivotekCamera(host='192.168.1.123', port=443, usr='user',
                    pwd=keyring.get_password('camera', 'user'))
print("Camera model is %s" % cam.model_name)
# Camera model is IB8369A
```

### View a snapshot image

We can optionally specify the image quality to `snapshot()` from 1 to 5 with a default of 3.

```py
from libpyvivotek import VivotekCamera
from PIL import Image
from io import BytesIO
import keyring

cam = VivotekCamera(host='192.168.1.123', port=443, usr='user',
                    pwd=keyring.get_password('camera', 'user'))

snapshot = Image.open(BytesIO(cam.snapshot(quality=3)))

snapshot.show()
```

### Getting parameters

```py
cam.get_param('capability_api_httpversion')
# "0311b_1"

cam.get_param('capability_naudioin')
# "0"

cam.get_param('capability_protocol_https')
# "1"

cam.get_param('event_i0_enable')
# "1"

cam.get_param('motion_c0_enable')
# "1"
```

### Setting parameters

```py
cam.set_param('event_i0_enable', 1)
# "1"

cam.set_param('event_i0_enable', 0)
# "0"
```

# python-vivotek

[![Build Status](https://travis-ci.org/HarlemSquirrelpython-vivotek.svg?branch=master)](https://travis-ci.org/HarlemSquirrelpython-vivotek)

A Python library for Vivotek IP cameras.

## Getting Started

```py
from libpyvivotek import VivotekCamera

cam = VivotekCamera(host='192.168.1.123', port=443, usr='user', pwd='passw0rd')
print("Camera model is %s" % cam.model_name)
# Camera model is IB8369A
```

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

```py
from libpyvivotek import VivotekCamera
from PIL import Image
from io import BytesIO
import keyring

cam = VivotekCamera(host='192.168.1.123', port=443, usr='user',
                    pwd=keyring.get_password('camera', 'user'))
snapshot = Image.open(BytesIO(cam.snapshot()))
snapshot.show()
```

### Getting parameters

```py
cam.get_param('capability_api_httpversion')
# "'0311b_1'"

cam.get_param('capability_naudioin')
# "'0'"

cam.get_param('capability_protocol_https')
# "'1'"

cam.get_param('event_i0_enable')
# "'1'"

cam.get_param('motion_c0_enable')
# "'1'"
```

### Setting parameters

```py
cam.set_param('event_i0_enable', 1)
# "'1'"

cam.set_param('event_i0_enable', 0)
# "'0'"
```

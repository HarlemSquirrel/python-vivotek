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

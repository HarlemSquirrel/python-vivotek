import requests
from requests.auth import HTTPBasicAuth

DEFAULT_EVENT_0_KEY = "event_i0_enable"
DEFAULT_PATHS = {
    "get": "/cgi-bin/admin/getparam.cgi",
    "set": "/cgi-bin/admin/setparam.cgi",
    "still": "/cgi-bin/viewer/video.jpg",
}

class VivotekCameraError(Exception):
    """Custom Error class for VivotekCamera"""
    def __init__(self, message, errors=[]):
        super().__init__(message)
        self.errors = errors

class VivotekCamera(object):
    """A python implementation of the Vivotek IB8369A"""

    def __init__(self, host, port, usr, pwd, daemon=False, ssl=None, verify_ssl=True, verbose=True):
        """
        Initialize a camera.
        """
        self.host = host
        self.port = port
        self._requests_auth = HTTPBasicAuth(usr, pwd)
        self.daemon = daemon
        self.verbose = verbose

        self.ssl = ssl
        if port==443 and ssl is None:
            self.ssl = True
        if self.ssl is None:
            self.ssl = False
        if self.ssl is None or self.ssl is False:
            self.verify_ssl = False
        else:
            self.verify_ssl = verify_ssl

        _protocol = 'https' if self.ssl else 'http'
        self._get_param_url = _protocol + "://" + self.host + DEFAULT_PATHS["get"]
        self._set_param_url = _protocol + "://" + self.host + DEFAULT_PATHS["set"]
        self._still_image_url = _protocol + "://" + self.host + DEFAULT_PATHS["still"]

    def event_enabled(self, event_key):
        """Return true if event for the provided key is enabled."""
        response = self.get_param(event_key)
        return int(response.replace("'", "")) == 1

    def snapshot(self):
        """Return the bytes of current still image."""
        try:
            response = requests.get(
                self._still_image_url,
                auth=self._requests_auth,
                timeout=10,
                verify=self.verify_ssl,
            )

            return response.content
        except requests.exceptions.RequestException as error:
            raise VivotekCameraError(error)

    def get_param(self, param):
        """Return the value of the provided key."""
        try:
            response = requests.get(
                self._get_param_url,
                auth=self._requests_auth,
                params=(param),
                timeout=10,
                verify=self.verify_ssl,
            )

            return self.__parse_response_value(response)
        except requests.exceptions.RequestException as error:
            raise VivotekCameraError(error)

    def set_param(self, param, value):
        """Set and return the value of the provided key."""
        try:
            response = requests.post(
                self._set_param_url,
                auth=self._requests_auth,
                data={ param: value },
                timeout=10,
                verify=self.verify_ssl,
            )

            return self.__parse_response_value(response)
        except requests.exceptions.RequestException as error:
            raise VivotekCameraError(error)

    @property
    def model_name(self):
        """Return the model name of the camera."""
        try:
            return self._model_name
        except AttributeError:
            self._model_name = self.get_param("system_info_modelname").replace("'", "")
            return self._model_name

    def __parse_response_value(self, response):
        """
        Parse the response from an API call and return the value only.
        This assumes the response is in the key='value' format.
        An error will be raised when ERROR is found in the body of the response.
        """
        if 'ERROR' in response.text:
            raise VivotekCameraError(response.text)

        return response.text.strip().split('=')[1].replace("'", "")

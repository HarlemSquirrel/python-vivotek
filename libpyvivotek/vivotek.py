"""A python implementation of the Vivotek IB8369A"""
import requests
from requests.auth import HTTPBasicAuth
from requests.auth import HTTPDigestAuth

DEFAULT_EVENT_0_KEY = "event_i0_enable"
CGI_BASE_PATH = "/cgi-bin"
API_PATHS = {
    "get": "/getparam.cgi",
    "get_anon": "/getparam.cgi",
    "set": "/setparam.cgi",
    "still": "/video.jpg",
}
SECURITY_LEVELS = {
    "anonymous":    0,
    "viewer":       1,
    "operator":     4,
    "admin":        6
}

def parse_response_value(response:requests.Response) -> str:
    """
    Parse the response from an API call and return the value only.
    This assumes the response is in the key='value' format.
    An error will be raised when ERROR is found in the body of the response.
    """
    if 'ERROR' in response.text:
        raise VivotekCameraError(response.text)
    if response.status_code == 401:
        raise VivotekCameraError('Unauthorized. Credentials may be invalid.')

    return response.text.strip().split('=')[1].replace("'", "")

class VivotekCameraError(Exception):
    """Custom Error class for VivotekCamera"""

class VivotekCamera():
    """A Vivotek IB8369A camera object"""

    # pylint: disable=too-many-instance-attributes
    # pylint: disable=too-many-arguments
    def __init__(self, host, sec_lvl, port=None, usr=None, pwd=None, digest_auth=False, ssl=None,
                 verify_ssl=True):
        """
        Initialize a camera.
        """
        self.host = host

        if port is None:
            self._port = 443 if ssl else 80
        else:
            self._port = port

        if ssl or (self._port == 443 and ssl is None):
            self._ssl = True
        else:
            self._ssl = False

        if self._ssl is False:
            self.verify_ssl = False
        else:
            self.verify_ssl = verify_ssl

        if sec_lvl not in SECURITY_LEVELS.keys():
            raise VivotekCameraError("Invalid security level: %s" % sec_lvl)

        if usr is None or sec_lvl == 'anonymous':
            self._requests_auth = None
            self._security_level = 'anonymous'
        else:
            self._security_level = sec_lvl
            if digest_auth:
                self._requests_auth = HTTPDigestAuth(usr, pwd)
            else:
                self._requests_auth = HTTPBasicAuth(usr, pwd)

        self._model_name = None

        _protocol = 'https' if self._ssl else 'http'
        self._url_base = _protocol + "://" + self.host
        if (ssl is None and port != 80) or (ssl and port != 443):
            self._url_base += ":" + str(self._port)
        self._cgi_url_base = self._url_base + CGI_BASE_PATH + "/" + self._security_level

        self._get_param_url = self._cgi_url_base + API_PATHS["get"]
        self._set_param_url = self._cgi_url_base + API_PATHS["set"]
        self._still_image_url = self._url_base + CGI_BASE_PATH + "/viewer" + API_PATHS["still"]

        class VivotekCameraParameters:
            def __getitem__(_, key):
                """Return the value of the provided key."""
                request_args = dict(
                    params=(key),
                    timeout=10,
                    verify=self.verify_ssl
                )
                if self._requests_auth is not None:
                    request_args['auth'] = self._requests_auth
                try:
                    response = requests.get(self._get_param_url, **request_args)

                    return parse_response_value(response)
                except requests.exceptions.RequestException as error:
                    raise VivotekCameraError from error

            def __setitem__(_, key, value):
                """Set and return the value of the provided key."""
                if SECURITY_LEVELS[self._security_level] < 4:
                    raise VivotekCameraError("Security level %s is too low to set parameters."
                                            % self._security_level)

                try:
                    response = requests.post(
                        self._set_param_url,
                        auth=self._requests_auth,
                        data={key: value},
                        timeout=10,
                        verify=self.verify_ssl,
                    )

                    return parse_response_value(response)
                except requests.exceptions.RequestException as error:
                    raise VivotekCameraError from error
        
        self.params = VivotekCameraParameters()

    def event_enabled(self, event_key):
        """Return true if event for the provided key is enabled."""
        response = self.params[event_key]
        return int(response.replace("'", "")) == 1

    def snapshot(self, quality=3):
        """Return the bytes of current still image."""
        try:
            response = requests.get(
                self._still_image_url,
                params=dict(quality=quality),
                auth=self._requests_auth,
                timeout=10,
                verify=self.verify_ssl,
            )

            return response.content
        except requests.exceptions.RequestException as error:
            raise VivotekCameraError from error

    @property
    def model_name(self):
        """Return the model name of the camera."""
        if self._model_name is not None:
            return self._model_name

        self._model_name = self.params["system_info_modelname"]
        return self._model_name
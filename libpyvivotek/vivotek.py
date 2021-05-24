"""A python implementation of the Vivotek IB8369A"""
import requests
from requests.auth import HTTPBasicAuth
from requests.auth import HTTPDigestAuth

from posixpath import join as joinurlpath
from urllib.parse import urlunparse, quote_plus

def geturl(scheme:str, netloc:str, *path_parts:str):
    components = [
        scheme,
        netloc,
        joinurlpath(*path_parts),
        '',
        '',
        ''
    ]

    return urlunparse(components)

DEFAULT_EVENT_0_KEY = "event_i0_enable"
CGI_BASE_PATH = "cgi-bin"
API_PATHS = {
    "get": "getparam.cgi",
    "get_anon": "getparam.cgi",
    "set": "setparam.cgi",
    "still": "video.jpg",
}
SECURITY_LEVELS = {
    "anonymous":    0,
    "viewer":       1,
    "operator":     4,
    "admin":        6
}

def parse_parameter_entry(entry:str) -> tuple:
    entry = entry.strip()

    equalsindex = entry.index('=')

    key = entry[0:equalsindex]
    value = entry[equalsindex+2:-1]

    return key, value

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

    _, value = parse_parameter_entry(response.text)

    return value

class VivotekCameraError(Exception):
    """Custom Error class for VivotekCamera"""

class VivotekCamera():
    """A Vivotek IB8369A camera object"""

    # pylint: disable=too-many-instance-attributes
    # pylint: disable=too-many-arguments
    def __init__(self, netloc:str, security_level='anonymous', username=None, password=None, digest_auth=False, ssl=None,
                 verify_ssl=True):
        """
        Initialize a camera.
        """
        self.netloc = netloc

        self._ssl = bool(ssl)

        if self._ssl is False:
            self.verify_ssl = False
        else:
            self.verify_ssl = verify_ssl

        if security_level not in SECURITY_LEVELS.keys():
            raise VivotekCameraError("Invalid security level: %s" % security_level)

        if username is None or security_level == 'anonymous':
            self._requests_auth = None
            self._security_level = 'anonymous'
        else:
            self._security_level = security_level
            if digest_auth:
                self._requests_auth = HTTPDigestAuth(username, password)
            else:
                self._requests_auth = HTTPBasicAuth(username, password)

        self._model_name = None

        scheme = 'https' if self._ssl else 'http'

        self._cgi_base_path = joinurlpath(CGI_BASE_PATH, self._security_level)

        self._get_param_url = geturl(scheme, netloc, self._cgi_base_path, API_PATHS["get"])
        self._set_param_url = geturl(scheme, netloc, self._cgi_base_path, API_PATHS["set"])
        self._still_image_url = geturl(scheme, netloc, CGI_BASE_PATH, "viewer", API_PATHS["still"])

        class VivotekCameraParameters:
            def __getitem__(self, key):
                """Return the value of the provided key."""
                try:
                    return next(self.items(key))[1]
                except StopIteration as eof:
                    raise KeyError(key) from eof 

            def __setitem__(_, key, value):
                """Set and return the value of the provided key."""
                if SECURITY_LEVELS[self._security_level] < SECURITY_LEVELS["operator"]:
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

            def items(_, *params:str):
                urlsafe_params = [quote_plus(param) for param in params]
                parsed_params = '&'.join(urlsafe_params)

                request_args = dict(
                    params=parsed_params,
                    timeout=10,
                    verify=self.verify_ssl
                )

                if self._requests_auth is not None:
                    request_args['auth'] = self._requests_auth
                
                try:
                    response = requests.get(self._get_param_url, **request_args)
                    param_entry_lines = response.text.strip().splitlines()

                    for line in param_entry_lines:
                        yield parse_parameter_entry(line)
                    
                except requests.exceptions.RequestException as error:
                    raise VivotekCameraError from error
            
            def __iter__(self):
                for key, _ in self.items():
                    yield key
        
        self.params = VivotekCameraParameters()

        class VivotekCameraEvent:
            __prefix:str

            def __init__(event, prefix:str):
                event.__prefix = prefix

                class EnabledEventParameters:
                    def __contains__(_, key:str) -> bool:
                        try:
                            return int(event[key]) == 1
                        except (KeyError, ValueError):
                            return False
                
                event.enabled = EnabledEventParameters()

            def __getitem__(event, key:str):
                try:
                    return self.params[event.__prefix + key]
                except KeyError as knf:
                    raise KeyError(key) from knf
            
            def __setitem__(event, key:str, value):
                self.params[event.__prefix + key] = value
            
            def __iter__(event):
                prefix_length = len(event.__prefix)

                for key, _ in self.params.items(event.__prefix.strip('_')):
                    yield key[prefix_length:]

        class VivotekCameraEvents:
            def __getitem__(_, index:int) -> VivotekCameraEvent:
                try:
                    prefix = f"event_i{index}_"
                    next(self.params.items(prefix.strip('_')))

                    return VivotekCameraEvent(prefix)
                except StopIteration as eof:
                    raise KeyError(index) from eof
            
            def __iter__(events):
                index = 0
                
                try:
                    yield events[index]
                    index += 1
                except KeyError:
                    return
        
        self.events = VivotekCameraEvents()

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
"""Test VivotekCamera"""

from typing import TypedDict, NotRequired

import inspect
import unittest
import vcr # type: ignore

from libpyvivotek.vivotek import VivotekCamera, VivotekCameraError


class VivotekCameraConfig(TypedDict):
    """Typed config"""
    host: str
    sec_lvl: str
    port: NotRequired[int | None]          # optional key
    usr: NotRequired[str]                  # optional key
    pwd: NotRequired[str]                  # optional key
    digest_auth: NotRequired[bool]         # optional key
    ssl: NotRequired[bool | None]          # optional key
    verify_ssl: NotRequired[bool]          # optional key

TEST_CONNECTION_DETAILS: VivotekCameraConfig = {
    "host":'fake_ip.local',
    "usr": 'test_user',
    "pwd": 't3st_p@55w0rdZ',
    "ssl": True,
    "verify_ssl": False,
    "sec_lvl": 'admin'
}

class TestVivotekCamera(unittest.TestCase):
    """Tests for VivotekCamera."""

    def cassette_file_path(self) -> str:
        """
        Return the cassette file path based on the name of the function that called this function
        """
        return f"tests/fixtures/vcr_cassettes/vivotek_camera_{inspect.stack()[1][3][5:]}.yaml"

    def setUp(self) -> None:
        """"Test setup"""
        self.cam = VivotekCamera(**TEST_CONNECTION_DETAILS)

    def test_security_level_invalid(self) -> None:
        """Test security level validation"""
        cam_args = TEST_CONNECTION_DETAILS.copy()
        cam_args["sec_lvl"] = 'bad_sec_level'
        error_msg = 'Invalid security level: bad_sec_level'
        with self.assertRaises(VivotekCameraError, msg=error_msg):
            VivotekCamera(**cam_args)

    def test_snapshot(self) -> None:
        """Test snapshot"""
        with vcr.use_cassette(self.cassette_file_path()):
            self.assertIsInstance(self.cam.snapshot(), bytes)

    # Getting parameters
    # ------------------
    def test_get_param_error(self) -> None:
        """Test getting param that doesn't exist"""
        with vcr.use_cassette(self.cassette_file_path()):
            with self.assertRaises(VivotekCameraError):
                self.cam.get_param('bogus_param')

    def test_get_param_invalid_credentials(self) -> None:
        """Test get param with invalid credentials"""
        cam_args = TEST_CONNECTION_DETAILS.copy()
        cam_args["pwd"] ='badpassword'
        self.cam = VivotekCamera(**cam_args)
        error_msg = 'Unauthorized. Credentials may be invalid.'

        with vcr.use_cassette(self.cassette_file_path()):
            with self.assertRaises(VivotekCameraError, msg=error_msg):
                self.cam.get_param('capability_api_httpversion')

    def test_event_enabled_false(self) -> None:
        """Test event enabled false"""
        with vcr.use_cassette(self.cassette_file_path()):
            self.assertFalse(self.cam.event_enabled('event_i0_enable'))

    def test_event_enabled_true(self) -> None:
        """Test event enabled true"""
        with vcr.use_cassette(self.cassette_file_path()):
            self.assertTrue(self.cam.event_enabled('event_i0_enable'))

    def test_model_name_admin(self) -> None:
        """Test model name with admin sec level"""
        with vcr.use_cassette(self.cassette_file_path()):
            self.assertEqual(self.cam.model_name, 'IB8369A')

    def test_model_name_viewer(self) -> None:
        """Test get model name with viewer sec level"""
        cam_args = TEST_CONNECTION_DETAILS.copy()
        cam_args["sec_lvl"] ='viewer'
        self.cam = VivotekCamera(**cam_args)
        with vcr.use_cassette(self.cassette_file_path()):
            self.assertEqual(self.cam.model_name, 'IB8369A')

    def test_model_name_viewer_digest(self) -> None:
        """Test model name with viewer using digest auth"""
        cam_args = TEST_CONNECTION_DETAILS.copy()
        cam_args["sec_lvl"] ='viewer'
        cam_args["digest_auth"] = True
        self.cam = VivotekCamera(**cam_args)
        with vcr.use_cassette(self.cassette_file_path()):
            self.assertEqual(self.cam.model_name, 'IB8369A')

    def test_model_name_anon(self) -> None:
        """Test get model name with anonymous user"""
        cam_args = TEST_CONNECTION_DETAILS.copy()
        cam_args["sec_lvl"] ='anonymous'
        self.cam = VivotekCamera(**cam_args)
        with vcr.use_cassette(self.cassette_file_path()):
            self.assertEqual(self.cam.model_name, 'IB8369A')

    # Setting parameters
    # ------------------
    def test_set_param_error(self) -> None:
        """Test set param error"""
        with vcr.use_cassette(self.cassette_file_path()):
            with self.assertRaises(VivotekCameraError):
                self.cam.set_param('bogus_param', 'some_value')

    def test_set_param_security_level_too_low(self) -> None:
        """Test set param when sec level too low"""
        cam_args = TEST_CONNECTION_DETAILS.copy()
        cam_args["sec_lvl"] ='viewer'
        self.cam = VivotekCamera(**cam_args)
        error_msg="Security level viewer is too low to set parameters."
        with self.assertRaises(VivotekCameraError, msg=error_msg):
            self.assertTrue(self.cam.event_enabled('event_i0_enable'))


    def test_set_param_invalid_credentials(self) -> None:
        """Test set param with invalid credentials"""
        cam_args = TEST_CONNECTION_DETAILS.copy()
        cam_args["pwd"] ='badpassword'
        self.cam = VivotekCamera(**cam_args)
        error_msg = 'Unauthorized. Credentials may be invalid.'

        with vcr.use_cassette(self.cassette_file_path()):
            with self.assertRaises(VivotekCameraError, msg=error_msg):
                self.cam.set_param('event_i0_enable', 0)

    def test_set_param_enable_event(self) -> None:
        """Test set param to enable event"""
        with vcr.use_cassette(self.cassette_file_path()):
            self.assertEqual(self.cam.set_param('event_i0_enable', 1), "1")
            self.assertTrue(self.cam.event_enabled('event_i0_enable'))

    def test_set_param_disable_event(self) -> None:
        """Test set param to disable event"""
        with vcr.use_cassette(self.cassette_file_path()):
            self.assertEqual(self.cam.set_param('event_i0_enable', 0), "0")
            self.assertFalse(self.cam.event_enabled('event_i0_enable'))

    def test_set_param_enable_event_operator(self) -> None:
        """Test set param to enable event as operator"""
        cam_args = TEST_CONNECTION_DETAILS.copy()
        cam_args["sec_lvl"] ='operator'
        self.cam = VivotekCamera(**cam_args)
        error_msg = 'ERROR: Invalid command!'
        with vcr.use_cassette(self.cassette_file_path()):
            with self.assertRaises(VivotekCameraError, msg=error_msg):
                self.cam.set_param('event_i0_enable', 1)


if __name__ == '__main__':
    unittest.main()

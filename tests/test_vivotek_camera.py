import inspect
import unittest
import vcr

from libpyvivotek.vivotek import VivotekCamera, VivotekCameraError

TEST_CONNECTION_DETAILS = dict(
    host ='fake_ip.local',
    usr = 'test_user',
    pwd = 't3st_p@55w0rdZ',
    ssl = True,
    verify_ssl = False,
    sec_lvl = 'admin'
)

class TestVivotekCamera(unittest.TestCase):
    """Tests for VivotekCamera."""

    def cassette_file_path(self):
        """
        Return the cassette file path based on the name of the function that called this function
        """
        return "tests/fixtures/vcr_cassettes/vivotek_camera_%s.yaml" % inspect.stack()[1][3][5:]

    def setUp(self):
        self.cam = VivotekCamera(**TEST_CONNECTION_DETAILS)

    def test_security_level_invalid(self):
        cam_args = TEST_CONNECTION_DETAILS.copy()
        cam_args.update(sec_lvl='bad_sec_level')
        error_msg = 'Invalid security level: bad_sec_level'
        with self.assertRaises(VivotekCameraError, msg=error_msg):
            cam = VivotekCamera(**cam_args)

    def test_snapshot(self):
        with vcr.use_cassette(self.cassette_file_path()):
            self.assertIsInstance(self.cam.snapshot(), bytes)

    # Getting parameters
    # ------------------
    def test_get_param_error(self):
        with vcr.use_cassette(self.cassette_file_path()):
            with self.assertRaises(VivotekCameraError):
                self.cam.get_param('bogus_param')

    def test_get_param_invalid_credentials(self):
        cam_args = TEST_CONNECTION_DETAILS.copy()
        cam_args.update(pwd='badpassword')
        self.cam = VivotekCamera(**cam_args)
        error_msg = 'Unauthorized. Credentials may be invalid.'

        with vcr.use_cassette(self.cassette_file_path()):
            with self.assertRaises(VivotekCameraError, msg=error_msg):
                self.cam.get_param('capability_api_httpversion')

    def test_event_enabled_false(self):
        with vcr.use_cassette(self.cassette_file_path()):
            self.assertFalse(self.cam.event_enabled('event_i0_enable'))

    def test_event_enabled_true(self):
        with vcr.use_cassette(self.cassette_file_path()):
            self.assertTrue(self.cam.event_enabled('event_i0_enable'))

    def test_model_name_admin(self):
        with vcr.use_cassette(self.cassette_file_path()):
            self.assertEqual(self.cam.model_name, 'IB8369A')

    def test_model_name_viewer(self):
        cam_args = TEST_CONNECTION_DETAILS.copy()
        cam_args.update(sec_lvl='viewer')
        self.cam = VivotekCamera(**cam_args)
        with vcr.use_cassette(self.cassette_file_path()):
            self.assertEqual(self.cam.model_name, 'IB8369A')

    def test_model_name_anon(self):
        cam_args = TEST_CONNECTION_DETAILS.copy()
        cam_args.update(sec_lvl='anonymous')
        self.cam = VivotekCamera(**cam_args)
        with vcr.use_cassette(self.cassette_file_path()):
            self.assertEqual(self.cam.model_name, 'IB8369A')

    # Setting parameters
    # ------------------
    def test_set_param_error(self):
        with vcr.use_cassette(self.cassette_file_path()):
            with self.assertRaises(VivotekCameraError):
                self.cam.set_param('bogus_param', 'some_value')

    def test_set_param_security_level_too_low(self):
        cam_args = TEST_CONNECTION_DETAILS.copy()
        cam_args.update(sec_lvl='viewer')
        self.cam = VivotekCamera(**cam_args)
        error_msg="Security level viewer is too low to set parameters."
        with self.assertRaises(VivotekCameraError, msg=error_msg):
            self.assertTrue(self.cam.event_enabled('event_i0_enable'))


    def test_set_param_invalid_credentials(self):
        cam_args = TEST_CONNECTION_DETAILS.copy()
        cam_args.update(pwd='badpassword')
        self.cam = VivotekCamera(**cam_args)
        error_msg = 'Unauthorized. Credentials may be invalid.'

        with vcr.use_cassette(self.cassette_file_path()):
            with self.assertRaises(VivotekCameraError, msg=error_msg):
                self.cam.set_param('event_i0_enable', 0)

    def test_set_param_enable_event(self):
        with vcr.use_cassette(self.cassette_file_path()):
            self.assertEqual(self.cam.set_param('event_i0_enable', 1), "1")
            self.assertTrue(self.cam.event_enabled('event_i0_enable'))

    def test_set_param_disable_event(self):
        with vcr.use_cassette(self.cassette_file_path()):
            self.assertEqual(self.cam.set_param('event_i0_enable', 0), "0")
            self.assertFalse(self.cam.event_enabled('event_i0_enable'))

    def test_set_param_enable_event_operator(self):
        cam_args = TEST_CONNECTION_DETAILS.copy()
        cam_args.update(sec_lvl='operator')
        self.cam = VivotekCamera(**cam_args)
        error_msg = 'ERROR: Invalid command!'
        with vcr.use_cassette(self.cassette_file_path()):
            with self.assertRaises(VivotekCameraError, msg=error_msg):
                self.cam.set_param('event_i0_enable', 1)


if __name__ == '__main__':
    unittest.main()

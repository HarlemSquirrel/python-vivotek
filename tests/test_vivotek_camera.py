import unittest
import vcr

from libpyvivotek.vivotek import VivotekCamera, VivotekCameraError

TEST_CONNECTION_DETAILS = dict(
    host ='fake_ip.local',
    port = 443,
    usr = 'test_user',
    pwd = 't3st_p@55w0rdZ',
    verify_ssl = False
)

class TestVivotekCamera(unittest.TestCase):
    """Tests for VivotekCamera."""

    def setUp(self):
        self.cam = VivotekCamera(**TEST_CONNECTION_DETAILS)

    # Getting parameters
    # ------------------
    def test_get_param_error(self):
        with vcr.use_cassette('tests/fixtures/vcr_cassettes/vivotek_camera_get_param_error.yaml'):
            with self.assertRaises(VivotekCameraError):
                self.cam.get_param('bogus_param')

    def test_event_enabled_false(self):
        with vcr.use_cassette('tests/fixtures/vcr_cassettes/vivotek_camera_event_enabled_false.yaml'):
            self.assertFalse(self.cam.event_enabled('event_i0_enable'))

    def test_event_enabled_true(self):
        with vcr.use_cassette('tests/fixtures/vcr_cassettes/vivotek_camera_event_enabled_true.yaml'):
            self.assertTrue(self.cam.event_enabled('event_i0_enable'))

    def test_model_name(self):
        with vcr.use_cassette('tests/fixtures/vcr_cassettes/vivotek_camera_model_name.yaml'):
            self.assertEqual(self.cam.model_name, 'IB8369A')

    # Setting parameters
    # ------------------
    def test_set_param_error(self):
        with vcr.use_cassette('tests/fixtures/vcr_cassettes/vivotek_camera_set_param_error.yaml'):
            with self.assertRaises(VivotekCameraError):
                self.cam.set_param('bogus_param', 'some_value')

    def test_set_param_enable_event(self):
        with vcr.use_cassette('tests/fixtures/vcr_cassettes/vivotek_camera_set_param_enable_event.yaml'):
            self.assertEqual(self.cam.set_param('event_i0_enable', 1), "'1'")
            self.assertTrue(self.cam.event_enabled('event_i0_enable'))

    def test_set_param_disable_event(self):
        with vcr.use_cassette('tests/fixtures/vcr_cassettes/vivotek_camera_set_param_disable_event.yaml'):
            self.assertEqual(self.cam.set_param('event_i0_enable', 0), "'0'")
            self.assertFalse(self.cam.event_enabled('event_i0_enable'))


if __name__ == '__main__':
    unittest.main()

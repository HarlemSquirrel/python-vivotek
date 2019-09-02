import unittest
import vcr

from libpyvivotek.vivotek import VivotekCamera

TEST_CONNECTION_DETAILS = dict(
    host ='fake_ip.local',
    port = 443,
    usr = 'test_user',
    pwd = 't3st_p@55w0rdZ',
    verify_ssl = False
)

class TestVivotekCamera(unittest.TestCase):
    """docstring for TestVivotekCamera."""

    def setUp(self):
        self.cam = VivotekCamera(**TEST_CONNECTION_DETAILS)

    def test_event_enabled_false(self):
        with vcr.use_cassette('tests/fixtures/vcr_cassettes/vivotek_camera_event_enabled_false.yaml'):
            self.assertFalse(self.cam.event_enabled('event_i0_enable'))

    def test_event_enabled_true(self):
        with vcr.use_cassette('tests/fixtures/vcr_cassettes/vivotek_camera_event_enabled_true.yaml'):
            self.assertTrue(self.cam.event_enabled('event_i0_enable'))

    def test_model_name(self):
        with vcr.use_cassette('tests/fixtures/vcr_cassettes/vivotek_camera_model_name.yaml'):
            self.assertEqual(self.cam.model_name, 'IB8369A')

if __name__ == '__main__':
    unittest.main()

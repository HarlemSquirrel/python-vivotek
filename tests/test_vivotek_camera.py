"""Test VivotekCamera"""

from typing import TypedDict, NotRequired, AsyncGenerator

import inspect
from unittest.mock import patch

import pytest
import pytest_asyncio
import vcr  # type: ignore

from libpyvivotek.vivotek import VivotekCamera, VivotekCameraError


class VivotekCameraConfig(TypedDict):
    """Typed config"""

    host: str
    sec_lvl: str
    port: NotRequired[int | None]  # optional key
    usr: NotRequired[str]  # optional key
    pwd: NotRequired[str]  # optional key
    digest_auth: NotRequired[bool]  # optional key
    ssl: NotRequired[bool | None]  # optional key
    verify_ssl: NotRequired[bool]  # optional key


TEST_CONNECTION_DETAILS: VivotekCameraConfig = {
    "host": "fake_ip.local",
    "usr": "test_user",
    "pwd": "t3st_p@55w0rdZ",
    "ssl": True,
    "verify_ssl": False,
    "sec_lvl": "admin",
}

class TestVivotekCamera:
    """Tests for VivotekCamera."""

    cam: VivotekCamera  # Class attribute to avoid pylint W0201

    def cassette_file_path(self) -> str:
        """
        Return the cassette file path based on the name of the function that called this function
        """
        caller = inspect.stack()[1][3]
        cassette_name = caller.removeprefix("test_")
        return f"tests/fixtures/vcr_cassettes/vivotek_camera_{cassette_name}.yaml"


    @pytest_asyncio.fixture(autouse=True)
    async def setup_cam(self) -> AsyncGenerator[None, None]:
        """
        Fixture to set up and tear down the VivotekCamera instance.
        """
        self.cam = VivotekCamera(**TEST_CONNECTION_DETAILS)
        yield
        await self.cam.close()

    def test_security_level_invalid(self) -> None:
        """Test security level validation"""
        cam_args = TEST_CONNECTION_DETAILS.copy()
        cam_args["sec_lvl"] = "bad_sec_level"
        error_msg = "Invalid security level: bad_sec_level"
        with pytest.raises(VivotekCameraError, match=error_msg):
            VivotekCamera(**cam_args)

    @pytest.mark.asyncio
    async def test_snapshot(self) -> None:
        """Test snapshot"""
        with vcr.use_cassette(self.cassette_file_path(), record_mode='none'):
            snapshot = await self.cam.snapshot()
            assert isinstance(snapshot, bytes)

    # Getting parameters
    # ------------------
    @pytest.mark.asyncio
    async def test_get_param_error(self) -> None:
        """Test getting param that doesn't exist"""
        with vcr.use_cassette(self.cassette_file_path(), record_mode='none'):
            with pytest.raises(VivotekCameraError):
                await self.cam.get_param("bogus_param")

    @pytest.mark.asyncio
    async def test_get_param_invalid_credentials(self) -> None:
        """Test get param with invalid credentials"""
        cam_args = TEST_CONNECTION_DETAILS.copy()
        cam_args["pwd"] = "badpassword"
        self.cam = VivotekCamera(**cam_args)
        error_msg = "Unauthorized. Credentials may be invalid."

        with vcr.use_cassette(self.cassette_file_path(), record_mode='none'):
            with pytest.raises(VivotekCameraError, match=error_msg):
                await self.cam.get_param("capability_api_httpversion")

    @pytest.mark.asyncio
    async def test_event_enabled_false(self) -> None:
        """Test event enabled false"""
        with vcr.use_cassette(self.cassette_file_path(), record_mode='none'):
            result = await self.cam.event_enabled("event_i0_enable")
            assert not result

    @pytest.mark.asyncio
    async def test_event_enabled_true(self) -> None:
        """Test event enabled true"""
        with vcr.use_cassette(self.cassette_file_path(), record_mode='none'):
            result = await self.cam.event_enabled("event_i0_enable")
            assert result

    @pytest.mark.asyncio
    async def test_get_model_name_admin(self) -> None:
        """Test model name with admin sec level"""
        with vcr.use_cassette(self.cassette_file_path(), record_mode='none'):
            model_name = await self.cam.get_model()
            assert model_name == "IB8369A"

    @pytest.mark.asyncio
    async def test_get_model_name_viewer(self) -> None:
        """Test get model name with viewer sec level"""
        cam_args = TEST_CONNECTION_DETAILS.copy()
        cam_args["sec_lvl"] = "viewer"
        self.cam = VivotekCamera(**cam_args)
        with vcr.use_cassette(self.cassette_file_path(), record_mode='none'):
            model_name = await self.cam.get_model()
            assert model_name == "IB8369A"

    @pytest.mark.asyncio
    async def test_get_model_name_viewer_digest(self) -> None:
        """Test model name with viewer using digest auth"""
        cam_args = TEST_CONNECTION_DETAILS.copy()
        cam_args["sec_lvl"] = "viewer"
        cam_args["digest_auth"] = True
        self.cam = VivotekCamera(**cam_args)
        with vcr.use_cassette(self.cassette_file_path(), record_mode='none'):
            model_name = await self.cam.get_model()
            assert model_name == "IB8369A"

    @pytest.mark.asyncio
    async def test_get_model_name_anon(self) -> None:
        """Test get model name with anonymous user"""
        cam_args = TEST_CONNECTION_DETAILS.copy()
        cam_args["sec_lvl"] = "anonymous"
        self.cam = VivotekCamera(**cam_args)
        with vcr.use_cassette(self.cassette_file_path(), record_mode='none'):
            model_name = await self.cam.get_model()
            assert model_name == "IB8369A"

    @pytest.mark.asyncio
    async def test_set_device_info(self) -> None:
        """Test set device info caches model and serial."""
        with patch.object(
            self.cam, "get_param", side_effect=["IB8369A", "123456"]
        ):
            await self.cam.set_device_info()

        assert self.cam.model_name == "IB8369A"
        assert self.cam.serial_number == "123456"

    @pytest.mark.asyncio
    async def test_get_firmware_version(self) -> None:
        """Test get firmware version."""
        with patch.object(
            self.cam, "get_param", return_value="0104a"
        ):
            assert await self.cam.get_firmware_version() == "0104a"

    # Setting parameters
    # ------------------
    @pytest.mark.asyncio
    async def test_set_param_error(self) -> None:
        """Test set param error"""
        with vcr.use_cassette(self.cassette_file_path(), record_mode='none'):
            with pytest.raises(VivotekCameraError):
                await self.cam.set_param("bogus_param", "some_value")

    @pytest.mark.asyncio
    async def test_set_param_security_level_too_low(self) -> None:
        """Test set param when sec level too low"""
        cam_args = TEST_CONNECTION_DETAILS.copy()
        cam_args["sec_lvl"] = "viewer"
        self.cam = VivotekCamera(**cam_args)
        error_msg = "Security level viewer is too low to set parameters."
        with pytest.raises(VivotekCameraError, match=error_msg):
            await self.cam.set_param("event_i0_enable", 1)

    @pytest.mark.asyncio
    async def test_set_param_invalid_credentials(self) -> None:
        """Test set param with invalid credentials"""
        cam_args = TEST_CONNECTION_DETAILS.copy()
        cam_args["pwd"] = "badpassword"
        self.cam = VivotekCamera(**cam_args)
        error_msg = "Unauthorized. Credentials may be invalid."

        with vcr.use_cassette(self.cassette_file_path(), record_mode='none'):
            with pytest.raises(VivotekCameraError, match=error_msg):
                await self.cam.set_param("event_i0_enable", 1)

    @pytest.mark.asyncio
    async def test_set_param_enable_event(self) -> None:
        """Test set param to enable event"""
        with vcr.use_cassette(self.cassette_file_path(), record_mode='none'):
            assert await self.cam.set_param("event_i0_enable", 1) == "1"

    @pytest.mark.asyncio
    async def test_set_param_disable_event(self) -> None:
        """Test set param to disable event"""
        with vcr.use_cassette(self.cassette_file_path(), record_mode='none'):
            assert await self.cam.set_param("event_i0_enable", 0) == "0"

    @pytest.mark.asyncio
    async def test_set_param_enable_event_operator(self) -> None:
        """Test set param to enable event as operator"""
        cam_args = TEST_CONNECTION_DETAILS.copy()
        cam_args["sec_lvl"] = "operator"
        self.cam = VivotekCamera(**cam_args)
        error_msg = "ERROR: Invalid command!"
        with vcr.use_cassette(self.cassette_file_path(), record_mode='none'):
            with pytest.raises(VivotekCameraError, match=error_msg):
                await self.cam.set_param("event_i0_enable", 1)

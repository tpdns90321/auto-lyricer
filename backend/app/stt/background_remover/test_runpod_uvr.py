import pytest
from unittest.mock import AsyncMock, Mock, patch
from aiohttp import ClientSession
from base64 import b64encode

from .runpod_uvr import RunpodUVR, RunpodUVRConfig, RunpodUVRResponse
from ..data import Audio, AudioExtension


@pytest.fixture
def valid_config():
    return {
        "RUNPOD_API_KEY": "test_api_key",
        "RUNPOD_UVR_ENDPOINT": "https://api.runpod.io/test/",
    }


@pytest.fixture
def invalid_config_missing_key():
    return {"RUNPOD_API_KEY": "", "RUNPOD_UVR_ENDPOINT": "https://api.runpod.io/test/"}


@pytest.fixture
def invalid_config_missing_endpoint():
    return {"RUNPOD_API_KEY": "test_api_key", "RUNPOD_UVR_ENDPOINT": ""}


@pytest.fixture
def mp3_audio():
    return Audio(binary=b"mp3_audio_data", extension=AudioExtension.MP3)


@pytest.fixture
def wav_audio():
    return Audio(binary=b"wav_audio_data", extension=AudioExtension.WAV)


@pytest.fixture
def ogg_audio():
    return Audio(binary=b"ogg_audio_data", extension=AudioExtension.OGG)


@pytest.fixture
def aac_audio():
    return Audio(binary=b"aac_audio_data", extension=AudioExtension.AAC)


@pytest.fixture
def mock_session():
    return Mock(spec=ClientSession)


class TestRunpodUVRConfig:
    def test_config_creation_with_valid_data(self, valid_config):
        config = RunpodUVRConfig(**valid_config)
        assert config.RUNPOD_API_KEY == "test_api_key"
        assert config.RUNPOD_UVR_ENDPOINT == "https://api.runpod.io/test/"

    def test_config_is_frozen(self, valid_config):
        config = RunpodUVRConfig(**valid_config)
        with pytest.raises(AttributeError):
            config.RUNPOD_API_KEY = "new_key"


class TestRunpodUVRResponse:
    def test_response_creation_with_valid_data(self):
        output_data = {"vocals": "base64_encoded_audio_data"}
        response = RunpodUVRResponse(output=output_data)
        assert response.output == output_data

    def test_response_is_frozen(self):
        response = RunpodUVRResponse(output={"vocals": "test"})
        with pytest.raises(AttributeError):
            response.output = {"new": "data"}


class TestRunpodUVR:
    @patch("app.stt.background_remover.runpod_uvr.ClientSession")
    def test_supported_audio_extensions(self, mock_client_session, valid_config):
        uvr = RunpodUVR(valid_config)
        expected_extensions = (
            AudioExtension.MP3,
            AudioExtension.OGG,
            AudioExtension.WAV,
        )
        assert uvr.supported_audio_extensions == expected_extensions

    @patch("app.stt.background_remover.runpod_uvr.ClientSession")
    def test_output_audio_extension(self, mock_client_session, valid_config):
        uvr = RunpodUVR(valid_config)
        assert uvr.output_audio_extension == AudioExtension.OGG

    @patch("app.stt.background_remover.runpod_uvr.ClientSession")
    def test_initialization_with_valid_config(self, mock_client_session, valid_config):
        uvr = RunpodUVR(valid_config)
        assert uvr._config.RUNPOD_API_KEY == "test_api_key"
        assert uvr._config.RUNPOD_UVR_ENDPOINT == "https://api.runpod.io/test/"
        mock_client_session.assert_called_once()

    def test_initialization_with_missing_api_key(self, invalid_config_missing_key):
        with pytest.raises(
            ValueError, match="RUNPOD_API_KEY must be provided in the configuration"
        ):
            RunpodUVR(invalid_config_missing_key)

    def test_initialization_with_missing_endpoint(
        self, invalid_config_missing_endpoint
    ):
        with pytest.raises(
            ValueError,
            match="RUNPOD_UVR_ENDPOINT must be provided in the configuration",
        ):
            RunpodUVR(invalid_config_missing_endpoint)

    @pytest.mark.asyncio
    @patch("app.stt.background_remover.runpod_uvr.ClientSession")
    async def test_remove_background_success_with_mp3(
        self, mock_client_session, valid_config, mp3_audio
    ):
        uvr = RunpodUVR(valid_config)

        processed_audio_data = b"processed_vocals_data"
        mock_response_data = {
            "output": {"vocals": b64encode(processed_audio_data).decode("utf-8")}
        }

        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_response_data)

        uvr._session.post = AsyncMock(return_value=mock_response)

        result = await uvr._remove_background(mp3_audio)

        uvr._session.post.assert_called_once_with(
            "/runsync",
            json={
                "input": {
                    "audio": b64encode(mp3_audio.binary).decode("utf-8"),
                    "parts": ["vocals"],
                },
            },
        )

        assert result.binary == processed_audio_data
        assert result.extension == AudioExtension.OGG

    @pytest.mark.asyncio
    @patch("app.stt.background_remover.runpod_uvr.ClientSession")
    async def test_remove_background_success_with_wav(
        self, mock_client_session, valid_config, wav_audio
    ):
        uvr = RunpodUVR(valid_config)

        processed_audio_data = b"processed_wav_vocals"
        mock_response_data = {
            "output": {"vocals": b64encode(processed_audio_data).decode("utf-8")}
        }

        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_response_data)

        uvr._session.post = AsyncMock(return_value=mock_response)

        result = await uvr._remove_background(wav_audio)

        assert result.binary == processed_audio_data
        assert result.extension == AudioExtension.OGG

    @pytest.mark.asyncio
    @patch("app.stt.background_remover.runpod_uvr.ClientSession")
    async def test_remove_background_api_error(
        self, mock_client_session, valid_config, mp3_audio
    ):
        uvr = RunpodUVR(valid_config)

        mock_response = Mock()
        mock_response.status = 500

        uvr._session.post = AsyncMock(return_value=mock_response)

        with pytest.raises(RuntimeError, match="Runpod UVR API returned status 500"):
            await uvr._remove_background(mp3_audio)

    @pytest.mark.asyncio
    @patch("app.stt.background_remover.runpod_uvr.ClientSession")
    async def test_remove_background_with_unsupported_format(
        self, mock_client_session, valid_config, aac_audio
    ):
        uvr = RunpodUVR(valid_config)

        converted_audio = Audio(
            binary=b"converted_mp3_data", extension=AudioExtension.MP3
        )
        processed_audio_data = b"processed_vocals_from_converted"

        mock_response_data = {
            "output": {"vocals": b64encode(processed_audio_data).decode("utf-8")}
        }

        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_response_data)

        uvr._session.post = AsyncMock(return_value=mock_response)

        with patch.object(uvr, "_convert_audio") as mock_convert:
            mock_convert.return_value = converted_audio

            result = await uvr.remove_background(aac_audio)

            mock_convert.assert_called_once_with(aac_audio)
            uvr._session.post.assert_called_once_with(
                "/runsync",
                json={
                    "input": {
                        "audio": b64encode(converted_audio.binary).decode("utf-8"),
                        "parts": ["vocals"],
                    },
                },
            )

            assert result.binary == processed_audio_data
            assert result.extension == AudioExtension.OGG

    @pytest.mark.asyncio
    @patch("app.stt.background_remover.runpod_uvr.ClientSession")
    async def test_remove_background_with_empty_audio(
        self, mock_client_session, valid_config
    ):
        uvr = RunpodUVR(valid_config)
        empty_audio = Audio(binary=b"", extension=AudioExtension.MP3)

        processed_audio_data = b"processed_empty"
        mock_response_data = {
            "output": {"vocals": b64encode(processed_audio_data).decode("utf-8")}
        }

        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_response_data)

        uvr._session.post = AsyncMock(return_value=mock_response)

        result = await uvr._remove_background(empty_audio)

        uvr._session.post.assert_called_once_with(
            "/runsync",
            json={
                "input": {
                    "audio": b64encode(b"").decode("utf-8"),
                    "parts": ["vocals"],
                },
            },
        )

        assert result.binary == processed_audio_data
        assert result.extension == AudioExtension.OGG

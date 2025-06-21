from ...shared.supported import SubtitleExtension
from ..data import Audio, AudioExtension
from .runpod_whisper import (
    RunpodWhisper,
    RunpodWhisperConfig,
    RunpodWhisperResponse,
)

import pytest
import pytest_asyncio
from unittest import mock


@pytest.fixture
def valid_config():
    return {
        "api_key": "test_api_key",
        "endpoint": "https://api.runpod.io/test/",
        "model": "whisper-1",
        "temperature": 0,
        "best_of": 5,
        "beam_size": 5,
        "patience": None,
        "length_penalty": None,
        "suppress_tokens": -1,
        "condition_on_previous_text": True,
        "temperature_increment_on_fallback": 0.2,
        "compression_ratio_threshold": 2.4,
        "logprob_threshold": -1.0,
        "no_speech_threshold": 0.6,
    }


@pytest.fixture
def invalid_config_missing_api_key():
    return {
        "api_key": "",
        "endpoint": "https://api.runpod.io/test/",
        "model": "whisper-1",
        "temperature": 1,
        "best_of": 5,
        "beam_size": 5,
        "patience": None,
        "length_penalty": None,
        "suppress_tokens": -1,
        "condition_on_previous_text": True,
        "temperature_increment_on_fallback": 0.2,
        "compression_ratio_threshold": 2.4,
        "logprob_threshold": -1.0,
        "no_speech_threshold": 0.6,
    }


@pytest.fixture
def invalid_config_missing_endpoint():
    return {
        "api_key": "test_api_key",
        "endpoint": "",
        "model": "whisper-1",
        "temperature": 1,
        "best_of": 5,
        "beam_size": 5,
        "patience": None,
        "length_penalty": None,
        "suppress_tokens": -1,
        "condition_on_previous_text": True,
        "temperature_increment_on_fallback": 0.2,
        "compression_ratio_threshold": 2.4,
        "logprob_threshold": -1.0,
        "no_speech_threshold": 0.6,
    }


@pytest.fixture
def invalid_config_missing_model():
    return {
        "api_key": "test_api_key",
        "endpoint": "https://api.runpod.io/test/",
        "model": "",
        "temperature": "1",
        "best_of": "5",
        "beam_size": "5",
        "patience": None,
        "length_penalty": None,
        "suppress_tokens": "-1",
        "condition_on_previous_text": "true",
        "temperature_increment_on_fallback": "0.2",
        "compression_ratio_threshold": "2.4",
        "logprob_threshold": "-1.0",
        "no_speech_threshold": "0.6",
    }


@pytest.fixture
def mp3_audio():
    return Audio(binary=b"mp3_audio_data", extension=AudioExtension.MP3)


# Test cases for RunpodWhisperConfig


@pytest.fixture
def valid_config_instance(valid_config):
    return RunpodWhisperConfig(**valid_config)


def test_config_creation_with_valid_data(valid_config_instance):
    assert valid_config_instance.api_key == "test_api_key"
    assert valid_config_instance.endpoint == "https://api.runpod.io/test/"


def test_config_is_frozen(valid_config_instance):
    with pytest.raises(AttributeError):
        valid_config_instance.api_key = "new_key"


# Test cases for RunpodWhisperResponse


@pytest.fixture
def valid_response():
    return RunpodWhisperResponse(
        transcription="transcribed text",
        detected_language="en",
        segments=[],
        model="whisper-1",
    )


def test_response_creation_with_valid_data(valid_response):
    assert valid_response.transcription == "transcribed text"
    assert valid_response.detected_language == "en"


def test_response_is_frozen(valid_response):
    with pytest.raises(AttributeError):
        valid_response.transcription = "new transcription"
    with pytest.raises(AttributeError):
        valid_response.detected_language = "fr"


# Test cases for RunpodWhisper class methods


@pytest_asyncio.fixture
async def runpod_whisper(valid_config):
    return RunpodWhisper(config=valid_config)


def test_missing_api_key_raises_error(invalid_config_missing_api_key):
    with pytest.raises(
        ValueError, match="api_key must be provided in the configuration."
    ):
        RunpodWhisper(invalid_config_missing_api_key)


def test_missing_endpoint_raises_error(invalid_config_missing_endpoint):
    with pytest.raises(
        ValueError, match="endpoint must be provided in the configuration."
    ):
        RunpodWhisper(invalid_config_missing_endpoint)


def test_missing_model_raises_error(invalid_config_missing_model):
    with pytest.raises(
        ValueError, match="model must be provided in the configuration."
    ):
        RunpodWhisper(invalid_config_missing_model)


@pytest.mark.asyncio
async def test_supported_audio_extensions(runpod_whisper):
    expected_extensions = (
        AudioExtension.MP3,
        AudioExtension.OGG,
        AudioExtension.WAV,
    )
    assert runpod_whisper._supported_audio_extensions == expected_extensions


@pytest.mark.asyncio
async def test_output_transcriptions_subtitle_extension(runpod_whisper):
    assert runpod_whisper._output_subtitle_extension == SubtitleExtension.VTT


@pytest.mark.asyncio
async def test_transcribe_success_with_mp3(runpod_whisper, mp3_audio):
    mock_response = mock.Mock()
    mock_response.status = 200
    mock_response.json = mock.AsyncMock(
        return_value={
            "output": {
                "segments": [],
                "transcription": "This is a test transcription.",
                "detected_language": "en",
                "model": "whisper-1",
            }
        }
    )

    runpod_whisper._session.post = mock.AsyncMock(return_value=mock_response)

    transcription = await runpod_whisper.transcribe(mp3_audio)
    assert transcription.content == "This is a test transcription."
    assert transcription.extension == SubtitleExtension.VTT


@pytest.mark.asyncio
async def test_transcribe_api_error(runpod_whisper, mp3_audio):
    mock_response = mock.Mock()
    mock_response.status = 500

    runpod_whisper._session.post = mock.AsyncMock(return_value=mock_response)
    with pytest.raises(RuntimeError, match="Failed to transcribe audio: 500"):
        await runpod_whisper.transcribe(mp3_audio)

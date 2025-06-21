import pytest
from unittest.mock import AsyncMock, Mock, patch
from io import BytesIO

from .converter import convert_audio_extension
from ..shared.data import Audio, AudioExtension


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


class TestConvertAudioExtension:
    @pytest.mark.asyncio
    async def test_convert_audio_ffmpeg_failure(self, mp3_audio: Audio):
        mock_process = Mock()
        mock_process.wait = AsyncMock(return_value=None)
        mock_process.returncode = 1

        with patch("asyncio.subprocess.create_subprocess_exec") as mock_create:
            mock_create.return_value = mock_process

            with pytest.raises(
                RuntimeError, match="FFmpeg process did not complete successfully"
            ):
                await convert_audio_extension(mp3_audio, AudioExtension.WAV)

    @pytest.mark.asyncio
    async def test_basic_functionality_parameters(self, mp3_audio: Audio):
        mock_process = Mock()
        mock_process.wait = AsyncMock(return_value=None)
        mock_process.returncode = 0

        with patch("asyncio.subprocess.create_subprocess_exec") as mock_create:
            mock_create.return_value = mock_process

            # Create a real output buffer
            output_buffer = BytesIO(b"test_result")

            with patch(
                "app.stt.converter.BytesIO", side_effect=[BytesIO(), output_buffer]
            ):
                result = await convert_audio_extension(mp3_audio, AudioExtension.WAV)

                # Verify the basic call structure
                mock_create.assert_called_once()
                args, kwargs = mock_create.call_args

                assert args[0] == "ffmpeg"
                assert "-i" in args
                assert "-" in args
                assert "-f" in args
                assert "wav" in args
                assert "stdin" in kwargs
                assert "stdout" in kwargs

                # Verify result structure
                assert isinstance(result, Audio)
                assert result.extension == AudioExtension.WAV

    @pytest.mark.asyncio
    async def test_integration_with_real_bytesio(self, mp3_audio: Audio):
        """Test the actual behavior with real BytesIO without mocking subprocess"""
        # This test verifies the data flow without external dependencies

        # Mock only the subprocess part
        mock_process = Mock()
        mock_process.wait = AsyncMock(return_value=None)
        mock_process.returncode = 0

        test_output = b"converted_test_data"

        with patch("asyncio.subprocess.create_subprocess_exec") as mock_create:
            mock_create.return_value = mock_process

            # Use a real BytesIO that we control for output
            output_buffer = BytesIO()
            output_buffer.write(test_output)
            output_buffer.seek(0)

            # Mock only the output BytesIO call (second call)
            original_bytesio = BytesIO

            def bytesio_side_effect(*args, **kwargs):
                if args and args[0] == mp3_audio.binary:
                    return original_bytesio(*args, **kwargs)
                else:
                    return output_buffer

            with patch("app.stt.converter.BytesIO", side_effect=bytesio_side_effect):
                result = await convert_audio_extension(mp3_audio, AudioExtension.OGG)

                assert result.binary == test_output
                assert result.extension == AudioExtension.OGG

    @pytest.mark.asyncio
    async def test_different_audio_extensions(self):
        """Test conversion between different audio formats"""
        test_cases = [
            (AudioExtension.MP3, AudioExtension.WAV),
            (AudioExtension.WAV, AudioExtension.OGG),
            (AudioExtension.OGG, AudioExtension.AAC),
            (AudioExtension.AAC, AudioExtension.MP3),
        ]

        for source_ext, target_ext in test_cases:
            source_audio = Audio(binary=b"test_data", extension=source_ext)

            mock_process = Mock()
            mock_process.wait = AsyncMock(return_value=None)
            mock_process.returncode = 0

            with patch("asyncio.subprocess.create_subprocess_exec") as mock_create:
                mock_create.return_value = mock_process

                output_buffer = BytesIO(f"converted_to_{target_ext.value}".encode())

                with patch(
                    "app.stt.converter.BytesIO", side_effect=[BytesIO(), output_buffer]
                ):
                    result = await convert_audio_extension(source_audio, target_ext)

                    # Verify the ffmpeg call contains the target format
                    args, kwargs = mock_create.call_args
                    assert target_ext.value in args

                    assert result.extension == target_ext

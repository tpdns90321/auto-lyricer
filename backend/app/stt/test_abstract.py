import pytest
import pytest_asyncio
from unittest.mock import patch

from .abstract import _AudioWorker, BackgroundRemover, SpeechToText
from .data import Audio, AudioExtension, Transcription
from ..shared.supported import Language, SubtitleExtension


class ConcreteAudioWorker(_AudioWorker):
    _supported_audio_extensions = (AudioExtension.MP3, AudioExtension.WAV)

    def __init__(self, config: dict):
        self.config = config


class ConcreteBackgroundRemover(BackgroundRemover):
    _supported_audio_extensions = (AudioExtension.MP3, AudioExtension.OGG)
    _output_audio_extension = AudioExtension.OGG

    def __init__(self, config: dict):
        self.config = config

    async def _remove_background(self, audio: Audio) -> Audio:
        return Audio(
            binary=b"processed_audio_data", extension=self._output_audio_extension
        )


class ConcreteSpeechToText(SpeechToText):
    _supported_audio_extensions = (AudioExtension.WAV, AudioExtension.MP3)
    _output_subtitle_extension = SubtitleExtension.SRT

    def __init__(self, config: dict):
        self.config = config

    async def _transcribe(
        self,
        audio: Audio,
        target_language: Language | None = None,
        prompt: str | None = None,
    ) -> Transcription:
        return Transcription(
            content="Hello world transcription",
            extension=self._output_subtitle_extension,
            language=target_language if target_language else None,
        )


@pytest.fixture
def mp3_audio():
    return Audio(binary=b"mp3_audio_data", extension=AudioExtension.MP3)


@pytest.fixture
def wav_audio():
    return Audio(binary=b"wav_audio_data", extension=AudioExtension.WAV)


@pytest.fixture
def aac_audio():
    return Audio(binary=b"aac_audio_data", extension=AudioExtension.AAC)


@pytest_asyncio.fixture
async def audio_worker():
    return ConcreteAudioWorker({})


@pytest_asyncio.fixture
async def background_remover():
    return ConcreteBackgroundRemover({})


@pytest_asyncio.fixture
async def speech_to_text():
    return ConcreteSpeechToText({})


class TestAudioWorker:
    def test_abstract_class_cannot_be_instantiated(self):
        with pytest.raises(TypeError):
            _AudioWorker({})  # type: ignore

    def test_supported_audio_extensions_property(
        self, audio_worker: ConcreteAudioWorker
    ):
        assert audio_worker.supported_audio_extensions == (
            AudioExtension.MP3,
            AudioExtension.WAV,
        )

    @pytest.mark.asyncio
    async def test_convert_audio_with_supported_format(
        self, audio_worker: ConcreteAudioWorker, mp3_audio: Audio
    ):
        result = await audio_worker._convert_audio(mp3_audio)
        assert result == mp3_audio

    @pytest.mark.asyncio
    async def test_convert_audio_with_unsupported_format(
        self, audio_worker: ConcreteAudioWorker, aac_audio: Audio
    ):
        with patch("app.stt.abstract.convert_audio_extension") as mock_convert:
            expected_audio = Audio(
                binary=b"converted_data", extension=AudioExtension.MP3
            )
            mock_convert.return_value = expected_audio

            result = await audio_worker._convert_audio(aac_audio)

            mock_convert.assert_called_once_with(
                origin_audio=aac_audio, target_extension=AudioExtension.MP3
            )
            assert result == expected_audio


class TestBackgroundRemover:
    def test_abstract_class_cannot_be_instantiated(self):
        with pytest.raises(TypeError):
            BackgroundRemover({})  # type: ignore

    def test_output_audio_extension_property(
        self, background_remover: ConcreteBackgroundRemover
    ):
        assert background_remover.output_audio_extension == AudioExtension.OGG

    @pytest.mark.asyncio
    async def test_remove_background_with_supported_format(
        self, background_remover: ConcreteBackgroundRemover, mp3_audio: Audio
    ):
        result = await background_remover.remove_background(mp3_audio)

        assert result.binary == b"processed_audio_data"
        assert result.extension == AudioExtension.OGG

    @pytest.mark.asyncio
    async def test_remove_background_with_unsupported_format(
        self, background_remover: ConcreteBackgroundRemover, aac_audio: Audio
    ):
        with patch("app.stt.abstract.convert_audio_extension") as mock_convert:
            converted_audio = Audio(
                binary=b"converted_mp3_data", extension=AudioExtension.MP3
            )
            mock_convert.return_value = converted_audio

            result = await background_remover.remove_background(aac_audio)

            mock_convert.assert_called_once_with(
                origin_audio=aac_audio, target_extension=AudioExtension.MP3
            )
            assert result.binary == b"processed_audio_data"
            assert result.extension == AudioExtension.OGG


class TestSpeechToText:
    def test_abstract_class_cannot_be_instantiated(self):
        with pytest.raises(TypeError):
            SpeechToText({})  # type: ignore

    def test_output_subtitle_extension_property(
        self, speech_to_text: ConcreteSpeechToText
    ):
        assert speech_to_text.output_subtitle_extension == SubtitleExtension.SRT

    @pytest.mark.asyncio
    async def test_transcribe_with_supported_format(
        self, speech_to_text: ConcreteSpeechToText, wav_audio: Audio
    ):
        result = await speech_to_text.transcribe(wav_audio)

        assert result.content == "Hello world transcription"
        assert result.extension == SubtitleExtension.SRT

    @pytest.mark.asyncio
    async def test_transcribe_with_unsupported_format(
        self, speech_to_text: ConcreteSpeechToText, aac_audio: Audio
    ):
        with patch("app.stt.abstract.convert_audio_extension") as mock_convert:
            converted_audio = Audio(
                binary=b"converted_wav_data", extension=AudioExtension.WAV
            )
            mock_convert.return_value = converted_audio

            result = await speech_to_text.transcribe(aac_audio)

            mock_convert.assert_called_once_with(
                origin_audio=aac_audio, target_extension=AudioExtension.WAV
            )
            assert result.content == "Hello world transcription"
            assert result.extension == SubtitleExtension.SRT

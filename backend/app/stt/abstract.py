from .data import Audio, AudioExtension, Transcription
from .converter import convert_audio_extension
from ..shared.supported import SubtitleExtension

from abc import ABC, abstractmethod


class _AudioWorker(ABC):
    """Abstract base class for audio processing services."""

    _supported_audio_extensions: tuple[AudioExtension, ...]

    @abstractmethod
    def __init__(self, config: dict):
        """Initialize the background remover service with the given configuration.

        :param config: Configuration dictionary for the background remover service.
        """
        pass

    @property
    def supported_audio_extensions(self) -> tuple[AudioExtension, ...]:
        """Get the list of audio extensions supported by the background remover service.

        :return: A list of supported audio extensions.
        """
        return self._supported_audio_extensions

    async def _convert_audio(self, audio: Audio) -> Audio:
        """Convert the given audio data to a supported audio format if necessary.

        :param audio: The audio data to process.
        :return: The processed audio data.
        """
        target_audio: Audio = audio
        if audio.extension not in self.supported_audio_extensions:
            target_audio = await convert_audio_extension(
                origin_audio=audio, target_extension=self.supported_audio_extensions[0]
            )

        return target_audio


class BackgroundRemover(_AudioWorker):
    _output_audio_extension: AudioExtension

    @abstractmethod
    async def _remove_background(self, audio: Audio) -> Audio:
        """Remove the background noise from the given audio.

        :param audio: The audio data from which to remove background noise.
        :return: The audio data with background noise removed.
        """
        pass

    async def remove_background(self, audio: Audio) -> Audio:
        """Remove the background noise from the given audio.

        :param audio: The audio data from which to remove background noise.
        :return: The audio data with background noise removed.
        """
        target_audio: Audio = await self._convert_audio(audio)
        return await self._remove_background(target_audio)

    @property
    def output_audio_extension(self) -> AudioExtension:
        """Get the output audio extension after background removal.

        :return: The output audio extension.
        """
        return self._output_audio_extension


class SpeechToText(_AudioWorker):
    _output_subtitle_extension: SubtitleExtension

    @abstractmethod
    async def _transcribe(self, audio: Audio) -> Transcription:
        """Transcribe the given audio to text.

        :param audio: The audio data to transcribe.
        :return: The Transcription Object with transcribed text.
        """
        pass

    async def transcribe(self, audio: Audio) -> Transcription:
        """Transcribe the given audio to text.

        :param audio: The audio data to transcribe.
        :return: The Transcription Object with transcribed text.
        """
        target_audio: Audio = await self._convert_audio(audio)
        return await self._transcribe(target_audio)

    @property
    def output_subtitle_extension(self) -> SubtitleExtension:
        """Get the output audio extension after transcription.

        :return: The output audio extension.
        """
        return self._output_subtitle_extension

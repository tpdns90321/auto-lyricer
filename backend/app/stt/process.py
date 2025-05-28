from .data import Audio, Transcription
from .abstract import BackgroundRemover, SpeechToText


class Transcribe:
    def __init__(self, background_remover: BackgroundRemover, stt: SpeechToText):
        """
        Initialize the speech-to-text process with background remover and STT service.

        :param background_remover: An instance of BackgroundRemoverAbstract.
        :param stt: An instance of SpeechToTextAbstract.
        """
        self._background_remover = background_remover
        self._speech_to_text = stt

    async def process(self, audio: Audio) -> Transcription:
        only_vocal_audio = await self._background_remover.remove_background(audio)
        return await self._speech_to_text.transcribe(only_vocal_audio)

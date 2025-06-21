from ...shared.supported import Language, SubtitleExtension
from ..abstract import SpeechToText
from ..data import Audio, AudioExtension, Transcription

from dataclasses import dataclass, field
from aiohttp import ClientSession
from base64 import b64encode


@dataclass(frozen=True)
class RunpodWhisperConfig:
    api_key: str
    endpoint: str
    model: str
    temperature: float = field(default=0.0)
    best_of: int = field(default=5)
    beam_size: int = field(default=5)
    patience: float | None = field(default=None)
    length_penalty: float | None = field(default=None)
    suppress_tokens: str = field(default="-1")
    condition_on_previous_text: bool = field(default=True)
    temperature_increment_on_fallback: float = field(default=0.2)
    compression_ratio_threshold: float = field(default=2.4)
    logprob_threshold: float = field(default=-1.0)
    no_speech_threshold: float = field(default=0.6)


@dataclass(frozen=True)
class RunpodWhisperResponse:
    segments: list[dict[str, str]]
    transcription: str
    model: str
    detected_language: str | None = field(default=None)
    translation: None = field(default=None)
    device: str = field(default="cuda")


class RunpodWhisper(SpeechToText):
    _supported_audio_extensions = (
        AudioExtension.MP3,
        AudioExtension.OGG,
        AudioExtension.WAV,
    )
    _output_subtitle_extension = SubtitleExtension.VTT

    def __init__(self, config: dict):
        """Initialize RunpodWhisper with configuration.

        Args:
            config: Dictionary containing api_key, endpoint, and other parameters.

        Raises:
            ValueError: If required configuration keys are missing or empty.
        """
        self._config = RunpodWhisperConfig(**config)

        if not self._config.api_key:
            raise ValueError("api_key must be provided in the configuration.")
        if not self._config.endpoint:
            raise ValueError("endpoint must be provided in the configuration.")
        if not self._config.model:
            raise ValueError("model must be provided in the configuration.")

        self._session = ClientSession(
            base_url=self._config.endpoint,
            headers={
                "Content-Type": "application/json",
                "Authorization": self._config.api_key,
            },
        )

    async def _transcribe(
        self,
        audio: Audio,
        target_language: Language | None = None,
        prompt: str | None = None,
    ) -> Transcription:
        config = self._config
        input = {
            "audio_base64": b64encode(audio.binary).decode("utf-8"),
            "model": config.model,
            "language": target_language.value if target_language else None,
            "transcription": "vtt",
            "temperature": config.temperature,
            "best_of": config.best_of,
            "beam_size": config.beam_size,
            "patience": config.patience,
            "length_penalty": config.length_penalty,
            "suppress_tokens": config.suppress_tokens,
            "condition_on_previous_text": config.condition_on_previous_text,
            "compression_ratio_threshold": config.compression_ratio_threshold,
            "logprob_threshold": config.logprob_threshold,
            "no_speech_threshold": config.no_speech_threshold,
            "prompt": prompt,
        }
        # due to linting issues, we need to set this separately
        temperature_increment_on_fallback = config.temperature_increment_on_fallback
        input["temperature_increment_on_fallback"] = temperature_increment_on_fallback

        response = await self._session.post(
            "/runsync",
            json={"input": input},
        )

        if response.status != 200:
            raise RuntimeError(f"Failed to transcribe audio: {response.status}")

        data = RunpodWhisperResponse(**(await response.json())["output"])
        language = target_language
        try:
            if not target_language:
                Language(data.detected_language)
        except ValueError:
            language = None

        return Transcription(
            content=data.transcription,
            extension=self.output_subtitle_extension,
            language=language,
        )

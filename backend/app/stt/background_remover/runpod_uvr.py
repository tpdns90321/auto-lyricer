from ..abstract import BackgroundRemover
from ...shared.data import Audio, AudioExtension

from dataclasses import dataclass
from aiohttp import ClientSession
from base64 import b64encode, b64decode


@dataclass(frozen=True)
class RunpodUVRConfig:
    api_key: str
    endpoint: str


@dataclass(frozen=True)
class RunpodUVRResponse:
    output: dict[str, str]


class RunpodUVR(BackgroundRemover):
    _supported_audio_extensions = (
        AudioExtension.MP3,
        AudioExtension.OGG,
        AudioExtension.WAV,
    )
    _output_audio_extension = AudioExtension.OGG

    def __init__(self, config: dict):
        """Initialize RunpodUVR with configuration.

        Args:
            config: Dictionary containing api_key and endpoint.

        Raises:
            ValueError: If required configuration keys are missing or empty.
        """
        self._config = RunpodUVRConfig(**config)

        if not self._config.api_key:
            raise ValueError("api_key must be provided in the configuration.")
        if not self._config.endpoint:
            raise ValueError("endpoint must be provided in the configuration.")

        self._session = ClientSession(
            base_url=self._config.endpoint,
            headers={
                "Content-Type": "application/json",
                "Authorization": self._config.api_key,
            },
        )

    async def _remove_background(self, audio: Audio) -> Audio:
        response = await self._session.post(
            "/runsync",
            json={
                "input": {
                    "audio": b64encode(audio.binary).decode("utf-8"),
                    "parts": ["vocals"],
                },
            },
        )
        if response.status != 200:
            raise RuntimeError(f"Runpod UVR API returned status {response.status}")

        body: RunpodUVRResponse = RunpodUVRResponse(**await response.json())
        return Audio(
            binary=b64decode(body.output["vocals"]),
            extension=AudioExtension.OGG,
        )

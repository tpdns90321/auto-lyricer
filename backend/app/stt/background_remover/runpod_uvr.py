from ..abstract import BackgroundRemover
from ..data import Audio, AudioExtension

from dataclasses import dataclass
from aiohttp import ClientSession
from base64 import b64encode, b64decode


@dataclass(frozen=True)
class RunpodUVRConfig:
    RUNPOD_API_KEY: str
    RUNPOD_UVR_ENDPOINT: str


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
            config: Dictionary containing RUNPOD_API_KEY and RUNPOD_UVR_ENDPOINT.

        Raises:
            ValueError: If required configuration keys are missing or empty.
        """
        self._config = RunpodUVRConfig(**config)

        if not self._config.RUNPOD_API_KEY:
            raise ValueError("RUNPOD_API_KEY must be provided in the configuration.")
        if not self._config.RUNPOD_UVR_ENDPOINT:
            raise ValueError(
                "RUNPOD_UVR_ENDPOINT must be provided in the configuration."
            )

        self._session = ClientSession(
            base_url=self._config.RUNPOD_UVR_ENDPOINT,
            headers={
                "Content-Type": "application/json",
                "Authorization": self._config.RUNPOD_API_KEY,
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

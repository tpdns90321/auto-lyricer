from .data import Audio, AudioExtension

import asyncio
from io import BytesIO


async def convert_audio_extension(
    origin_audio: Audio, target_extension: AudioExtension
) -> Audio:
    """Convert audio binary data to the specified audio extension.

    :param origin_binary: The original audio binary data.
    :param target_extension: The target audio extension to convert to.
    :return: Converted audio binary data.
    """
    origin_binary = origin_audio.binary
    output_buffer = BytesIO()
    process = await asyncio.subprocess.create_subprocess_exec(
        "ffmpeg",
        "-i",
        "-",  # Input from stdin
        "-f",
        target_extension.value,  # Output format
        "-",  # Output to stdout
        stdin=BytesIO(origin_binary),  # Provide input binary data
        stdout=output_buffer,
    )
    await process.wait()
    if process.returncode != 0:
        raise RuntimeError("FFmpeg process did not complete successfully.")
    output_buffer.seek(0)

    return Audio(binary=output_buffer.read(), extension=target_extension)

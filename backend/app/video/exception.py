from enum import Enum


class UnknownError(Exception):
    def __init__(self, contain_exception: Exception):
        """Initialize UnknownError.

        Args:
            contain_exception: The original exception that was caught.
        """
        super().__init__("Unknown exception: " + str(contain_exception))


class NotFoundThings(Enum):
    video = "video"
    video_id = "video_id"


class NotFoundError(Exception):
    def __init__(self, thing: NotFoundThings):
        """Initialize NotFoundError.

        Args:
            thing: The type of thing that was not found.
        """
        super().__init__("Not found " + str(thing))


class UnsupportedPlatformError(Exception):
    def __init__(self, platform: str):
        """Initialize UnsupportedPlatformError.

        Args:
            platform: Name of the unsupported platform.
        """
        super().__init__("Unsupported platform: " + platform)

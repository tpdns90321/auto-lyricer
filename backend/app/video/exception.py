from enum import Enum


class UnknownException(Exception):
    def __init__(self, contain_exception: Exception):
        super().__init__("Unknown exception: " + str(contain_exception))


class NotFoundThings(Enum):
    video = "video"


class NotFoundException(Exception):
    def __init__(self, thing: NotFoundThings):
        super().__init__("Not found " + str(thing))


class UnsupportedPlatformException(Exception):
    def __init__(self, platform: str):
        super().__init__("Unsupported platform: " + platform)

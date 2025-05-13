from .supported import Platform


class UnsupportedPlatformException(Exception):
    def __init__(self, platform: Platform):
        super().__init__(f"Unsupported platform: {platform}")
        self.platform = platform


class UnknownException(Exception):
    def __init__(self, exception: Exception):
        super().__init__(f"Unknown exception: {exception}")
        self.exception = exception

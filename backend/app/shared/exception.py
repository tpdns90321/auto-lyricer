class UnsupportedPlatformException(Exception):
    def __init__(self, platform_name: str):
        super().__init__(f"Unsupported platform: {platform_name}")
        self.platform = platform_name


class UnknownException(Exception):
    def __init__(self, exception: Exception):
        super().__init__(f"Unknown exception: {exception}")
        self.exception = exception

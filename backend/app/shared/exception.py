class UnsupportedPlatformError(Exception):
    def __init__(self, platform_name: str):
        """Initialize UnsupportedPlatformError.

        Args:
            platform_name: Name of the unsupported platform.
        """
        super().__init__(f"Unsupported platform: {platform_name}")
        self.platform = platform_name


class UnknownError(Exception):
    def __init__(self, exception: Exception):
        """Initialize UnknownError.

        Args:
            exception: The original exception that was caught.
        """
        super().__init__(f"Unknown exception: {exception}")
        self.exception = exception

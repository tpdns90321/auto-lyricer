class VideoExtractError(Exception):
    def __init__(self, message: str):
        """Initialize VideoExtractError with message.

        Args:
            message: Error message describing the extraction failure.
        """
        self.message = message
        super().__init__(self.message)

from enum import Enum


class NotFoundThing(str, Enum):
    TranscriptionInstance = "transcription instance"
    VideoInstance = "video instance"


class NotFoundThingError(Exception):
    def __init__(self, thing: NotFoundThing):
        """Initialize NotFoundThingError.

        Args:
            thing: The type of thing that was not found.
        """
        self.thing = thing
        super().__init__(f"Not found {thing}")

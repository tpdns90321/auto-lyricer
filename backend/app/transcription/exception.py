from enum import Enum


class NotFoundThing(str, Enum):
    TranscriptionInstance = "transcription instance"
    VideoInstance = "video instance"


class NotFoundThingException(Exception):
    def __init__(self, thing: NotFoundThing):
        self.thing = thing
        super().__init__(f"Not found {thing}")

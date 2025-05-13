from enum import Enum


class NotFoundThing(Enum):
    VideoInstance = "Video instance"


class NotFoundThingException(Exception):
    def __init__(self, thing: NotFoundThing):
        self.thing = thing
        super().__init__(f"{thing.value} not found")

from enum import Enum

class OutputMarkers(Enum):
    NO_FIELD = "ENUM.NO_FIELD"

    def __str__(self):
        return self.value

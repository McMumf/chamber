from enum import Enum

class OperatingMode(str, Enum):
    HEATING = "Heating"
    COOLING = "Cooling"
    RESTING = "Resting"

    def __str__(self) -> str:
        return self.value

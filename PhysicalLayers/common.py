from enum import Enum

class CommunicatorAppMessageTypes(Enum):
    LOCATION = "LOCATION"
    ISLOCATION = "ISLOCATION"
    ISDISTANCE = "ISDISTANCE"
    TEXTMESSAGE = "TEXTMESSAGE"

# define your own message types
class GPSHandlerAppMessageTypes(Enum):
    LOCATION = "LOCATION"
    DISTANCE = "DISTANCE"
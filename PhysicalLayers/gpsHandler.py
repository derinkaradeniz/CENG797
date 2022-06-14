import time
import random

from adhoccomputing.GenericModel import GenericModel
from adhoccomputing.Generics import *
import pickle

# define your own message types
class GPSHandlerAppMessageTypes(Enum):
    LOCATION = "LOCATION"
    DISTANCE = "DISTANCE"

# define your own message header structure
class GPSHandlerAppMessageHeader(GenericMessageHeader):
    pass


class GPSHandlerAppEventTypes(Enum):
    pass
    

#class GPSHandlerAppConfig:
#    def __init__(self, framerate):
#        self.framerate = framerate

class GPSHandlerApp(GenericModel):
    myLocation = [0]*2
    def on_init(self, eventobj: Event):
        self.counter = 0       
    
    def __init__(self, componentname, componentinstancenumber, context=None, configurationparameters=None, num_worker_threads=1, topology=None):
        super().__init__(componentname, componentinstancenumber, context, configurationparameters, num_worker_threads, topology)

        self.myLocation[0] = random.random() * 360 - 180
        self.myLocation[1] = random.random() * 180 - 90
        logger.applog(f"My Location {str(self.myLocation[0])} , {str(self.myLocation[1])}")

    def on_message_from_peer(self, eventobj: Event):
        #evt = Event(self, EventTypes.MFRT, eventobj.eventcontent)
        #hesaplama yap
        if eventobj.eventcontent.header.messagetype == "ISLOCATION":  
            header = GPSHandlerAppMessageHeader(GPSHandlerAppMessageTypes.LOCATION, self.componentinstancenumber, eventobj.eventcontent.header.messagefrom)     
            payload = self.myLocation
            message = GenericMessage(header, payload)
            evt = Event(self, EventTypes.MFRP, message)
            self.send_peer(evt)

        elif eventobj.eventcontent.header.messagetype == "ISDISTANCE":
            nodeLocation = eventobj.eventContent.payload
            distance = sqrt((self.myLocation[0] - nodeLocation[0])**2 + (self.myLocation[1] - nodeLocation[1])**2)

            header = GPSHandlerAppMessageHeader(GPSHandlerAppMessageTypes.DISTANCE, self.componentinstancenumber, eventobj.eventcontent.header.messagefrom)     
            payload = distance
            message = GenericMessage(header, payload)
            evt = Event(self, EventTypes.MFRP, message) 
            self.send_peer(evt)
            logger.applog(f"{self.componentname}.{self.componentinstancenumber}: My distance from {eventobj.eventcontent.header.messagefrom} is {str(distance)}")
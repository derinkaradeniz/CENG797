import time
import random

from adhoccomputing.GenericModel import GenericModel
from adhoccomputing.Generics import *
import pickle

from lorem import *

# define your own message types
class CommunicatorAppMessageTypes(Enum):
    LOCATION = "LOCATION"
    ISLOCATION = "ISLOCATION"
    DISTANCE = "ISDISTANCE"
    TEXTMESSAGE = "TEXTMESSAGE"

# define your own message header structure
class CommunicatorAppMessageHeader(GenericMessageHeader):
    pass

class CommunicatorAppEventTypes(Enum):    
    STARTGPSREQ = "startspsreq"

class CommunicatorApp(GenericModel):
    myLocation = [0]*2
    def on_init(self, eventobj: Event):
        self.counter = 0       
    
    def __init__(self, componentname, componentinstancenumber, context=None, configurationparameters=None, num_worker_threads=1, topology=None):
        super().__init__(componentname, componentinstancenumber, context, configurationparameters, num_worker_threads, topology)
        self.eventhandlers[CommunicatorAppEventTypes.STARTGPSREQ] = self.on_startgpsreq

     def on_message_from_bottom(self, eventobj: Event):
        if eventobj.eventcontent.hdr.messagetype == "LOCATION"
            hdr = CommunicatorAppMessageHeader(CommunicatorAppMessageHeader.ISDISTANCE, eventobj.eventcontent.hdr.messagefrom, eventobj.eventcontent.hdr.messageto)     
            payload = eventobj.eventcontent.payload
            message = GenericMessage(hdr, payload) 
            evt = Event(self, EventTypes.MFRP, message)
            self.send_peer(evt)

    def on_message_from_peer(self, eventobj: Event):
        if eventobj.eventcontent.hdr.messagetype == "LOCATION"
            hdr = CommunicatorAppMessageHeader(CommunicatorAppMessageHeader.LOCATION, self.componentinstancenumber, eventobj.eventcontent.hdr.messageto)     
            payload = eventobj.eventcontent.payload
            message = GenericMessage(hdr, payload) 
            evt = Event(self, EventTypes.MFRT, message)
            self.send_down(evt)
        elif eventobj.eventcontent.hdr.messagetype == "DISTANCE":
            distance = eventobj.eventcontent.payload
            if payload < 10:
                hdr = CommunicatorAppMessageHeader(CommunicatorAppMessageHeader.TEXTMESSAGE, eventobj.eventcontent.hdr.messagefrom, eventobj.eventcontent.hdr.messageto)     
                payload = loremIpsum
                message = GenericMessage(hdr, payload) 
                evt = Event(self, EventTypes.MFRP, message)
                self.send_peer(evt)


    def on_startgpsreq(self, eventobj: Event):
        hdr = CommunicatorAppMessageTypes(GPSHandlerAppMessageTypes.ISLOCATION, self.componentinstancenumber, self.componentinstancenumber)     
        payload = "location request"
        message = GenericMessage(hdr, payload)
        evt = Event(self, EventTypes.MFRP, message)
        self.send_peer(evt)


import time
import random

from adhoccomputing.GenericModel import GenericModel
from adhoccomputing.Generics import *
from common import *
#from gpsHandler import GPSHandlerAppMessageTypes, CommunicatorAppMessageTypes
#import pickle

from lorem import *

#class GPSHandlerAppMessageTypes(Enum):
#    LOCATION = "LOCATION"
#    DISTANCE = "DISTANCE"

# define your own message types
#class CommunicatorAppMessageTypes(Enum):
#    LOCATION = "LOCATION"
#    ISLOCATION = "ISLOCATION"
#    ISDISTANCE = "ISDISTANCE"
#    TEXTMESSAGE = "TEXTMESSAGE"

# define your own message header structure
class CommunicatorAppMessageHeader(GenericMessageHeader):
    pass

class CommunicatorAppEventTypes(Enum):    
    STARTGPSREQ = "startspsreq"

class CommunicatorApp(GenericModel):
    myLocation = [0]*2
    def on_init(self, eventobj: Event):
        #print("comm: on init")
        self.counter = 0       
    
    def __init__(self, componentname, componentinstancenumber, context=None, configurationparameters=None, num_worker_threads=1, topology=None):
        #print("comm: init")
        super().__init__(componentname, componentinstancenumber, context, configurationparameters, num_worker_threads, topology)
        self.eventhandlers[CommunicatorAppEventTypes.STARTGPSREQ] = self.on_startgpsreq

    def on_message_from_bottom(self, eventobj: Event):
        #print("comm: from bottom")
        if eventobj.eventcontent.header.messagefrom != self.componentinstancenumber:
            if eventobj.eventcontent.header.messagetype == CommunicatorAppMessageTypes.LOCATION:
                #print("comm: from bottom: location")
                header = CommunicatorAppMessageHeader(CommunicatorAppMessageTypes.ISLOCATIONBOTTOM, eventobj.eventcontent.header.messagefrom, eventobj.eventcontent.header.messageto)
                payload = eventobj.eventcontent.payload
                message = GenericMessage(header, payload) 
                evt = Event(self, EventTypes.MFRP, message)
                self.send_peer(evt)
                #header = CommunicatorAppMessageHeader(CommunicatorAppMessageTypes.ISDISTANCE, eventobj.eventcontent.header.messagefrom, eventobj.eventcontent.header.messageto)     
                #payload = eventobj.eventcontent.payload
                #message = GenericMessage(header, payload) 
                #evt = Event(self, EventTypes.MFRP, message)
                #self.send_peer(evt)
            elif eventobj.eventcontent.header.messagetype == CommunicatorAppMessageTypes.LOCATIONBOTTOM:
                #print("comm: from bottom: locationbottom")
                header = CommunicatorAppMessageHeader(CommunicatorAppMessageTypes.ISDISTANCE, eventobj.eventcontent.header.messagefrom, eventobj.eventcontent.header.messageto)     
                payload = eventobj.eventcontent.payload
                message = GenericMessage(header, payload) 
                evt = Event(self, EventTypes.MFRP, message)
                self.send_peer(evt)
            elif eventobj.eventcontent.header.messagetype == CommunicatorAppMessageTypes.TEXTMESSAGE:
                print(f"{self.componentname}.{self.componentinstancenumber}: Text message received from {eventobj.eventcontent.header.messagefrom}: {eventobj.eventcontent.payload.rsplit(" ",1)}")
        else:
            pass

    def on_message_from_peer(self, eventobj: Event):        
        #print("comm: from peer")
        if eventobj.eventcontent.header.messagetype == GPSHandlerAppMessageTypes.LOCATION:
            #print("comm: from peer: location")
            header = CommunicatorAppMessageHeader(CommunicatorAppMessageTypes.LOCATION, self.componentinstancenumber,MessageDestinationIdentifiers.LINKLAYERBROADCAST)
            #MessageDestinationIdentifiers.LINKLAYERBROADCAST   
            payload = eventobj.eventcontent.payload
            message = GenericMessage(header, payload) 
            evt = Event(self, EventTypes.MFRT, message)
            self.send_down(evt)
        elif eventobj.eventcontent.header.messagetype == GPSHandlerAppMessageTypes.LOCATIONBOTTOM:
            #print("comm: from peer: locationbottom")
            header = CommunicatorAppMessageHeader(CommunicatorAppMessageTypes.LOCATIONBOTTOM, self.componentinstancenumber, eventobj.eventcontent.header.messageto)     
            payload = eventobj.eventcontent.payload
            message = GenericMessage(header, payload) 
            evt = Event(self, EventTypes.MFRT, message)
            self.send_down(evt)            
            #self.send_down(eventobj)
        elif eventobj.eventcontent.header.messagetype == GPSHandlerAppMessageTypes.DISTANCE:
            #print("comm: from peer: distance")
            distance = eventobj.eventcontent.payload
            #print(f"Distance at comm: {str(distance)}")
            if distance < 500:
                header = CommunicatorAppMessageHeader(CommunicatorAppMessageTypes.TEXTMESSAGE, eventobj.eventcontent.header.messagefrom, eventobj.eventcontent.header.messageto)     
                payload = loremIpsum2
                message = GenericMessage(header, payload) 
                evt = Event(self, EventTypes.MFRT, message)
                self.send_down(evt)


    def on_startgpsreq(self, eventobj: Event):
        #print("on_startgpsreq")
        header = CommunicatorAppMessageHeader(CommunicatorAppMessageTypes.ISLOCATION, self.componentinstancenumber, self.componentinstancenumber)     
        payload = "location request"
        message = GenericMessage(header, payload)
        evt = Event(self, EventTypes.MFRP, message)
        self.send_peer(evt)


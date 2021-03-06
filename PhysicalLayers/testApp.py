import time
import random
from pathlib import Path

from adhoccomputing.GenericModel import GenericModel
from adhoccomputing.Generics import *
from common import *
from lorem import *

class TestAppMessageHeader(GenericMessageHeader):
    pass

class TestAppEventTypes(Enum):    
    STARTREQ = "startreq"

class TestAppMessageTypes(Enum):
    BURST = "burst"
    ACK = "ack"

class TestApp(GenericModel):
    myLocation = [0]*2
    seqCount = 0
    def on_init(self, eventobj: Event):
        #print("comm: on init")
        self.counter = 0       
    
    def __init__(self, componentname, componentinstancenumber, context=None, configurationparameters=None, num_worker_threads=1, topology=None):
        #print("comm: init")
        super().__init__(componentname, componentinstancenumber, context, configurationparameters, num_worker_threads, topology)
        self.eventhandlers[TestAppEventTypes.STARTREQ] = self.on_startreq

    def on_message_from_bottom(self, eventobj: Event):
        #print("comm: from bottom")
        if (eventobj.eventcontent.header.messagefrom != self.componentinstancenumber) and (eventobj.eventcontent.header.messageto == self.componentinstancenumber):
            if eventobj.eventcontent.header.messagetype == TestAppMessageTypes.BURST:
                print(f"Node {self.componentinstancenumber}: received {eventobj.eventcontent.header.sequencenumber} from Node {eventobj.eventcontent.header.messagefrom}.")
                header = TestAppMessageHeader(TestAppMessageTypes.ACK, self.componentinstancenumber, eventobj.eventcontent.header.messagefrom, sequencenumber=eventobj.eventcontent.header.sequencenumber )
                payload = bytearray(1)
                message = GenericMessage(header, payload)
                evt = Event(self, EventTypes.MFRT, message)
                self.send_down(evt)
            elif eventobj.eventcontent.header.messagetype == TestAppMessageTypes.ACK:
                print(f"Node {self.componentinstancenumber}: ACK received {eventobj.eventcontent.header.sequencenumber} from Node {eventobj.eventcontent.header.messagefrom}.")
        else:
            pass

    def on_message_from_peer(self, eventobj: Event):        
        #print("comm: from peer")
        pass
        

    def on_startreq(self, eventobj: Event):
        #print("on_startreq")
        #header = TestAppMessageHeader(TestAppMessageTypes.BURST, self.componentinstancenumber, 0)
        #payload = bytearray([1] * 64)
        #message = GenericMessage(header, payload)
        #evt = Event(self, EventTypes.MFRT, message)

        #for i in range(20):
        #    evt.eventcontent.header.sequencenumber = i + 1
        #    self.send_down(evt)
        #    print(f"Sent message seq: {evt.eventcontent.header.sequencenumber}")

        #for i in range(100):
        #    header = TestAppMessageHeader(TestAppMessageTypes.BURST, self.componentinstancenumber, 0,sequencenumber= i + 1)
        #    payload = bytearray([1] * 64)
        #    message = GenericMessage(header, payload)
        #    evt = Event(self, EventTypes.MFRT, message)
        #    self.send_down(evt)
        #    #print(f"Sent message seq: {evt.eventcontent.header.sequencenumber}")

        self.seqCount = self.seqCount + 1
        header = TestAppMessageHeader(TestAppMessageTypes.BURST, self.componentinstancenumber, 2,sequencenumber= self.seqCount)
        payload = bytearray([1] * 64)
        message = GenericMessage(header, payload)
        evt = Event(self, EventTypes.MFRT, message)
        self.send_down(evt)
        #print(f"Sent message seq: {evt.eventcontent.header.sequencenumber}")
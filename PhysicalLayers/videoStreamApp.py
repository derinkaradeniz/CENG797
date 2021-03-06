import os
import sys
import time, random, math
from enum import Enum
from pickle import FALSE


from csmaPlain import CsmaPlain, MacCsmaPPersistentConfigurationParameters
from adhoccomputing.GenericModel import GenericModel
from adhoccomputing.Generics import Event, EventTypes, ConnectorTypes, GenericMessageHeader,GenericMessage
from adhoccomputing.Experimentation.Topology import Topology
from adhoccomputing.Networking.PhysicalLayer.UsrpB210OfdmFlexFramePhy import  UsrpB210OfdmFlexFramePhy

from adhoccomputing.Networking.ApplicationLayer.OpenCVVideoStreamingApp import  OpenCVVideoStreamingApp, OpenCVVideoStreamingAppConfig
#from adhoccomputing.Networking.MacProtocol.CSMA import MacCsmaPPersistent, MacCsmaPPersistentConfigurationParameters

#registry = ComponentRegistry()
#from ahc.Channels.Channels import FIFOBroadcastPerfectChannel
#from ahc.EttusUsrp.UhdUtils import AhcUhdUtils

#framers = FramerObjects()


# define your own message types
class ApplicationLayerMessageTypes(Enum):
    BROADCAST = "BROADCAST"
    VIDEO = "VIDEO"


# define your own message header structure
class ApplicationLayerMessageHeader(GenericMessageHeader):
    pass


class VideoStreamingApplicationLayerEventTypes(Enum):
    STARTBROADCAST = "startbroadcast"
    STARTSTREAMING = "startstreaming"

class VideoStreamingAppConfig(OpenCVVideoStreamingAppConfig):
    def __init__(self, framerate):
        self.framerate = framerate


class VideoStreamingApplicationLayer(OpenCVVideoStreamingApp):
    

    def on_init(self, eventobj: Event):
        self.counter = 0
    
    def __init__(self, componentname, componentinstancenumber, context=None, configurationparameters=None, num_worker_threads=1, topology=None):
        super().__init__(componentname, componentinstancenumber, context, configurationparameters, num_worker_threads, topology)
        self.eventhandlers[VideoStreamingApplicationLayerEventTypes.STARTBROADCAST] = self.on_startbroadcast

    def on_message_from_top(self, eventobj: Event):
    # print(f"I am {self.componentname}.{self.componentinstancenumber},sending down eventcontent={eventobj.eventcontent}\n")
        self.send_down(Event(self, EventTypes.MFRT, eventobj.eventcontent))
    
    def on_message_from_bottom(self, eventobj: Event):
        evt = Event(self, EventTypes.MFRT, eventobj.eventcontent)
        print(f"I am Node.{self.componentinstancenumber}, received from Node.{eventobj.eventcontent.header.messagefrom} a message: {eventobj.eventcontent.payload}")    
        if self.componentinstancenumber == 1:
            evt.eventcontent.header.messageto = 0
            evt.eventcontent.header.messagefrom = 1
        else:
            evt.eventcontent.header.messageto = 1
            evt.eventcontent.header.messagefrom = 0
        evt.eventcontent.payload = eventobj.eventcontent.payload
        #print(f"I am {self.componentname}.{self.componentinstancenumber}, sending down eventcontent={eventobj.eventcontent.payload}\n")
        self.send_down(evt)  # PINGPONG
    
    def on_startbroadcast(self, eventobj: Event):
        #if self.componentinstancenumber == 1:
        #   hdr = ApplicationLayerMessageHeader(ApplicationLayerMessageTypes.BROADCAST, 1, 0)
        #else:
        #    hdr = ApplicationLayerMessageHeader(ApplicationLayerMessageTypes.BROADCAST, 0, 1)
        hdr = ApplicationLayerMessageHeader(ApplicationLayerMessageTypes.BROADCAST, self.componentinstancenumber, 1)
        self.counter = self.counter + 1
        
        payload = "BMSG-" + str(self.counter)
        broadcastmessage = GenericMessage(hdr, payload)
        evt = Event(self, EventTypes.MFRT, broadcastmessage)
        # time.sleep(3)
        self.send_down(evt)
        #print("Starting broadcast")
    
         
class UsrpNode(GenericModel):
    counter = 0
    def on_init(self, eventobj: Event):
        pass
    
    def __init__(self, componentname, componentinstancenumber, context=None, configurationparameters=None, num_worker_threads=1, topology=None):
        super().__init__(componentname, componentinstancenumber, context, configurationparameters, num_worker_threads, topology)
        # SUBCOMPONENTS
        
        macconfig = MacCsmaPPersistentConfigurationParameters(0.05)
        
        self.appl = VideoStreamingApplicationLayer("VideoStreamingApplicationLayer", componentinstancenumber, topology=topology)
        self.phy = UsrpB210OfdmFlexFramePhy("UsrpB210OfdmFlexFramePhy", componentinstancenumber, topology=topology)
        self.mac = CsmaPlain("MacCsmaPPersistent", componentinstancenumber,  configurationparameters=macconfig, uhd=self.phy.sdrdev,topology=topology)
        
        self.components.append(self.appl)
        self.components.append(self.phy)
        self.components.append(self.mac)

        # CONNECTIONS AMONG SUBCOMPONENTS
        self.appl.connect_me_to_component(ConnectorTypes.UP, self) #Not required if nodemodel will do nothing
        self.appl.connect_me_to_component(ConnectorTypes.DOWN, self.mac)
        
        self.mac.connect_me_to_component(ConnectorTypes.UP, self.appl)
        self.mac.connect_me_to_component(ConnectorTypes.DOWN, self.phy)
        
        # Connect the bottom component to the composite component....
        self.phy.connect_me_to_component(ConnectorTypes.UP, self.mac)
        self.phy.connect_me_to_component(ConnectorTypes.DOWN, self)
        
        # self.phy.connect_me_to_component(ConnectorTypes.DOWN, self)
        # self.connect_me_to_component(ConnectorTypes.DOWN, self.appl)
    
        

def main():
    topo = Topology()
# Note that the topology has to specific: usrp winslab_b210_0 is run by instance 0 of the component
# Therefore, the usrps have to have names winslab_b210_x where x \in (0 to nodecount-1)
    topo.construct_winslab_topology_without_channels(4, UsrpNode)
  # topo.construct_winslab_topology_with_channels(2, UsrpNode, FIFOBroadcastPerfectChannel)
  
  # time.sleep(1)
  # topo.nodes[0].send_self(Event(topo.nodes[0], UsrpNodeEventTypes.STARTBROADCAST, None))

    topo.start()
    i = 0
    while(i < 20):
        topo.nodes[3].appl.send_self(Event(topo.nodes[0], VideoStreamingApplicationLayerEventTypes.STARTBROADCAST, None))
        time.sleep(1)
        i = i + 1


if __name__ == "__main__":
    main()

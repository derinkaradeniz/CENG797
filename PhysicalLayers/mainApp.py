import os
import sys
import time

from adhoccomputing.GenericModel import GenericModel
from adhoccomputing.Generics import *
from adhoccomputing.Experimentation.Topology import Topology
from adhoccomputing.Networking.LinkLayer.GenericLinkLayer import GenericLinkLayer
from adhoccomputing.Networking.NetworkLayer.GenericNetworkLayer import GenericNetworkLayer
from adhoccomputing.Networking.LogicalChannels.GenericChannel import GenericChannel
from adhoccomputing.Networking.PhysicalLayer.UsrpB210OfdmFlexFramePhy import  UsrpB210OfdmFlexFramePhy
from adhoccomputing.Networking.MacProtocol.CSMA import MacCsmaPPersistent, MacCsmaPPersistentConfigurationParameters
from adhoccomputing.Networking.ApplicationLayer.MessageSegmentation import *
from gpsHandler import *
from communicator import *
import logging


macconfig = MacCsmaPPersistentConfigurationParameters(0.5, -50)
#sdrconfig = SDRConfiguration(freq =915000000.0, bandwidth = 4000000, chan = 0, hw_tx_gain = 70, hw_rx_gain = 30, sw_tx_gain = -12.0)
sdrconfig = SDRConfiguration(freq =915000000.0, bandwidth = 20000000, chan = 0, hw_tx_gain = 76, hw_rx_gain = 20, sw_tx_gain = -12.0)



class AdHocNode(GenericModel):

    def on_init(self, eventobj: Event):
        logger.applog(f"Initializing {self.componentname}.{self.componentinstancenumber}")
        pass

    def on_message_from_top(self, eventobj: Event):
        self.send_down(eventobj)

    def on_message_from_bottom(self, eventobj: Event):
        self.send_up(eventobj)

    def __init__(self, componentname, componentinstancenumber, context=None, configurationparameters=None, num_worker_threads=1, topology=None):
        super().__init__(componentname, componentinstancenumber, context, configurationparameters, num_worker_threads, topology)
        # SUBCOMPONENTS
        
        self.gpsApp = GPSHandlerApp("GPSHandlerApp", componentinstancenumber, topology=topology)
        self.appl = CommunicatorApp("CommunicatorApp", componentinstancenumber, topology=topology)
        self.seg = MessageSegmentation("MessageSegmentation", componentinstancenumber, topology=topology)
        self.phy = UsrpB210OfdmFlexFramePhy("UsrpB210OfdmFlexFramePhy", componentinstancenumber, topology=topology,usrpconfig=sdrconfig, )
        self.mac = MacCsmaPPersistent("MacCsmaPPersistent", componentinstancenumber,  configurationparameters=macconfig, sdr=self.phy.sdrdev, topology=topology)

        self.components.append(self.gpsApp)
        self.components.append(self.appl)
        self.components.append(self.mac)
        self.components.append(self.seg)
        self.components.append(self.phy)
        
        # CONNECTIONS AMONG SUBCOMPONENTS
        self.gpsApp.connect_me_to_component(ConnectorTypes.PEER, self.appl) 

        self.appl.connect_me_to_component(ConnectorTypes.PEER, self.gpsApp)
        self.appl.connect_me_to_component(ConnectorTypes.DOWN, self.seg)

        self.seg.connect_me_to_component(ConnectorTypes.UP, self.appl)
        self.seg.connect_me_to_component(ConnectorTypes.DOWN, self.mac)
        
        self.mac.connect_me_to_component(ConnectorTypes.UP, self.seg)
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
    while(i < 3):
        #topo.nodes[3].appl.send_self(Event(topo.nodes[0], UsrpApplicationLayerEventTypes.STARTBROADCAST, None))
        topo.nodes[3].appl.send_self(Event(topo.nodes[0], CommunicatorAppEventTypes.STARTGPSREQ, None))

        time.sleep(1)
        i = i + 1


if __name__ == "__main__":
    main()

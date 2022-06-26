import os
import sys
import time

from adhoccomputing.GenericModel import GenericModel
from adhoccomputing.Generics import *
from adhoccomputing.Experimentation.Topology import Topology
#from adhoccomputing.Networking.LinkLayer.GenericLinkLayer import GenericLinkLayer
#from adhoccomputing.Networking.NetworkLayer.GenericNetworkLayer import GenericNetworkLayer
#from adhoccomputing.Networking.LogicalChannels.GenericChannel import GenericChannel
from adhoccomputing.Networking.PhysicalLayer.UsrpB210OfdmFlexFramePhy import  UsrpB210OfdmFlexFramePhy
from adhoccomputing.Networking.ApplicationLayer.MessageSegmentation import *
from csmaPlain import CsmaPlain, CsmaPlainConfigurationParameters
from gpsHandler import *
from communicator import *
from testApp import *
import logging
import threading

macconfig = CsmaPlainConfigurationParameters(-70)
sdrconfig = SDRConfiguration(freq =915000000.0, bandwidth = 2000000, chan = 0, hw_tx_gain = 70, hw_rx_gain = 20, sw_tx_gain = -12.0)

class AdHocNode(GenericModel):

    def on_init(self, eventobj: Event):
        print(f"Initializing {self.componentname}.{self.componentinstancenumber}")
        pass

    def on_message_from_top(self, eventobj: Event):
        self.send_down(eventobj)

    def on_message_from_bottom(self, eventobj: Event):
        self.send_up(eventobj)

    def __init__(self, componentname, componentinstancenumber, context=None, configurationparameters=None, num_worker_threads=1, topology=None):
        print("main: init")
        super().__init__(componentname, componentinstancenumber, context, configurationparameters, num_worker_threads, topology)
        
        self.appl = TestApp("TestApp", componentinstancenumber, topology=topology)
        self.seg = MessageSegmentation("MessageSegmentation", componentinstancenumber, topology=topology)
        self.phy = UsrpB210OfdmFlexFramePhy("UsrpB210OfdmFlexFramePhy", componentinstancenumber, topology=topology, usrpconfig = sdrconfig)
        self.mac = CsmaPlain("CsmaPlain", componentinstancenumber,  configurationparameters=macconfig, sdr=self.phy.sdrdev, topology=topology)

        self.components.append(self.appl)
        self.components.append(self.mac)
        self.components.append(self.seg)
        self.components.append(self.phy)
        
        # SubComponent Connections
        self.appl.connect_me_to_component(ConnectorTypes.DOWN, self.seg)

        self.seg.connect_me_to_component(ConnectorTypes.UP, self.appl)
        self.seg.connect_me_to_component(ConnectorTypes.DOWN, self.mac)
        
        self.mac.connect_me_to_component(ConnectorTypes.UP, self.seg)
        self.mac.connect_me_to_component(ConnectorTypes.DOWN, self.phy)
        
        self.phy.connect_me_to_component(ConnectorTypes.UP, self.mac)
        self.phy.connect_me_to_component(ConnectorTypes.DOWN, self)        

def main():
    print("main")
    topo = Topology()
    topo.construct_winslab_topology_without_channels(4, AdHocNode)
    topo.start()   
    time.sleep(1) 

    i = 0
    while(i < 1):
        j = 0
        #while(j < 4):
        #    #topo.nodes[3].appl.send_self(Event(topo.nodes[0], UsrpApplicationLayerEventTypes.STARTBROADCAST, None))
        #    if j != 1 or j!= 3:
        #        topo.nodes[j].appl.send_self(Event(topo.nodes[0], TestAppEventTypes.STARTREQ, None))
        #        print(f"Call {j} ")
        #        time.sleep(1)
        #    j = j + 1

        topo.nodes[2].appl.send_self(Event(topo.nodes[0], TestAppEventTypes.STARTREQ, None))
        time.sleep(0.01)

        seqCount = 0
        payload = bytearray([1] * 64)

        for k in range(1000):

            seqCount = seqCount + 1
            header = TestAppMessageHeader(TestAppMessageTypes.BURST, 0, 2,sequencenumber= seqCount)
            message = GenericMessage(header, payload)
            evt = Event(topo.nodes[0], EventTypes.MFRT, message)
            topo.nodes[0].appl.send_down(evt)
            #topo.nodes[0].appl.send_self(Event(topo.nodes[0], TestAppEventTypes.STARTREQ, None))
            time.sleep(0.1)
        print("TIME IS UP!")
        time.sleep(10)
        #topo.nodes[2].appl.send_self(Event(topo.nodes[0], TestAppEventTypes.STARTREQ, None))
        #time.sleep(1)

        i = i + 1
    
    time.sleep(3)
    print("END")

if __name__ == "__main__":
    main()
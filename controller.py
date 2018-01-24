from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_0
from ryu.topology import event, switches
from ryu.topology.api import get_switch, get_link
from random import choice

SWITCH_LIST = []
LINK_LIST = []
PATHS = [('top', [1, 2, 5]), ('middle', [1, 3, 5]), ('bottom', [1, 4, 5])]

class L2Switch(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_0.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(L2Switch, self).__init__(*args, **kwargs)

    @set_ev_cls(event.EventSwitchEnter, MAIN_DISPATCHER)
    def get_topology_data(self, ev):
        SWITCH_LIST = []
        LINK_LIST = []
        SWITCH_LIST.extend(get_switch(self, None))
        switches=[switch.dp.id for switch in SWITCH_LIST]
        LINK_LIST.extend(get_link(self, None))
        links = [(link.src.dpid,link.dst.dpid,{'port':link.src.port_no}) for link in LINK_LIST]
        print('\n==========TOPOLOGY DISCOVERY=========')
        print('SWITCHES: ')
        print(' ' + str(switches))
        print('LINKS: ')
        for l in links:
            print(' ' + str(l))
        print('=====================================\n')

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg = ev.msg
        dp = msg.datapath
        ofp = dp.ofproto
        ofp_parser = dp.ofproto_parser

        paths_usage = {'top': 0, 'middle': 0, 'bottom': 0}
        
        rand_path = choice(PATHS)
        
        
        #actions = [ofp_parser.OFPActionOutput(ofp.OFPP_FLOOD)]
        #out = ofp_parser.OFPPacketOut(
        #    datapath=dp, buffer_id=msg.buffer_id, in_port=msg.in_port,
        #    actions=actions)
        #dp.send_msg(out)

    def add_flow(self, datapath, in_port, dst, src, actions):
        ofproto = datapath.ofproto

        match = datapath.ofproto_parser.OFPMatch(
            in_port=in_port,
            dl_dst=haddr_to_bin(dst), dl_src=haddr_to_bin(src))

        mod = datapath.ofproto_parser.OFPFlowMod(
            datapath=datapath, match=match, cookie=0,
            command=ofproto.OFPFC_ADD, idle_timeout=0, hard_timeout=0,
            priority=ofproto.OFP_DEFAULT_PRIORITY,
            flags=ofproto.OFPFF_SEND_FLOW_REM, actions=actions)
        
        datapath.send_msg(mod)

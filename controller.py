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
PATHS = [{'id': 'top', 'path': [1, 2, 5]}, {'id': 'middle', 'path': [1, 3, 5]}, {'id': 'bottom', 'path':[1, 4, 5]}]

class L2Switch(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_0.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(L2Switch, self).__init__(*args, **kwargs)

    def send_flow_stats_request(self, pin_msg):
        datapath = pin_msg.datapath
        ofp = datapath.ofproto
        ofp_parser = datapath.ofproto_parser

        match = ofp_parser.OFPMatch(in_port=pin_msg.in_port)
        table_id = 0xff
        out_port = ofp.OFPP_NONE
        req = ofp_parser.OFPFlowStatsRequest(datapath, 0, match, table_id, out_port)

        datapath.send_msg(req)

   def add_flow(self, datapath, in_port, dst, src, actions):
        ofproto = datapath.ofproto

        match = datapath.ofproto_parser.OFPMatch(
            in_port=in_port,
            dl_dst=haddr_to_bin(dst), dl_src=haddr_to_bin(src))

        mod = datapath.ofproto_parser.OFPFlowMod(
            datapath=datapath, match=match, cookie=0,
            command=ofproto.OFPFC_ADD, idle_timeout=0, hard_time$
            priority=ofproto.OFP_DEFAULT_PRIORITY,
            flags=ofproto.OFPFF_SEND_FLOW_REM, actions=actions)

        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def flow_stats_reply_handler(self, ev):
        msg = ev.msg
        ofp = msg.datapath.ofproto
        body = ev.msg.body

        flows = []

        if body:
            for stat in body:
                flows.append('table_id=%s match=%s '
                    'duration_sec=%d duration_nsec=%d '
                    'priority=%d '
                    'idle_timeout=%d hard_timeout=%d '
                    'cookie=%d packet_count=%d byte_count=%d '
                    'actions=%s' %
                    (stat.table_id, stat.match,
                    stat.duration_sec, stat.duration_nsec,
                    stat.priority,
                    stat.idle_timeout, stat.hard_timeout,
                    stat.cookie, stat.packet_count, stat.byte_count,
                    stat.actions))
            print('FlowStats: %s', flows)
        else:
            print('Flow table is EMPTY.')
            random_path = choice(PATHS)
            print('Chosen random path: ' + str(random_path))

        print('=====================================\n')

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
        in_port = msg.in_port

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]
        dst = eth.dst
        src = eth.src

        print('\n=====================================')
        print('PACKET IN at port: ' + str(in_port))

        self.send_flow_stats_request(msg)

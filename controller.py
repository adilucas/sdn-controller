from ryu.base
import app_manager
from ryu.controller
import ofp_event
from ryu.controller.handler
import MAIN_DISPATCHER
from ryu.controller.handler
import set_ev_cls
from ryu.ofproto
import ofproto_v1_0
from ryu.topology
import event, switches
from ryu.topology.api
import get_switch, get_link
from random
import choice

SWITCH_LIST = []
LINK_LIST = []
PATHS = [('top', [1, 2, 5]), ('middle', [1, 3, 5]), ('bottom', [1, 4, 5])]

class L2Switch(app_manager.RyuApp):
  OFP_VERSIONS = [ofproto_v1_0.OFP_VERSION]

def __init__(self, * args, * * kwargs):
  super(L2Switch, self).__init__( * args, * * kwargs)

@set_ev_cls(event.EventSwitchEnter, MAIN_DISPATCHER)
def get_topology_data(self, ev):
  SWITCH_LIST = []
LINK_LIST = []
SWITCH_LIST.extend(get_switch(self, None))
switches = [
  switch.dp.id
  for
  switch in SWITCH_LIST
]
LINK_LIST.extend(get_link(self, None))
links = [(link.src.dpid, link.dst.dpid, {
  'port': link.src.port_no
}) for link in LINK_LIST]
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
parser = dp.ofproto_parser
in_port = msg.match['in_port']
pkt = packet.Packet(msg.data)
eth = pkt.get_protocols(ethernet.ethernet)[0]
dst = eth.dst
src = eth.src
paths_usage = {
  'top': 0,
  'middle': 0,
  'bottom': 0
}

rand_path = choice(PATHS)

def send_port_stats_request(self, datapath):
  ofp = dp.ofproto
ofp_parser = dp.ofproto_parser
req = ofp_parser.OFPPortStatsRequest(dp, 0, ofp.OFPP_ANY)
dp.send_msg(req)

@set_ev_cls(ofp_event.EventOFPPortStatsReply, MAIN_DISPATCHER)
def port_stats_reply_handler(self, ev):
  for stat in ev.msg.body:
  self.logger.info("\tport_no=%d "
    "rx_packets=%d tx_packets=%d "
    "\n \trx_bytes=%d tx_bytes=%d "
    "rx_dropped=%d tx_dropped=%d "
    "rx_errors=%d tx_errors=%d "
    "\n \trx_frame_err=%d rx_over_err=%d rx_crc_err=%d "
    "\n \tcollisions=%d duration_sec=%d duration_nsec=%d" %
    (stat.port_no,
      stat.rx_packets, stat.tx_packets,
      stat.rx_bytes, stat.tx_bytes,
      stat.rx_dropped, stat.tx_dropped,
      stat.rx_errors, stat.tx_errors,
      stat.rx_frame_err, stat.rx_over_err,
      stat.rx_crc_err, stat.collisions,
      stat.duration_sec, stat.duration_nsec))

# out = ofp_parser.OFPPacketOut(#datapath = dp, buffer_id = msg.buffer_id, in_port = msg.in_port, #actions = actions)# dp.send_msg(out)

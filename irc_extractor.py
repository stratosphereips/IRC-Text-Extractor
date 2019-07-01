import json
import os
from collections import defaultdict

from graphviz import Digraph
from scapy.all import sniff
from scapy.layers.inet import IP, TCP
from scapy.layers.l2 import Ether

dir_path = os.path.dirname(os.path.realpath(__file__))
# path to data dit
data_dir_path = os.path.expanduser('~/strato_test_data')
output_dir_path = os.path.join(dir_path, 'output/')

PCAP = '49-1'
PCAP_PATH = os.path.join(data_dir_path, PCAP + '.pcap')
PCAP_JSON_PATH = os.path.join(output_dir_path, PCAP + '.json')
PCAP_TXT_PATH = os.path.join(output_dir_path, PCAP + '.txt')
TREE_PATH = os.path.join(output_dir_path, PCAP + '_tree.gv')

irc_logs = defaultdict(lambda: [])
unfinished_msg = ''
msg_not_finished = False

# IRC Communication port
PORT = 6667


def process_packet(pkt):
    # process only TCP
    if (TCP not in pkt) or (pkt[TCP].sport != PORT and pkt[TCP].dport != PORT):
        return

    # FIXME: not use global
    global msg_not_finished, unfinished_msg

    # Uncomment to visualize the packetw
    # pkt.pdfdump('packet_visualization.pdf')

    timestamp = pkt.time
    ip_src = pkt[IP].src
    ip_dst = pkt[IP].dst
    dport = pkt[TCP].dport
    sport = pkt[TCP].sport

    data = pkt[Ether][IP][TCP].payload.raw_packet_cache
    if data and 'PRIVMSG' in data.decode('ascii'):
        payload = data.decode('ascii')
        # payload schema is (list of) src PRIVMSG dst msg \r\n, so we split them by \r\n

        p_splitted = payload.split('\r\n')
        p_len = len(p_splitted)
        for i, msg in enumerate(p_splitted):
            if i == 0 and msg_not_finished:
                msg_not_finished = False
                msg = unfinished_msg + msg

            if i == p_len - 1 and payload[:4] != '\r\n':
                msg_not_finished = True
                unfinished_msg = msg
                return

            msg_splitted = msg.split()

            # msg starts with :, so it can be neglected
            src, dst, msg_text = msg_splitted[0], msg_splitted[2], ' '.join(msg_splitted[3:])[1:]
            irc_log = {'timestamp': timestamp, 'src_ip': ip_src, 'src_port': sport, 'dst_ip': ip_dst,
                       'dst_port': dport, 'src': src, 'dst': dst, 'msg': msg_text}
            irc_logs[((ip_src, sport), (ip_dst, dport))].append(irc_log)


def save_logs():
    logs = []
    for session, communication in irc_logs.items():
        src, dest = session[0], session[1]
        logs.append({'session {}:{}->{}:{}'.format(src[0], src[1], dest[0], dest[1]): communication})

    final_irc_logs = {'data': logs}

    with open(PCAP_JSON_PATH, 'w+', encoding='utf-8') as f:
        f.write(json.dumps(final_irc_logs, indent=4))

    with open(PCAP_TXT_PATH, 'w+', encoding='utf-8') as g:
        for session, logs in irc_logs.items():
            src, dest = session[0], session[1]
            g.write('session {}:{}->{}:{}\n'.format(src[0], src[1], dest[0], dest[1]))
            for log in logs:
                nick, channel, msg = log.get('src', ''), log.get('dst', ''), log.get('msg', '')
                g.write(' '.join([nick, channel, msg]) + '\n')


def load_logs(json_filename):
    global irc_logs
    with open(json_filename, 'r') as f:
        sessions = json.load(f)['data']
        irc_logs = {}
        for s in sessions:
            irc_logs.update(s)


def visualize_graph():
    dot = Digraph('IRC Tree', filename=TREE_PATH)
    dot.graph_attr.update(sep='+100,s100')
    hash_node = lambda v: str(abs(hash(v)) % (10 ** 8))
    edges = set()

    for session, logs in irc_logs.items():
        for log in logs:
            v1, v2, msg = log.get('src', ''), log.get('dst', ''), log.get('msg', '')
            v1_id = hash_node(v1)
            v2_id = hash_node(v2)

            # comment this block of code to show non-duplicate edges between nodes
            dot.node(v1_id, label=v1)
            dot.node(v2_id, label=v2)
            dot.edge(v1_id, v2_id)

            ## uncomment this block of code to show duplicate edges between nodes
            # if (v1_id, v2_id) not in edges:
            #     edges.add((v1_id, v2_id))
            #     dot.node(v1_id, label=v1)
            #     dot.node(v2_id, label=v2)
            #     dot.edge(v1_id, v2_id)

    dot.view()


def main():
    if os.path.isfile(PCAP_JSON_PATH):
        load_logs(PCAP_JSON_PATH)
    else:
        sniff(offline=PCAP_PATH, prn=process_packet, store=0)
        save_logs()

    # irc_logs.sort(key=lambda x: x.get('timestamp'))
    visualize_graph()


if __name__ == '__main__':
    main()

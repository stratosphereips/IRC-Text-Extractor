import json
from collections import defaultdict

from scapy.all import sniff
from scapy.layers.inet import IP, TCP
from scapy.layers.l2 import Ether


class IRCExtractor:
    irc_port_dict = {'2': 2407, '3': 2407, '4': 6667, '34': 2407, '39': 6667, '46': 4975, '51': 2407, '56': 80,
                     'irc1': 6667}

    def __init__(self):
        self.irc_logs = defaultdict(lambda: [])
        self.irc_packet_counter = 0
        self.unfinished_msg = ''
        self.msg_not_finished = False

    def process_packet(self, pkt, irc_port):
        # process only TCP
        if (TCP not in pkt) or (pkt[TCP].sport != irc_port and pkt[TCP].dport != irc_port):
            return

        if self.irc_packet_counter % 1000 == 0:
            print('IRC Packet #{}'.format(self.irc_packet_counter))

        # Uncomment to visualize the packetw
        # pkt.pdfdump('packet_visualization.pdf')

        timestamp = pkt.time
        ip_src = pkt[IP].src
        ip_dst = pkt[IP].dst
        dport = pkt[TCP].dport
        sport = pkt[TCP].sport
        data = pkt[Ether][IP][TCP].payload.raw_packet_cache

        self.irc_packet_counter += 1

        try:
            payload = data.decode('ascii')
        except:
            return

        if data and 'PRIVMSG' in payload:
            # payload = data.decode('utf8')
            # payload schema is (list of) src PRIVMSG dst msg \r\n, so we split them by \r\n
            p_splitted = payload.split('\r\n')
            p_len = len(p_splitted)
            for i, msg in enumerate(p_splitted):
                if i == 0 and self.msg_not_finished:
                    self.msg_not_finished = False
                    msg = self.unfinished_msg + msg

                if i == p_len - 1 and payload[:4] != '\r\n':
                    self.msg_not_finished = True
                    self.unfinished_msg = msg
                    return

                msg_splitted = msg.split()

                if msg_splitted[1] != 'PRIVMSG':
                    continue

                if len(msg_splitted) < 4:
                    continue

                # msg starts with :, so it can be neglected
                src, dst, msg_text = msg_splitted[0], msg_splitted[2], ' '.join(msg_splitted[3:])[1:]
                irc_log = {'timestamp': timestamp, 'src_ip': ip_src, 'src_port': sport, 'dst_ip': ip_dst,
                           'dst_port': dport, 'src': src, 'dst': dst, 'msg': msg_text}
                self.irc_logs[((ip_src, sport), (ip_dst, dport))].append(irc_log)

    def save_logs(self, pcap_out_json_path):
        logs = []
        for session, communication in self.irc_logs.items():
            src, dest = session[0], session[1]
            logs.append({'session {}:{}->{}:{}'.format(src[0], src[1], dest[0], dest[1]): communication})

        final_irc_logs = {'data': logs}

        with open(pcap_out_json_path, 'w+', encoding='utf-8') as f:
            f.write(json.dumps(final_irc_logs, indent=4))

        # with open(pcap_txt_path, 'w+', encoding='utf-8') as g:
        #     for session, logs in irc_logs.items():
        #         src, dest = session[0], session[1]
        #         g.write('session {}:{}->{}:{}\n'.format(src[0], src[1], dest[0], dest[1]))
        #         for log in logs:
        #             nick, channel, msg = log.get('src', ''), log.get('dst', ''), log.get('msg', '')
        #             g.write(' '.join([nick, channel, msg]) + '\n')

    def filter_logs(self, irc_logs, pcap_json_path):
        logs = []
        for session, communication in irc_logs.items():
            filtered_com = []
            for c in communication:
                if c['src'] != 'PRIVMSG' and c['src'] != 'NOTICE' and c['dst'] != 'PRIVMSG' and c['dst'] != 'NOTICE':
                    filtered_com.append(c)

            if len(filtered_com) > 0:
                logs.append({session: filtered_com})

        final_irc_logs = {'data': logs}

        with open(pcap_json_path, 'w+', encoding='utf-8') as f:
            f.write(json.dumps(final_irc_logs, indent=4))

    def load_logs(self, json_filename):
        print('loading logs...')
        with open(json_filename, 'r') as f:
            sessions = json.load(f)['data']
            irc_logs2 = {}
            for s in sessions:
                irc_logs2.update(s)

        return irc_logs2

    def sniff_pcap(self, pcap_path, pcap_out_json_path):
        print('sniffing pcap...')
        self.irc_logs = defaultdict(lambda: [])
        sniff(pcap_path, self.process_packet, count=0)
        self.save_logs(pcap_out_json_path)
        return self.irc_logs

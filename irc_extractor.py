import json
import socket
from collections import defaultdict

import dpkt


def compute_periodicity(communication):
    # TODO: implement
    # floating_avg = 0
    # for msg in communication:
    #     floating_avg
    return 0


class IRCExtractor:
    irc_port_dict = {'2': 2407, '3': 2407, '4': 6667, '34-1': 2407, '39': 6667, '46': 4975, '51': 2407, '56': 80,
                     'irc1': 6667}

    def __init__(self, pcap):
        self.irc_logs = defaultdict(lambda: [])
        self.irc_packet_counter = 0
        self.unfinished_msg = ''
        self.msg_not_finished = False
        self.irc_port = self.irc_port_dict[pcap]

    def process_packet(self, timestamp, buffer):
        eth = dpkt.ethernet.Ethernet(buffer)
        if eth.type != dpkt.ethernet.ETH_TYPE_IP:
            # not ip packet
            return

        ip = eth.data
        if type(ip.data) != dpkt.tcp.TCP:
            # not tcp packet
            return

        tcp = ip.data
        ip_src = socket.inet_ntoa(ip.src)
        ip_dst = socket.inet_ntoa(ip.dst)
        sport = tcp.sport
        dport = tcp.dport
        data = tcp.data

        if sport != self.irc_port and dport != self.irc_port:
            # invalid port
            return

        if self.irc_packet_counter % 1000 == 0:
            print('IRC PRIVMSG Packet #{}'.format(self.irc_packet_counter))

        try:
            payload = data.decode('ascii')
        except:
            return
        self.irc_packet_counter += 1
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

                # if len(msg_splitted) < 4:
                #     continue

                # msg starts with :, so it can be neglected
                src, dst, msg_text = msg_splitted[0], msg_splitted[2], ' '.join(msg_splitted[3:])[1:]
                irc_log = {'timestamp': timestamp, 'msg': msg_text, 'pkt_size': len(buffer)}
                self.irc_logs[((src, ip_src, sport), (dst, ip_dst, dport))].append(irc_log)

    def save_logs(self, pcap_out_json_path):
        logs = []
        for session, communication in self.irc_logs.items():
            session_log = {}
            src, dst = session[0], session[1]
            msg_times = list(map(lambda c: c['timestamp'], communication))
            pkt_sizes = list(map(lambda c: c['pkt_size'], communication))

            session_log['src'] = src[0]
            session_log['src_ip'] = src[1]
            session_log['src_port'] = src[2]

            session_log['dst'] = dst[0]
            session_log['dst_ip'] = dst[1]
            session_log['dst_port'] = dst[2]

            session_log['start_time'] = min(msg_times)
            session_log['end_time'] = max(msg_times)

            session_log['msg_count'] = len(communication)
            session_log['pkt_size_total'] = sum(pkt_sizes)
            session_log['msgs'] = communication
            session_log['periodicity'] = compute_periodicity(communication)

            logs.append(session_log)

        final_irc_logs = {'sessions': logs}

        self.irc_logs = logs

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
        self.irc_logs = defaultdict(lambda: [])
        with open(json_filename, 'r') as f:
            self.irc_logs = json.load(f)['sessions']

        return self.irc_logs

    def sniff_pcap(self, pcap_path, pcap_out_json_path):
        print('sniffing pcap...')
        self.irc_logs = defaultdict(lambda: [])

        with open(pcap_path, 'rb') as f:
            pcap = dpkt.pcap.Reader(f)
            for ts, buf in pcap:
                self.process_packet(ts, buf)

        self.save_logs(pcap_out_json_path)
        return self.irc_logs

    def utf8len(s: str):
        return len(s.encode('utf-8'))

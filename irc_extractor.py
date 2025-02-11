import json
import os
import socket
from collections import defaultdict
from copy import deepcopy
import dpkt
import numpy as np
import re
import irc_config


def compute_session_periodicity(communication):
    """
    using Fast Fourier Transform to compute periodicity of messages in sessions

    @:return value in [0,1] interval - 0 means that messages are not periodic at all
    """

    if len(communication) < 3:
        return None

    t = list(map(lambda x: x['timestamp'], communication))
    td = np.asarray(list(map(lambda x: x[0] - x[1], zip(t[1:], t))))
    fft_res = np.absolute(np.fft.fft(td))
    T = fft_res.argmax() + 2

    rng_size = int(len(td) / T)
    td_T = [td[x * T:x * T + T] for x in range(rng_size)]
    td_T_avg = np.mean(td_T, 0)
    # ||td_t - td_avg ||2 / ||td_t||
    td_nmse = np.linalg.norm(td_T - td_T_avg) / np.linalg.norm(td_T)

    return 1 - td_nmse


def compute_msg_periodicity(communication):
    if len(communication) < 3:
        return len(communication) * [None]

    t = list(map(lambda x: x['timestamp'], communication))

    msg_per = list()
    # not able to compute last element periodicity - no successor msg
    msg_per.append(None)

    for ta, tb, tc in zip(t, t[1:], t[2:]):
        t1 = tb - ta
        t2 = tc - tb
        try:
            msg_per.append(t2 / t1)
        except ZeroDivisionError:
            msg_per.append(None)
            print('t1 = {} - {} =  {}, t2:{} - {} = {},'.format(tb, ta, t1, tc, tb, t2))

    # not able to compute last element periodicity - no successor msg
    msg_per.append(None)

    return msg_per


class IRCExtractor:
    irc_port_dict = {'2.irc': 2407, '3.irc': 2407, '4.irc': 6667, '34.irc': 2407, '39.irc': 6667, '42.irc': 4975,
                     '51.irc': 54468, '56.irc': 80, '62.irc': 443, 'irc1': 6667, 'irc3': 6667}

    def __init__(self, pcap):
        self.irc_logs = defaultdict(lambda: [])
        self.irc_packet_counter = 0
        self.unfinished_msg = ''
        self.msg_not_finished = False
        self.irc_port = self.irc_port_dict[pcap]

    def process_packet(self, timestamp, buffer):
        eth = dpkt.ethernet.Ethernet(buffer)
        if eth.type != dpkt.ethernet.ETH_TYPE_IP and eth.type != dpkt.ethernet.ETH_TYPE_8021Q:
            # not ip packet
            return

        try:
            ip = eth.data
            # not tcp packet
            if type(ip.data) != dpkt.tcp.TCP:
                return
        except AttributeError:
            return 
            
        try:
            tcp = ip.data
            ip_src = socket.inet_ntoa(ip.src)
            ip_dst = socket.inet_ntoa(ip.dst)
            sport = tcp.sport
            dport = tcp.dport
            data = tcp.data
        except OSError:
            return

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

                if len(msg_splitted) < 4 or msg_splitted[1] != 'PRIVMSG':
                    continue

                # msg starts with :, so it can be neglected
                src, dst, msg_text = msg_splitted[0], msg_splitted[2], ' '.join(msg_splitted[3:])[1:]
                irc_log = {'timestamp': timestamp, 'msg': msg_text, 'pkt_size': len(buffer), 'sport': sport}
                self.irc_logs[((src, ip_src), (dst, ip_dst, dport))].append(irc_log)

    def save_logs(self, pcap_out_json_path, malicious):
        logs = []
        for session, communication in self.irc_logs.items():
            session_log = {}
            src, dst = session[0], session[1]
            msg_times = list(map(lambda c: c['timestamp'], communication))
            pkt_sizes = list(map(lambda c: c['pkt_size'], communication))

            session_log['src'] = src[0]
            session_log['src_ip'] = src[1]

            session_log['src_ports'] = list(set(map(lambda x: x['sport'], communication)))

            for msg in communication:
                del msg['sport']
            
            session_log['dst'] = dst[0]
            session_log['dst_ip'] = dst[1]
            session_log['dst_port'] = dst[2]

            session_log['start_time'] = min(msg_times)
            session_log['end_time'] = max(msg_times)
            session_log['duration'] =  session_log['end_time'] - session_log['start_time']

            session_log['msg_count'] = len(communication)
            session_log['pkt_size_total'] = sum(pkt_sizes)

            per = compute_session_periodicity(communication)
            if per is not None:
                session_log['periodicity'] = per
            else:
                session_log['periodicity'] = np.nan

            msg_per = compute_msg_periodicity(communication)
            
            # MODEL 2
            src = src[0]
            usr_rgx = re.match(r'^.*?(?=@)', src + '@')
            src_username = src[: usr_rgx.regs[0][1]]
            spec_chars_username_mean = 0 if len(src_username) == 0 else len(re.findall(r'[^A-Za-z]', src_username)) / len(src_username)
            msg_special_chars = []
            msg_word_count = defaultdict(lambda: 0)

            comm2 = []
            for msg, p in zip(communication, msg_per):
                msg['periodicity'] = p if p is not None else np.nan
                msg_content = msg['msg']
                msg_words = msg_content.split()
                for word in msg_words:
                    msg_word_count[word] += 1
                msg_spec = 0 if len(msg_content) == 0 else len(re.findall(r'[^A-Za-z]', msg_content)) / len(msg_content)
                msg_special_chars.append(msg_spec)
                
                comm2.append(msg)

            _wordcounts = list(msg_word_count.values())
            p = _wordcounts / np.sum(_wordcounts)
            msg_word_entropy = -np.sum(p * np.log2(p))
            spec_chars_msg_mean = np.mean(msg_special_chars)

            session_log['spec_chars_username_mean'] = spec_chars_username_mean
            session_log['spec_chars_msg_mean'] = spec_chars_msg_mean
            session_log['msg_word_entropy'] = msg_word_entropy
            session_log['malicious'] = malicious
            session_log['msgs'] = comm2

            logs.append(session_log)

        final_irc_logs = {'sessions': logs}

        self.irc_logs = logs

        with open(pcap_out_json_path, 'w+', encoding='utf-8') as f:
            f.write(json.dumps(final_irc_logs, indent=4))

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

        return deepcopy(self.irc_logs)

    def sniff_pcap(self, pcap_path, pcap_out_json_path, malicious):
        print('sniffing pcap...')
        self.irc_logs = defaultdict(lambda: [])

        with open(pcap_path, 'rb') as f:
            pcap = dpkt.pcap.Reader(f)
            for ts, buf in pcap:
                # checking for zero ethertype and throwing away:
                if len(buf) > 0:
                    try:
                        self.process_packet(ts, buf)
                    except:
                        continue
 
        self.save_logs(pcap_out_json_path, malicious)
        return self.irc_logs


def main():
    for pcap in irc_config.PCAPS.items():
        print('Sniffing PCAP {}...'.format(pcap[0]))
        irc_extractor = IRCExtractor(pcap[0])
        if os.path.isfile(irc_config.pcap_json_path(pcap[0])):
            print(irc_config.pcap_json_path(pcap[0]))
            irc_logs = irc_extractor.load_logs(irc_config.pcap_json_path(pcap[0]))
            # filter_logs()
        else:
            irc_logs = irc_extractor.sniff_pcap(irc_config.pcap_path(pcap), irc_config.pcap_json_path(pcap[0]), malicious=pcap[1])

    # irc_extractor.extract_features()
    # irc_logs.sort(key=lambda x: x.get('timestamp'))
    # graph = build_graph(irc_logs)
    # visualize_graph(graph, PCAP_GRAPH_PATH)


if __name__ == '__main__':
    main()

import re
from collections import defaultdict

import numpy as np
import pandas as pd

import irc_config
from irc_extractor import IRCExtractor


def get_trn_lines(irc_logs, malicious):
    trn_lines = []

    for session in irc_logs:
        if 'periodicity' not in session:
            continue

        periodicity = session['periodicity']
        duration = session['end_time'] - session['start_time']
        src, src_ip, src_ports = session['src'], session['src_ip'], session['src_ports']
        dst, dst_ip, dst_port = session['dst'], session['dst_ip'], session['dst_port']
        pkt_size = session['pkt_size_total']
        msg_count = session['msg_count']

        # add the @ char to the end in case there is no @ to not have blank username
        usr_rgx = re.match(r'^.*?(?=@)', src + '@')
        src_username = src[: usr_rgx.regs[0][1]]
        username_spec_chars_var = len(re.findall(r'[^A-Za-z]', src_username)) / len(src_username)
        msg_special_chars = []
        msg_word_count = defaultdict(lambda: 0)
        for msg in session['msgs']:
            msg_content = msg['msg']
            msg_words = msg_content.split()
            for word in msg_words:
                msg_word_count[word] += 1
            msg_spec = len(re.findall(r'[^A-Za-z]', msg_content)) / len(msg_content)
            msg_special_chars.append(msg_spec)

        _wordcounts = list(msg_word_count.values())
        p = _wordcounts / np.sum(_wordcounts)
        msg_word_entropy = -np.sum(p * np.log2(p))
        spec_chars_msg_var = np.mean(msg_special_chars)

        line = [round(periodicity, 4), round(duration, 0), round(pkt_size), msg_count, len(src_ports), dst_port,
                round(username_spec_chars_var, 4), round(spec_chars_msg_var, 4), round(msg_word_entropy, 4), malicious]
        trn_lines.append(line)

    return trn_lines


def create_trn_data_txt(irc_logs_malicious, irc_logs_nonmalicious, pcap_txt_path):
    print('creating training txt data..')
    mal_data = get_trn_lines(irc_logs_malicious, malicious=1)
    nonmal_data = get_trn_lines(irc_logs_nonmalicious, malicious=0)

    trn_data = mal_data + nonmal_data
    with open(pcap_txt_path, 'w+') as f:
        f.write('\n'.join(list(map(lambda line: ';'.join(map(str, line)), trn_data))))
        f.close()


def create_trn_data_csv(irc_logs_malicious, irc_logs_nonmalicious, pcap_csv_path):
    print('creating training csv data..')
    cols = ['periodicity', 'duration', 'pkt_size', 'msg_count', 'src_ports_count', 'dst_port', 'src_spec_chars',
            'msg_spec_chars', 'msg_word_entropy', 'malicious']

    mal_data = get_trn_lines(irc_logs_malicious, malicious=1)
    nonmal_data = get_trn_lines(irc_logs_nonmalicious, malicious=0)

    trn_data = mal_data + nonmal_data

    df = pd.DataFrame(trn_data, columns=cols)
    df.to_csv(pcap_csv_path, encoding='utf-8', sep=';')


def main():
    irc_logs_malicious = []
    for pcap in irc_config.PCAPS_MALICIOUS:
        extr = IRCExtractor(pcap)
        irc_logs_malicious += extr.load_logs(irc_config.pcap_json_path(pcap))

    irc_logs_nonmalicious = []
    for pcap in irc_config.PCAPS_NONMALICIOUS:
        extr = IRCExtractor(pcap)
        irc_logs_nonmalicious += extr.load_logs(irc_config.pcap_json_path(pcap))

    create_trn_data_csv(irc_logs_malicious, irc_logs_nonmalicious, irc_config.PCAP_TRN_CSV_PATH)
    create_trn_data_txt(irc_logs_malicious, irc_logs_nonmalicious, irc_config.PCAP_TRN_TXT_PATH)


if __name__ == '__main__':
    main()

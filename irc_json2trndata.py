import re
from collections import defaultdict

import numpy as np
import pandas as pd

import irc_config
from irc_extractor import IRCExtractor
from sklearn.impute import SimpleImputer 

def get_trn_lines(irc_logs):
    trn_lines = []

    for session in irc_logs:
        if 'periodicity' not in session:
            periodicity = -1
        else:
            periodicity = session['periodicity']
        
        duration = session['end_time'] - session['start_time']
        src, src_ip, src_ports = session['src'], session['src_ip'], session['src_ports']
        dst, dst_ip, dst_port = session['dst'], session['dst_ip'], session['dst_port']
        pkt_size = session['pkt_size_total']
        msg_count = session['msg_count']

        msg_word_entropy = session['msg_word_entropy']
        spec_chars_msg_mean = session['spec_chars_msg_mean']
        spec_chars_username_mean = session['spec_chars_username_mean']
        malicious = session['malicious']

        line = [round(periodicity, 4), round(duration, 0), round(pkt_size), msg_count, len(src_ports),round(dst_port,0),
                round(spec_chars_username_mean, 4), round(spec_chars_msg_mean, 4), round(msg_word_entropy, 4), int(malicious)]
        trn_lines.append(line)

    return trn_lines


def create_trn_data_txt(irc_logs_malicious, irc_logs_nonmalicious, pcap_txt_path):
    print('creating training txt data..')
    mal_data = get_trn_lines(irc_logs_malicious)
    nonmal_data = get_trn_lines(irc_logs_nonmalicious)

    trn_data = mal_data + nonmal_data
    with open(pcap_txt_path, 'w+') as f:
        f.write('\n'.join(list(map(lambda line: ';'.join(map(str, line)), trn_data))))
        f.close()


def create_trn_data_csv(irc_logs_malicious, irc_logs_nonmalicious, pcap_csv_path):
    print('creating training csv data..')
    cols = ['periodicity', 'duration', 'pkt_size', 'msg_count', 'src_ports_count','dst_port', 'src_spec_chars',
            'msg_spec_chars', 'msg_word_entropy', 'malicious']

    mal_data = get_trn_lines(irc_logs_malicious)
    nonmal_data = get_trn_lines(irc_logs_nonmalicious)

    trn_data = mal_data + nonmal_data

    df = pd.DataFrame(trn_data, columns=cols)
    imp = SimpleImputer(strategy="mean")
    ii = imp.fit_transform(df)
    
    df = pd.DataFrame(ii, columns=cols)     
    df = df.round({'periodicity':4})    
    df.to_csv(pcap_csv_path, encoding='utf-8', sep=';')

    
def main():
    irc_logs_malicious = []
    for pcap in irc_config.PCAPS_MALICIOUS:
        # print(pcap)
        extr = IRCExtractor(pcap)
        irc_logs_malicious += extr.load_logs(irc_config.pcap_json_path(pcap))

    irc_logs_nonmalicious = []
    for pcap in irc_config.PCAPS_NONMALICIOUS:
        extr = IRCExtractor(pcap)
        irc_logs_nonmalicious += extr.load_logs(irc_config.pcap_json_path(pcap))
    
    create_trn_data_csv(irc_logs_malicious, irc_logs_nonmalicious, irc_config.PCAP_TRN_CSV_PATH)
    
    # lines_mal = compute_features(irc_logs_malicious, True)
    # lines_nonmal = compute_features(irc_logs_malicious, False)
    # data = lines_mal + lines_nonmal
    # import json
    # with open('training_data.json', 'w+') as fp:
    #     json.dump(data, fp, indent=4)

if __name__ == '__main__':
    main()
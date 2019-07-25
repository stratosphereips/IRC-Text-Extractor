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
        line = [round(periodicity, 4), round(duration, 0), pkt_size, msg_count, len(src_ports), dst_port, malicious]
        trn_lines.append(line)

    return trn_lines


def create_trn_data_txt(irc_logs_malicious, irc_logs_nonmalicious, pcap_txt_path):
    print('creating training txt data..')
    mal_data = get_trn_lines(irc_logs_malicious, malicious=1)
    nonmal_data = get_trn_lines(irc_logs_nonmalicious, malicious=0)

    trn_data = mal_data + nonmal_data
    with open(pcap_txt_path, 'w+') as f:
        f.write('\n'.join(list(map(lambda line: ','.join(map(str, line)), trn_data))))
        f.close()


def create_trn_data_csv(irc_logs_malicious, irc_logs_nonmalicious, pcap_csv_path):
    print('creating training csv data..')
    cols = ['periodicity', 'duration', 'pkt_size', 'msg_count', 'src_ports_count', 'dst_port', 'malicious']

    mal_data = get_trn_lines(irc_logs_malicious, malicious=1)
    nonmal_data = get_trn_lines(irc_logs_nonmalicious, malicious=0)

    trn_data = mal_data + nonmal_data

    df = pd.DataFrame(trn_data, columns=cols)
    df.to_csv(pcap_csv_path, encoding='utf-8', sep=',')


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

import numpy as np
import pandas as pd


def get_trn_lines(irc_logs):
    trn_lines = []

    for malicious in range(1):
        for session in irc_logs:
            if 'periodicity' not in session:
                continue

            periodicity = session['periodicity']
            duration = session['end_time'] - session['start_time']
            src, src_ip, src_ports = session['src'], session['src_ip'], session['src_ports']
            dst, dst_ip, dst_port = session['dst'], session['dst_ip'], session['dst_port']
            pkt_size = session['pkt_size_total']
            msg_count = session['msg_count']
            line = [periodicity, duration, pkt_size, msg_count, len(src_ports), dst_port, 1]
            trn_lines.append(line)

    return trn_lines


def create_trn_data_txt(irc_logs, pcap_txt_path):
    print('creating training txt data..')
    trn_lines = get_trn_lines(irc_logs)

    with open(pcap_txt_path, 'w+') as f:
        f.write('\n')
        f.write('\n'.join(list(map(lambda line: ' '.join(line), map(str, trn_lines)))))
        f.close()


def create_trn_data_csv(irc_logs, pcap_csv_path):
    print('creating training csv data..')
    trn_lines = get_trn_lines(irc_logs)
    cols = ['periodicity', 'duration', 'pkt_size', 'msg_count', 'src_ports_count', 'dst_port', 'malicious']
    df = pd.DataFrame(np.array(trn_lines), columns=cols)
    df.to_csv(pcap_csv_path, encoding='utf-8', sep=',')


def main():
    pass


if __name__ == '__main__':
    main()

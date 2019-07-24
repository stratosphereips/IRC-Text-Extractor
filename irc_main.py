import os

from irc_extractor import IRCExtractor
from irc_json2trndata import create_trn_data

dir_path = os.path.dirname(os.path.realpath(__file__))
# path to data dir
data_dir_path = os.path.expanduser('~/strato_test_data/pcaps/malicious/merged_irc')
output_dir_path = os.path.join(dir_path, 'output/')

PCAP = 'irc1'
PCAP_PATH = os.path.join(data_dir_path, PCAP + '.pcap')
PCAP_JSON_PATH = os.path.join(output_dir_path, PCAP + '.json')
PCAP_TXT_PATH = os.path.join(output_dir_path, 'trn/non-malicious.txt')
PCAP_GRAPH_PATH = os.path.join(output_dir_path, PCAP + '_tree.gv')


def main():
    irc_extractor = IRCExtractor(PCAP)
    if os.path.isfile(PCAP_JSON_PATH):
        irc_logs = irc_extractor.load_logs(PCAP_JSON_PATH)
        create_trn_data(irc_logs, PCAP_TXT_PATH)
        # filter_logs()

    else:
        irc_logs = irc_extractor.sniff_pcap(PCAP_PATH, PCAP_JSON_PATH)

    # irc_extractor.extract_features()
    # irc_logs.sort(key=lambda x: x.get('timestamp'))
    # graph = build_graph(irc_logs)
    # visualize_graph(graph, PCAP_GRAPH_PATH)


if __name__ == '__main__':
    main()

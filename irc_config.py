import os

dir_path = os.path.dirname(os.path.realpath(__file__))
# path to data dir
data_dir_path = os.path.expanduser('~/strato_test_data/pcaps/malicious/merged_irc')
output_dir_path = os.path.join(dir_path, 'output/')

PCAP = 'irc1'
PCAP_PATH = os.path.join(data_dir_path, PCAP + '.pcap')
PCAP_JSON_PATH = os.path.join(output_dir_path, PCAP + '.json')
PCAP_TXT_PATH = os.path.join(dir_path, 'input/trn_data.txt')
PCAP_CSV_PATH = os.path.join(dir_path, 'input/trn_data.csv')
PCAP_GRAPH_PATH = os.path.join(output_dir_path, PCAP + '_tree.gv')

PCAPS_MALICIOUS = ['2.irc', '3.irc', '34.irc']
PCAPS_NONMALICIOUS = ['irc1']

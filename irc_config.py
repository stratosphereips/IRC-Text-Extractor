import os

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
DATA_DIR_PATH = os.path.expanduser('~/strato_test_data/pcaps/malicious/merged_irc')
OUTPUT_DIR_PATH = os.path.join(DIR_PATH, 'output/')

PCAPS_MALICIOUS = ['2.irc', '3.irc', '34.irc']
PCAPS_NONMALICIOUS = ['irc1']
PCAP_TRN_TXT_PATH = os.path.join(DIR_PATH, 'input/trn_data.txt')
PCAP_TRN_CSV_PATH = os.path.join(DIR_PATH, 'input/trn_data.csv')

PCAP = 'irc1'

pcap_json_path = lambda pcap: os.path.join(OUTPUT_DIR_PATH, pcap + '.json')
pcap_graph_path = lambda pcap: os.path.join(OUTPUT_DIR_PATH, pcap + '_tree.gv')
pcap_path = lambda pcap: os.path.join(DATA_DIR_PATH, PCAP + '.pcap')

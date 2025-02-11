import os

DIR_PATH = os.path.dirname(os.path.realpath(__file__))

DATA_DIR_MAL_PATH = os.path.expanduser('~/pcaps/mal')
DATA_DIR_NONMAL_PATH = os.path.expanduser('~/pcaps/nonmal')
OUTPUT_DIR_PATH = os.path.join(DIR_PATH, 'output/')

PCAPS_MALICIOUS = ['2.irc', '3.irc', '4.irc','34.irc','39.irc','46.irc','51.irc']
PCAPS_NONMALICIOUS = ['irc1','irc3']
PCAP_TRN_TXT_PATH = os.path.join(DIR_PATH, 'input/trn_data_per.txt')
PCAP_TRN_CSV_PATH = os.path.join(DIR_PATH, 'input/trn_data_per.csv')

PCAP = 'irc1'
PCAPS = {'2.irc': True, '3.irc': True, '4.irc': True,'34.irc': True,'39.irc': True,'46.irc': True,'51.irc': True, 'irc1': False,'irc3': False}

pcap_json_path = lambda pcap: os.path.join(OUTPUT_DIR_PATH, pcap[0] + '.json')
pcap_path = lambda pcap: os.path.join(DATA_DIR_MAL_PATH if pcap[1] else DATA_DIR_NONMAL_PATH, pcap[0] + '.pcap')
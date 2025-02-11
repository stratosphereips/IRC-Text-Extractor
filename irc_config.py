import os

DIR_PATH = os.path.dirname(os.path.realpath(__file__))

DATA_DIR_PATH = os.path.join(DIR_PATH, 'data/')
OUTPUT_DIR_PATH = os.path.join(DIR_PATH, 'output/')

PCAPS_MALICIOUS = ['2.irc', '3.irc', '4.irc','34.irc','39.irc','42.irc','51.irc','56.irc','62.irc']
PCAPS_NONMALICIOUS = ['irc1']#, 'irc3']
PCAP_TRN_CSV_PATH = os.path.join(DIR_PATH, 'input/trn_data_v2.csv')

PCAP = 'irc1'
PCAPS = {'irc1': False}#{'2.irc': True, '3.irc': True, '4.irc': True,'34.irc': True,'39.irc': True,'42.irc': True,'51.irc': True, '56.irc': True,'62.irc': True, 'irc1': False}#'irc3': False}

pcap_json_path = lambda pcap: os.path.join(OUTPUT_DIR_PATH, pcap + '.json')
pcap_path = lambda pcap: os.path.join(DATA_DIR_PATH if pcap[1] else DATA_DIR_PATH, pcap[0] + '.pcap')
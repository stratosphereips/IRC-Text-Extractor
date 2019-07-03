urls = ['IoTScenarios/CTU-IoT-Malware-Capture-2-15/bro/irc.log',
        'IoTScenarios/CTU-IoT-Malware-Capture-2-72/bro/irc.log',
        'IoTScenarios/CTU-IoT-Malware-Capture-2-71/bro/irc.log',
        'IoTScenarios/CTU-IoT-Malware-Capture-2-73/bro/irc.log',
        'IoTScenarios/CTU-IoT-Malware-Capture-2-51/bro/irc.log',
        'IoTScenarios/CTU-IoT-Malware-Capture-3-1/bro/irc.log',
        'IoTScenarios/CTU-IoT-Malware-Capture-34-2/bro/irc.log',
        'IoTScenarios/CTU-IoT-Malware-Capture-2-41/bro/irc.log',
        'IoTScenarios/CTU-IoT-Malware-Capture-2-47/bro/irc.log',
        'IoTScenarios/CTU-IoT-Malware-Capture-2-44/bro/irc.log',
        'IoTScenarios/CTU-IoT-Malware-Capture-51-3/bro/irc.log',
        'IoTScenarios/CTU-IoT-Malware-Capture-2-43/bro/irc.log',
        'IoTScenarios/CTU-IoT-Malware-Capture-2-74/bro/irc.log',
        'IoTScenarios/CTU-IoT-Malware-Capture-51-1/bro/irc.log',
        'IoTScenarios/CTU-IoT-Malware-Capture-39-1/bro/irc.log',
        'IoTScenarios/CTU-IoT-Malware-Capture-2-45/bro/irc.log',
        'IoTScenarios/CTU-IoT-Malware-Capture-2-64/bro/irc.log',
        'IoTScenarios/CTU-IoT-Malware-Capture-56-1/bro/irc.log',
        'IoTScenarios/CTU-IoT-Malware-Capture-2-42/bro/irc.log',
        'IoTScenarios/CTU-IoT-Malware-Capture-51-2/bro/irc.log',
        'IoTScenarios/CTU-IoT-Malware-Capture-2-1/bro/irc.log',
        'IoTScenarios/CTU-IoT-Malware-Capture-46-1/bro/irc.log',
        'IoTScenarios/CTU-IoT-Malware-Capture-39-3/bro/irc.log',
        'IoTScenarios/CTU-IoT-Malware-Capture-4-1/bro/irc.log',
        'IoTScenarios/CTU-IoT-Malware-Capture-42-2/bro/irc.log',
        'IoTScenarios/CTU-IoT-Malware-Capture-2-32/bro/irc.log',
        'IoTScenarios/CTU-IoT-Malware-Capture-2-22/bro/irc.log',
        'IoTScenarios/CTU-IoT-Malware-Capture-34-1/bro/irc.log',
        'IoTScenarios/CTU-IoT-Malware-Capture-2-28/bro/irc.log',
        'IoTScenarios/CTU-IoT-Malware-Capture-2-40/bro/irc.log',
        'IoTScenarios/CTU-IoT-Malware-Capture-2-17/bro/irc.log',
        'IoTScenarios/CTU-IoT-Malware-Capture-2-80/bro/irc.log']

import re

urls = list(map(lambda url: 'https://mcfp.felk.cvut.cz/nonpublic/' + re.findall('\/(.*?)\/', url)[0], urls))
with open('adresses.txt', 'w+') as f:
    f.write('\n'.join(urls))

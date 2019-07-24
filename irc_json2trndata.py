def create_trn_data(irc_logs, pcap_txt_path):
    print('creating trn data..')
    txt_lines = []
    for session in irc_logs:
        if 'periodicity' not in session:
            continue

        src, src_ip, src_ports = session['src'], session['src_ip'], session['src_ports']
        dst, dst_ip, dst_port = session['dst'], session['dst_ip'], session['dst_port']
        duration = session['end_time'] - session['start_time']
        pkt_size = session['pkt_size_total']
        periodicity = session['periodicity']
        line = [src, src_ip, str(len(src_ports)), dst, dst_ip, str(dst_port), str(duration), str(pkt_size),
                str(round(periodicity, 4))
                ]
        txt_lines.append(' '.join(line))

    with open(pcap_txt_path, 'a+') as f:
        f.write('\n')
        f.write('\n'.join(txt_lines))
        f.close()

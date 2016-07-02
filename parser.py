#!/usr/bin/env python
import os
import requests
import csv
import StringIO
import re
import base64

csv_vpngate = "http://www.vpngate.net/api/iphone/"
response = requests.get(csv_vpngate)
text_raw = response.text.encode("utf-8")

text_remove_1 = re.sub(r"\*vpn_servers\r\n", "", text_raw)
text = re.sub(r"#HostName","HostName", text_remove_1)

csv_reader = csv.DictReader(StringIO.StringIO(text))
count = 0
default_dir = "/opt/davfs/vpn"

for csv in csv_reader:
    hostname = csv["HostName"]
    ip = csv["IP"]
    country = csv["CountryShort"]
    session = csv["NumVpnSessions"]
    if session:
        if session.isdigit() and (int(session) < 2):
            continue
    else:
        continue

    try:
        decoded = base64.b64decode(csv["OpenVPN_ConfigData_Base64"])

        proto_line = re.findall(r"^proto (\w*)", decoded, re.MULTILINE)
        if proto_line:
            proto = proto_line[0]
            #print proto

        remote_line = re.findall(r"^remote .* (\d*)", decoded, re.MULTILINE)
        if remote_line:
            port = remote_line[0]
            #print port

    except:
        pass
    finally:
        if( hostname and ip and decoded ):
            filename = "%s_%s_%s_%s_%s.ovpn" % (hostname, ip, port, proto, country)
            fullname = os.path.join(default_dir, filename)
            with open(fullname, "w+") as f:
                count+=1
                f.write(decoded)

print "Total parsed %d files" % count

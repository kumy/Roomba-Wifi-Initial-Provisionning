#!/usr/bin/env python3

import binascii
import sys
import socket
import ssl
import struct
import time
import paho.mqtt.client as mqtt

# Get Robot CA
# openssl s_client -showcerts -connect 192.168.10.1 < /dev/null 2>/dev/null|openssl x509 -outform PEM > robot-ca.pem

msgs = [
    #{'topic':"delta", 'payload':'{ "state" : { "timezone" : "Europe/Paris" } }'},
    #{'topic':"wifictl", 'payload':'{ "state" : { "sdiscUrl" : "https://disc-prod.iot.irobotapi.com/v1/robot/discover?robot_id=0000000000000000&country_code=FR&sku=R966040" } }'},
    #{'topic':"wifictl", 'payload':'{ "state" : { "ntphosts" : "0.irobot.pool.ntp.org 1.irobot.pool.ntp.org 2.irobot.pool.ntp.org 3.irobot.pool.ntp.org" } }'},
    #{'topic':"delta", 'payload':'{ "state" : {"country" : "FR"} }'},
    #{'topic':"delta", 'payload':'{ "state" : { "cloudEnv" : "prod" } }'},
    {'topic':"wifictl", 'payload':'{"state": {"wlcfg": {"pass": "wifisecretpasssword", "sec": 7, "ssid": "575757"}}}'},  # ssid as hex ("WWW" here)
    #{'topic':"wifictl", 'payload':'{ "state" : { "utctime" : 1579291795 } }'},
    #{'topic':"wifictl", 'payload':'{ "state" : { "localtimeoffset" : 60 } }'},
    {'topic':"wifictl", 'payload':'{ "state" : { "chkssid" : true } }'},
    {'topic':"wifictl", 'payload':'{ "state" : { "wactivate" : true } }'},
    {'topic':"wifictl", 'payload':'{ "state" : { "get" : "netinfo" } }'},
    {'topic':"wifictl", 'payload':'{ "state" : { "uap" : false } }'},
]

# voodoo packet?
MAGIC_PACKET=b'\xef\xcc\x3b\x29\x00'

# format:  :1:timestamp:16 alpha-decimal chars
PASSWORD=b':1:1579195386:8fx7nYqVtKgWJ9tO'

HOST="192.168.10.1"
PORT=8883

def provision_password():
    payload=MAGIC_PACKET+PASSWORD
    authentication_exchange=b'\xf0'+bytes([len(payload)])+payload

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    wrappedSocket = ssl.wrap_socket(sock, ssl_version=ssl.PROTOCOL_TLS, ciphers='DEFAULT@SECLEVEL=1')

    try:
        wrappedSocket.connect((HOST, PORT))
    except Exception as e:
        print("Connection Error %s" % e)

    wrappedSocket.send(authentication_exchange)

    data = b''
    data_len = len(payload)
    while True:
        try:
            # NOTE data is 0xf0 (mqtt RESERVED) length (0x23 = 35),
            # 0xefcc3b2900 (magic packet), 0xXXXX... (30 bytes of
            # password). so 7 bytes, followed by 30 bytes of password
            # (total of 37)
            if len(data) >= data_len+2:
                break
            data_received = wrappedSocket.recv(1024)
            print("received data: hex: %s, length: %d" % (binascii.hexlify(data_received), len(data_received)), flush=True)
        except socket.error as e:
            print("Socket Error: %s" % e)
            break

        if len(data_received) == 0:
            print("socket closed")
            break
        else:
            data += data_received
            if len(data) >= 2:
                data_len = struct.unpack("B", data[1:2])[0]

    wrappedSocket.close()
    print("received data: hex: %s, length: %d" % (binascii.hexlify(data), len(data)))

    if len(data) <= 7:
        print('Error setting password, receive %d bytes. Follow the '
              'instructions and try again.' % len(data))
        sys.exit(1)
    time.sleep(2)

def provision_wifi():
    client = mqtt.Client('0000000000000000')
    client.tls_set(ca_certs='/path/to/robot-ca.pem', cert_reqs=ssl.CERT_NONE)
    client.tls_insecure_set(True)
    client.username_pw_set('0000000000000000', PASSWORD)
    client.tls_insecure_set(True)
    client.connect("192.168.10.1", 8883, 60)
    
    for msg in msgs:
        print('Sending:', msg['topic'], msg['payload'], flush=True)
        client.publish(msg['topic'], msg['payload'])
        time.sleep(1)
      
    client.disconnect()
    


def main():
    provision_password()
    provision_wifi()

if __name__ == "__main__":
    main()

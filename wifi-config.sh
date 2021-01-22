#!/bin/bash

ROOMBA_PASSWORD=:1:1579195386:8fx7nYqVtKgWJ9tO
BLID=80A7001234567890
IP=192.168.10.1
MOSQUITTO="mosquitto_pub -L mqtts://$BLID@$IP:8883/  --insecure  -P $ROOMBA_PASSWORD  -V mqttv311 --cafile robot-ca.pem -i $BLID --ciphers DEFAULT@SECLEVEL=1 -d"

# Define password
echo -n "f023efcc3b29003a313a313537393139353338363a386678376e597156744b67574a39744f" | xxd -r -p | openssl s_client -CAfile robot-ca.pem -connect $IP -quiet -noservername

$MOSQUITTO -t delta -m '{ "state" : { "timezone" : "Europe/Paris" } }' ; sleep 1
$MOSQUITTO -t delta -m '{ "state" : {"country" : "FR"} }' ; sleep 1
$MOSQUITTO -t wifictl -m '{"state": {"wlcfg": {"pass": "wifisecretpasssword", "sec": 7, "ssid": "54657374"}}}' ; sleep 1
$MOSQUITTO -t wifictl -m '{ "state" : { "chkssid" : true } }' ; sleep 1
$MOSQUITTO -t wifictl -m '{ "state" : { "wactivate" : true } }' ; sleep 1
$MOSQUITTO -t wifictl -m '{ "state" : { "get" : "netinfo" } }' ; sleep 1
$MOSQUITTO -t wifictl -m '{ "state" : { "uap" : false } }' ; sleep 1


import network
import time
import ujson
from machine import Pin
from mfrc522 import MFRC522
from umqtt.simple import MQTTClient

# --- 1. NETWORK SETUP ---
SSID, PASSWORD = "EdNet", "Huawei@123"
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)
while not wlan.isconnected(): time.sleep(1)
print("WiFi Connected! IP:", wlan.ifconfig()[0])

# --- 2. CONFIG ---
TEAM_ID = "ubuliza_david"
MQTT_BROKER = "157.173.101.159"
pending_amount = 0
should_write = False
KEY = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

# Pins for YOUR library: sck, mosi, miso, rst, cs(sda)
# According to your library __init__: (self, sck, mosi, miso, rst, cs)
rdr = MFRC522(14, 13, 12, 5, 4)

def on_message(topic, msg):
    global pending_amount, should_write
    try:
        data = ujson.loads(msg)
        pending_amount = int(data['amount'])
        should_write = True
        print("\n[MQTT] Top-up command received!")
    except: pass

client = MQTTClient(TEAM_ID, MQTT_BROKER)
client.set_callback(on_message)
client.connect()
client.subscribe("rfid/{}/card/topup".format(TEAM_ID))

print("System Live. Scan Card...")

# --- 3. MAIN LOOP ---
while True:
    try:
        client.check_msg()
        (stat, tag_type) = rdr.request(rdr.REQIDL)
        
        if stat == rdr.OK:
            (stat, raw_uid) = rdr.anticoll()
            if stat == rdr.OK:
                # 1. Select the tag first (Required by your library's structure)
                if rdr.select_tag(raw_uid) == rdr.OK:
                    
                    # 2. AUTHENTICATE (Matching your 4-arg signature: mode, addr, sect, ser)
                    # addr=8, sect=KEY, ser=raw_uid
                    if rdr.auth(rdr.AUTHENT1A, 8, KEY, raw_uid) == rdr.OK:
                        
                        # 3. WRITE LOGIC
                        if should_write:
                            buf = [0]*16
                            buf[0:4] = [(pending_amount >> 24) & 0xFF, (pending_amount >> 16) & 0xFF, (pending_amount >> 8) & 0xFF, pending_amount & 0xFF]
                            if rdr.write(8, buf) == rdr.OK:
                                print("SUCCESS: Physical Write OK")
                                should_write = False
                            else:
                                print("Write Error")

                        # 4. READ LOGIC
                        block_data = rdr.read(8)
                        if block_data is not None:
                            balance = (block_data[0]<<24 | block_data[1]<<16 | block_data[2]<<8 | block_data[3])
                            uid_str = "0x%02x%02x%02x%02x" % (raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3])
                            payload = ujson.dumps({"uid": uid_str, "balance": balance, "team": TEAM_ID})
                            client.publish("rfid/{}/card/status".format(TEAM_ID), payload)
                            print("UID:", uid_str, "Balance:", balance)
                        
                        rdr.stop_crypto1()
                
                time.sleep(1)
    except Exception as e:
        print("Error:", e)
        time.sleep(1)
    time.sleep(0.1)
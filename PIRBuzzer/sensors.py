#from flask import Flask, render_template
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
import os
from dotenv import load_dotenv
from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory, PNOperationType
import json
import RPi.GPIO as GPIO
import time, threading
import requests

load_dotenv()

response = requests.get('https://sd3b.online/get_device_token-12345')
token = response.json()
print(token)
pnconfig = PNConfiguration()



pnconfig.subscribe_key = os.environ.get('PUBNUB_SUBSCRIBE_KEY')
pnconfig.publish_key = os.environ.get('PUBNUB_PUBLISH_KEY')
pnconfig.user_id = "12345"
pnconfig.auth_key = token
pubnub = PubNub(pnconfig)


my_channel = "johns_sd3b_pi"

def my_publish_callback(envelope, status):
    #Check whether request successfully completed or not
    if not status.is_error():
        pass
    else:
        pass


class MySubscribeCallback(SubscribeCallback):
    def presense(self, pubnub, presence):
        pass

    def status(self, pubnub, status):
        if status.category == PNStatusCategory.PNUnexpectedDisconnectCategory:
            pass
        elif status.category == PNStatusCategory.PNConnectedCategory:
            #pubnub.publish().channel(my_channel).message("Hello world").pn_async(my_publish_callback)
            print("Connected to channel")
            pass
        elif status.category == PNStatusCategory.PNDecryptionErrorCategory:
            pass

    def message(self, pubnub, message):
        print(message.message)
        received = message.message
        if "buzzer" in received.keys():
            if received["buzzer"] == "on":
                data["alarm"] = True
            else:
                data["alarm"] = False

pubnub.add_listener(MySubscribeCallback())

def publish(channel, message):
    pubnub.publish().channel(channel).message(message).pn_async(my_publish_callback)


#app = Flask(__name__)
alive = 0
data = {}

PIR_pin = 23
Buzzer_pin = 24

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_pin, GPIO.IN)
GPIO.setup(Buzzer_pin, GPIO.OUT)

def beep(repeat):
    for i in range(0, repeat):
        for pulse in range(60):
            GPIO.output(Buzzer_pin, True)
            time.sleep(0.001)
            GPIO.output(Buzzer_pin, False)
            time.sleep(0.001)
        time.sleep(0.02)



def motion_detection():
    data["alarm"] = False
    trigger = False
    while True:
        if GPIO.input(PIR_pin):
            print("Motion detected")
            beep(4)
            publish(my_channel, {"motion":"Motion Detected"})
            trigger = True
        elif trigger:
            publish(my_channel, {"motion":"No Motion Detected"})
            trigger = False
        if data["alarm"]:
            beep(2)
        time.sleep(1)


#@app.route("/")
#def index():
#    return render_template("index.html")


#@app.route("/keep_alive")
#def keep_alive():
#    global alive, data
#    alive += 1
#    keep_alive_count = str(alive)
#    data['keep_alive'] = keep_alive_count
#    parsed_json = json.dumps(data)
#    return str(parsed_json)


#@app.route("/status=<name>-<action>", methods=["POST"])
#def event(name, action):
#    global data
#    if name == "buzzer":
#        if action == "on":
#            data["alarm"] = True
#        elif action == "off":
#            data["alarm"] = False
#    return str("Ok")


if __name__ == '__main__':
    sensorsThread = threading.Thread(target=motion_detection)
    sensorsThread.start()
    pubnub.subscribe().channels(my_channel).execute()

from paho.mqtt import client as mqtt_client
from ATserial import AtCommand as atc
from ATserial import findPort
import json
import requests
import pyttsx3
import time


class Call():
    def __init__(self, at):
        self.at = at
        self.port = 1883
        self.broker = '119.91.198.5'
        self.topic = "/call"
        self.client_id = 'SERVER'
        self.mapurl = 'http://map.puqing.work/index.html?'
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        self.dangerVoice = "您好，我是智能汽车辅助系统，您被绑定的驾驶员出现危险情况，请即时确定驾驶员情况，他的位置信息将通过短信发送给您，请注意查收。"
        self.client = self.connect_mqtt()
        self.subscribe()
        self.client.loop_forever()

    def generateShortLink(self, long_link):
        """
        Generate short link
        """
        try:
            response = requests.get(
                'https://ock.cn/api/short?token=62515c3686d74&longurl=' +
                long_link)
            response = json.loads(response.text)
            if response['code'] == 1000:
                return response['data']['short']
            else:
                return None
        except Exception as e:
            print(e)
            return None

    def sendDangerMessage(self, contacts, longitude, latitude):
        """
        Send danger message to contacts
        params:
            contacts: the phone number of the contacts
            longitude: the longitude of the driver
            latitude: the latitude of the driver
        """
        short_url = self.generateShortLink(self.mapurl + '(' + str(longitude) +
                                           ',' + str(latitude) + ')')
        if short_url is not None:
            # set the SMS center
            # if you want to send message in other place, please change this
            self.at.send_at('AT+CSCA="+8613800773500"')
            self.at.check_at_resp('OK')

            self.at.send_at('AT+CMGF=1')
            self.at.check_at_resp('OK')

            self.at.send_at('AT+CMGS="' + contacts + '"')
            self.at.check_at_resp('>')

            self.at.send_at('Your bound driver is in danger.')
            self.at.send_at('You can find he/she at ' + short_url)

            self.at.send_at_notn('\x1a')
            self.at.check_at_resp('OK')

    def callPhone(self, contacts):
        """
        Call the phone
        """
        self.at.send_at('ATD' + contacts + ';')
        self.at.check_at_resp('OK')

        start_time = time.time()
        while True:
            # If the dialed number times out or the call is disconnected,
            # the phone will be hang up
            if time.time() - start_time >= 30:
                self.at.send_at('ATH')
                self.at.check_at_resp('OK')
                break
            if self.at.check_at_resp('OK'):
                print('Ready to speak...')
                i = 0
                while i < 3:
                    # If the call is connected, the phone will speak
                    self.at.send_at('AT+CLCC')
                    # If the call is disconnected, the phone will be hang up
                    if self.at.check_at_resp('NO CARRIER') is None:
                        self.engine.say(self.dangerVoice)
                        self.engine.runAndWait()
                        i += 1
                    else:
                        break

    def connect_mqtt(self):
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
            else:
                print("Failed to connect, return code %d\n", rc)

        client = mqtt_client.Client(self.client_id)
        client.on_connect = on_connect
        client.connect(self.broker, self.port)
        return client

    def subscribe(self):
        def on_message(client, userdata, msg):
            msg = msg.payload.decode()
            json_msg = json.loads(msg)
            contacts = json_msg['contacts'].replace('"', '')
            longitude = json_msg['longitude']
            latitude = json_msg['latitude']
            print("The contacts is: ", contacts)
            print("The longitude is :", longitude)
            print("The latitude is :", latitude)

            self.sendDangerMessage(contacts, longitude, latitude)

            self.callPhone(contacts)

        self.client.subscribe(self.topic)
        self.client.on_message = on_message


if __name__ == '__main__':
    port = findPort()
    if port is None:
        print("Can't find the port!")
        exit(1)
    print("The L610 port is: ", port)

    at = atc()
    at.open(port)

    call = Call(at)

    at.close()

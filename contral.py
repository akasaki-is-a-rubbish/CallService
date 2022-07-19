import numpy as np
import serial
import serial.tools.list_ports
import re
from paho.mqtt import client as mqtt_client
import pyttsx3
import matplotlib.pyplot as plt

# plt.ion()
plt.figure(1)
mngr = plt.get_current_fig_manager()
mngr.window.wm_geometry("+1380+0")
t = np.zeros(10)
i = 0
LAST_STATUS = False
LAST_DATA = 0


class Contral:
    def __init__(self):
        self.ser = serial.Serial(Contral.findPort(), timeout=1, baudrate=115200)
        self.client_id = "contral_client"
        self.broker = "broker-cn.emqx.io"
        self.port = 1883
        self.client = self.connect_mqtt()
        self.topic = "/call"
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", 180)
        self.dangerVoice = "喝酒不开车，开车不喝酒。"
        if self.is_open():
            print("Serial port is open")
            self.run()
        else:
            print("Serial port is not open")

    def __del__(self):
        self.ser.close()
        self.client.disconnect()

    def publish(self):
        message = '{"contacts":"18273623931"}'
        self.client.publish(self.topic, message)

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

    def is_open(self):
        return self.ser.is_open

    def run(self):
        global LAST_STATUS, LAST_DATA, t, i
        while True:
            line = self.ser.readline()
            if line:
                line.decode("ascii", "ignore")
                line = str(line, "utf-8")
                line = line.replace("\r\n", "")
                data = line[line.find(":") + 1 :]
                expression = "".join(re.findall(r"[A-Za-z]", line))
                if expression == "alcohol":
                    print("alcohol-->", float(data))
                    t = np.roll(t, -1)
                    t[9] = float(data)
                    print("t-->", t)
                    plt.clf()
                    plt.plot(t, "r")
                    plt.pause(0.01)
                    plt.draw()
                    if (
                        float(data) > 40
                        and LAST_STATUS is False
                        and LAST_DATA < float(data)
                    ):
                        LAST_STATUS = True
                        LAST_DATA = float(data)
                        self.engine.say(self.dangerVoice)
                        self.engine.runAndWait()
                        # self.publish()
                        print("publish")
                    elif float(data) < 200:
                        LAST_STATUS = False
                        LAST_DATA = float(data)
                    elif float(data) == LAST_DATA:
                        pass
                    else:
                        LAST_DATA = float(data)

    def findPort():
        ports = serial.tools.list_ports.comports()
        for each in ports:
            print(each.description)
            if "CP210x USB to UART" in each.description:
                return each.device


if __name__ == "__main__":
    con = Contral()

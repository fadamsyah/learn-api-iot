"""
Arduino:
    DHT unit:
        - Humidity    : %
        - Temperature : C
    DHT Status Code:
        - 200 : Success
        - 400 : Gagal baca temperature dan humidity
        - 401 : Berhasil baca temperatur tapi humidity gagal
        - 402 : Gagal baca temperature tapi humidity berhasil

RabbitMQ:
    host: localhost
    port: 5672
    exchange: arduino
    exchange_type: direct
    DHT
        routing_key: dht
        msg: "YYYY-MM-DD HH:MM:SS|<status>|<humidity>|<celcius>"
"""

import pika
import serial
import time
import yaml

from datetime import datetime

class ArduinoNode:
    def __init__(self, port, baudrate=57600):
        self.ser = serial.Serial(port, baudrate=baudrate)
        self.ser.flushInput()
    
    def close(self):
        self.ser.close()
    
    def get_dht(self):
        msg = 'get dht' + '\n'
        self.ser.write(msg.encode())
        
        res = self.ser.readline().decode("utf-8")
        status, humidity, celcius = res.split('|')
        humidity = float(humidity)
        celcius  = float(celcius)
        
        return status, humidity, celcius

config   = yaml.safe_load(open('config.yml').read())['arduino']
port     = config['port']
baudrate = config['baudrate']
cfg_dht  = config['dht']
node     = ArduinoNode(port, baudrate)

if __name__ == '__main__':
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', port=5672))
    channel    = connection.channel()
    channel.exchange_declare(exchange='arduino', exchange_type='direct')
    
    rh_t_last = time.time()
    while True:
        time.sleep(2 / 1000) # 2 ms
        if (time.time() - rh_t_last) >= cfg_dht['sampling_time']:
            rh_t_last = time.time()
            status, humidity, celcius = node.get_dht()
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            msg = f"{now}|{status}|{humidity}|{celcius}"
            channel.basic_publish(exchange='arduino', routing_key='dht', body=msg)
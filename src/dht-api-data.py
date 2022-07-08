import pika
import sqlite3
from datetime import datetime
from flask import Flask, jsonify, request
from threading import Thread

app = Flask(__name__)

LIST_TIME     = []
LIST_TIME_RAW = []
LIST_CELCIUS  = []
LIST_HUMIDITY = []

def callback(ch, method, properties, body):
    global DATA
    
    msg = body.decode()
    now, status, humidity, celcius = msg.split('|')
    
    status   = int(status)
    humidity = float(humidity)
    celcius  = float(celcius)
    
    if status != 200:
        return
    
    LIST_TIME_RAW.append(now)
    LIST_CELCIUS.append(celcius)
    LIST_HUMIDITY.append(humidity)
    
    now = now.replace('-', '').replace(':', '').replace(' ', '')
    LIST_TIME.append(now)

def find_start_and_end_index(list_time, t_start, t_end):
    if (t_end >= list_time[-1]):
        i_end = len(list_time)
    elif (t_end < list_time[0]):
        i_end = None
    elif (t_end == list_time[0]):
        i_end = 1
    else:
        for i in list(reversed(range(len(list_time)))):
            if (t_end >= list_time[i]):
                i_end = i
                break
    
    if (t_start <= list_time[0]):
        i_start = 0
    elif (t_start > list_time[-1]):
        i_start = None
    elif (t_start == list_time[-1]):
        i_start = len(list_time) - 1
    else:
        for i in list(reversed(range(i_end))):
            if (t_start >= list_time[i]):
                i_start = i
                break
    
    return i_start, i_end

@app.route('/get_dht', methods=['POST'])
def get_dht():
    if request.method != 'POST':
        return
    
    global LIST_TIME, LIST_TIME_RAW, LIST_CELCIUS, LIST_HUMIDITY
    
    data    = request.json
    t_start = data['t_start'].replace('-', '').replace(':', '').replace(' ', '')
    t_end   = data['t_end'].replace('-', '').replace(':', '').replace(' ', '')
    
    if (len(LIST_TIME) == 0) or (t_start > t_end):
        return jsonify({
            'list_time'    : [],
            'list_time_raw': [],
            'list_celcius' : [],
            'list_humidity': [],
        }), 200
    
    i_start, i_end = find_start_and_end_index(LIST_TIME, t_start, t_end)
    
    result = {
        'list_time'    : LIST_TIME[i_start:i_end],
        'list_time_raw': LIST_TIME_RAW[i_start:i_end],
        'list_celcius' : LIST_CELCIUS[i_start:i_end],
        'list_humidity': LIST_HUMIDITY[i_start:i_end],
    }
    
    return jsonify(result), 200

if __name__ == '__main__':
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', port=5672))
    channel    = connection.channel()
    channel.exchange_declare(exchange='arduino', exchange_type='direct')
    queue_dht = channel.queue_declare(queue='', exclusive=True)
    channel.queue_bind(exchange='arduino', queue=queue_dht.method.queue, routing_key='dht')
    channel.basic_consume(queue=queue_dht.method.queue, on_message_callback=callback, auto_ack=True)
    
    consumer_thread = Thread(target=channel.start_consuming)
    consumer_thread.start()
    
    app.run(port='5001')
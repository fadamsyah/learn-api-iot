import pika
import sqlite3

def callback(ch, method, properties, body):
    msg = body.decode()
    now, status, humidity, celcius = msg.split('|')
    
    status   = int(status)
    humidity = float(humidity)
    celcius  = float(celcius)
    now_date = now.split(' ')[0]
    now_date = 'D_' + now_date.replace('-', '_')
    
    conn   = sqlite3.connect('dht.db')
    cursor = conn.cursor()
    cursor.execute(
        f"CREATE TABLE IF NOT EXISTS {now_date}" + """ (
        time TIMESTAMP PRIMARY KEY,
        status INT NOT NULL,
        humidity FLOAT NOT NULL,
        celcius FLOAT NOT NULL
        );""",
    )
    cursor.execute(
        f"INSERT INTO {now_date}" + """ (time, status, humidity, celcius)
        VALUES (?, ?, ?, ?)
        ;""",
        (now, status, humidity, celcius)
    )
    
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == '__main__':
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', port=5672))
    channel    = connection.channel()
    channel.exchange_declare(exchange='arduino', exchange_type='direct')
    queue_dht = channel.queue_declare(queue='', exclusive=True)
    channel.queue_bind(exchange='arduino', queue=queue_dht.method.queue, routing_key='dht')
    channel.basic_consume(queue=queue_dht.method.queue, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()
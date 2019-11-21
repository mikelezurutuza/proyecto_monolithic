import pika
import json


def publish(exchange, queue, message):
    credentials = pika.PlainCredentials('guest', 'guest')
    parameters = pika.ConnectionParameters('192.168.17.4', 5672, '/', credentials)
    connection = pika.BlockingConnection(parameters)

    channel = connection.channel()

    channel.exchange_declare(exchange=exchange, exchange_type='direct')
    print(exchange + '  ' + queue + '    ' +json.dumps(message), flush=True)
    channel.basic_publish(exchange=exchange, routing_key=queue, body=json.dumps(message))
    connection.close()
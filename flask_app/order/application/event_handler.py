import threading

import pika
import json

from .orchestrator import get_orchestrator
from .models import Order
from . import Session
from .event_publisher import publish


class Rabbit():
    def __init__(self, exchange, queue, which):
        # Rabbit config
        credentials = pika.PlainCredentials('guest', 'guest')
        parameters = pika.ConnectionParameters('192.168.17.4', 5672, '/', credentials)
        connection = pika.BlockingConnection(parameters)
        self.channel = connection.channel()
        self.channel.exchange_declare(exchange=exchange, exchange_type='direct')
        self.declare_queue(exchange, queue, which)
        #Lo suyo sería tener un thread por cada queue
        thread = threading.Thread(target=self.channel.start_consuming)
        thread.start()
        thread.join(0)

    def declare_queue(self, exchange_name, routing_key, which):
        result = self.channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue
        self.channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key=routing_key)
        self.channel.basic_consume(queue=queue_name, on_message_callback=which, auto_ack=True)
        # self.channel.start_consuming()

    @staticmethod
    def machine_response(ch, method, properties, body):
        print('MACHINE CALLBACK, LLAMANDO A DELIVERY', flush=True)
        # Crear el delivery
        body = json.loads(body)
        print(body, flush=True)
        body['delivered'] = True
        print(body, flush=True)
        publish('delivery_event_exchange', 'delivery_update_event_queue', body)

    @staticmethod
    def sagas_response(ch, method, properties, body):
        print('SAGAS CALLBACK', flush=True)
        body= json.loads(body)
        orchestrator = get_orchestrator()
        orchestrator.treat_message(body)
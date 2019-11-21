import threading

import pika
import json

from .models import Piece
from . import Session
from .machine import Machine

my_machine = Machine()

class Rabbit():
    def __init__(self):
        # Rabbit config
        exchange_name = 'machine_event_exchange'
        credentials = pika.PlainCredentials('guest', 'guest')
        parameters = pika.ConnectionParameters('192.168.17.4', 5672, '/', credentials)
        connection = pika.BlockingConnection(parameters)
        self.channel = connection.channel()
        self.channel.exchange_declare(exchange=exchange_name, exchange_type='direct')
        self.declare_queue(exchange_name, 'machine_event_queue')
        #Lo suyo sería tener un thread por cada queue
        thread = threading.Thread(target=self.channel.start_consuming)
        thread.start()
        thread.join(0)

    def declare_queue(self, exchange_name, routing_key):
        result = self.channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue
        self.channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key=routing_key)
        self.channel.basic_consume(queue=queue_name, on_message_callback=self.callback, auto_ack=True)
        # self.channel.start_consuming()

    @staticmethod
    def callback(ch, method, properties, body):
        session = Session()
        status = False
        body = json.loads(body)
        try:
            number_of_pieces = body['num_pieces']
            orderId = body['orderId']

            pieces_list = list()
            for _ in range(number_of_pieces):
                piece = Piece()
                piece.orderId = orderId
                session.add(piece)
                session.commit()
                session.refresh(piece)
                print(piece, flush=True)
                pieces_list.append(piece)

            if pieces_list:  # miramos si hay elemento en la lista.
                print('hay elementos', flush=True)
                my_machine.add_pieces_to_queue(pieces_list)

        except KeyError:
            session.rollback()
            session.close()

        session.close()

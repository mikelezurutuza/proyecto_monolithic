import threading

import pika
import json

from sqlalchemy.orm.exc import NoResultFound

from .models import Payment
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
    def reserve(ch, method, properties, body):
        print(body, flush=True)
        session = Session()
        status = True
        print('Llegamos', flush=True)
        body = json.loads(body)
        money = body['num_pieces'] * 2
        try:
            try:
                user = session.query(Payment).filter(Payment.userId == body['userId']).one()
                if user.money < money:
                    raise NoResultFound("No tiene dinero suficiente")
                user.money -= money
                user.reserved_money = money
                session.commit()

                body['status']=status
                body['tipo']="PAYMENT"
                print(body, flush=True)

            except NoResultFound:
                print("no tiene dinero", flush=True)
                status = False
            finally:
                publish('order_event_exchange', 'sagas_queue', body)

        except KeyError:
            session.rollback()
        session.close()

    @staticmethod
    def cancelled(ch, method, properties, body):
        print(body, flush=True)
        session = Session()
        print('Llegamos', flush=True)
        body = json.loads(body)
        money = body['num_pieces'] * 2
        try:
            try:
                user = session.query(Payment).filter(Payment.userId == body['userId']).one()
                user.reserved_money -= money
                user.money += money
                session.commit()

                print(body, flush=True)

            except NoResultFound:
                print("no tiene dinero", flush=True)

        except KeyError:
            session.rollback()
        session.close()
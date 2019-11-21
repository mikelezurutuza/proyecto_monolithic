import threading
import pika
from sqlalchemy.orm.exc import NoResultFound

from .event_publisher import publish
from . import Session
import json
from .models import Delivery

class Rabbit():
    def __init__(self, queue, which):
        # Rabbit config
        exchange_name = 'delivery_event_exchange'
        credentials = pika.PlainCredentials('guest', 'guest')
        parameters = pika.ConnectionParameters('192.168.17.4', 5672, '/', credentials)
        connection = pika.BlockingConnection(parameters)
        self.channel = connection.channel()
        self.channel.exchange_declare(exchange=exchange_name, exchange_type='direct')
        self.declare_queue(exchange_name, queue, which)
        thread = threading.Thread(target=self.channel.start_consuming)
        thread.start()
        thread.join(0)

    def declare_queue(self, exchange_name, routing_key, which):
        result = self.channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue
        self.channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key=routing_key)
        #Si pongo un queuename personalizado da 404 el docker, no sé por qué
        self.channel.basic_consume(queue=queue_name, on_message_callback=which, auto_ack=True)
        # self.channel.start_consuming()

    @staticmethod
    def create_callback(ch, method, properties, body):
        print('CREATE CALLBACK', flush=True)
        session = Session()
        new_delivery = None
        status = True
        body = json.loads(body)
        print(body, flush=True)
        try:
            new_delivery = Delivery(
                orderId=body['orderId'],
                delivered= False,
            )

            if body["zip"] == "01" or body["zip"] == "48" or body["zip"] == "20":
                session.add(new_delivery)
                session.commit()
            else:
                status = False

        except KeyError:
            status = False
            session.rollback()
        body["status"]=status
        body['tipo'] = "DELIVERY"
        publish('order_event_exchange', 'sagas_queue', body)
        session.close()

    @staticmethod
    def cancel_callback(ch, method, properties, body):
        print('CANCEL CALLBACK', flush=True)
        session = Session()
        body = json.loads(body)
        print(body, flush=True)
        try:
            session.query(Delivery).filter(Delivery.orderId == body['orderId']).one().delete()
        except KeyError:
            session.rollback()
        session.close()

    @staticmethod
    def update_callback(ch, method, properties, body):
        print("UPDATE CALLBACK", flush=True)
        session = Session()
        content = json.loads(body)

        try:
            new_delivery = Delivery(
                orderId=content['orderId'],
                delivered=True,
            )
            try:
                delivery = session.query(Delivery).filter(Delivery.orderId == new_delivery.orderId).one()
                delivery.delivered = new_delivery.delivered
                print(delivery)
                session.commit()
            except NoResultFound:
                print("no existe el pedido")
        except KeyError:
            session.rollback()

        session.close()
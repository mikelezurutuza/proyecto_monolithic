import json

from .event_publisher import publish

class Orchestrator(object):

    def __init__(self):
        self.order_list = list()

    def treat_message(self, body):
        order_state = self.get_order(body['orderId'])

        if "PAYMENT" == body['tipo']:
            order_state.treat_payment(body)
        if "DELIVERY" == body['tipo']:
            order_state.treat_delivery(body)

        if order_state.p_state.get_state() == "ACCEPTED" and order_state.d_state.get_state() == "ACCEPTED":
            publish('machine_event_exchange', 'machine_event_queue', body)
            self.order_list.remove(order_state)
        elif order_state.p_state.get_state() == "CANCELLED" or order_state.d_state.get_state() == "CANCELLED":
            publish('payment_event_exchange', 'payment_cancel_queue', body)
            publish('delivery_event_exchange', 'delivery_cancel_event_queue', body)
            self.order_list.remove(order_state)

    def get_order(self, orderId):
        response = None
        for i in self.order_list:
            if i.orderId == orderId:
                response = i
        return response

orchestrator = Orchestrator()
def get_orchestrator():
    return orchestrator
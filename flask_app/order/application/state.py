class OrderState(object):
    def __init__(self, orderId, pieces, userId):
        self.orderId = orderId
        self.pieces = pieces
        self.userId = userId
        self.p_state = Pending_state()
        self.d_state = Pending_state()
        self.tipo = None

    def treat_payment(self, body):
        if body["status"]:
            self.p_state = Accepted_state()
        else:
            self.p_state = Cancelled_state()

    def treat_delivery(self, body):
        if body["status"]:
            self.d_state = Accepted_state()
        else:
            self.d_state = Cancelled_state()

class State(object):
    def get_state(self):
        return "STATE"

class Pending_state(State):
    def get_state(self):
        return "PENDING"

class Accepted_state(State):
    def get_state(self):
        return "ACCEPTED"

class Cancelled_state(State):
    def get_state(self):
        return "CANCELLED"
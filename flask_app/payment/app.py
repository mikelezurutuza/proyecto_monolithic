from application import create_app
from application.event_handler import Rabbit

app = create_app()
app.app_context().push()
Rabbit('payment_event_exchange', 'payment_reserve_queue', Rabbit.reserve)
Rabbit('payment_event_exchange', 'payment_cancel_queue', Rabbit.cancelled)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=17000)

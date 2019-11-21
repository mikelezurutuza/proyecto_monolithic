from application import create_app
from application.event_handler import Rabbit

app = create_app()
app.app_context().push()
Rabbit('delivery_create_event_queue', Rabbit.create_callback)
Rabbit('delivery_cancel_event_queue', Rabbit.cancel_callback)
Rabbit('delivery_update_event_queue', Rabbit.update_callback)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=14000)

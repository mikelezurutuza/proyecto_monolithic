from application import create_app
from application.event_handler import Rabbit

app = create_app()
app.app_context().push()
Rabbit('order_event_exchange', 'machine_response_queue', Rabbit.machine_response)
Rabbit('order_event_exchange', 'sagas_queue', Rabbit.sagas_response)



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=16000)


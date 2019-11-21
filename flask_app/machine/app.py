from application import create_app
from application.event_handler import Rabbit

app = create_app()
app.app_context().push()
Rabbit()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=15000)

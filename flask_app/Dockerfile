FROM python:3.6
ADD ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt

ENTRYPOINT gunicorn -b 0.0.0.0:${GUNICORN_PORT} app:app

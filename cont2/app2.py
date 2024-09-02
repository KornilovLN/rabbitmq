import pika
import json
import sys

def prepare_all():
    connection_params = pika.ConnectionParameters(
        host='rabbitmq',
        credentials=pika.PlainCredentials('rmuser', 'rmpassword'),
        connection_attempts=10,
        retry_delay=5
    )
    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()
    channel.queue_declare(queue='my_queue')
    return connection, channel

def send_message(channel, container_name, app_name, message_name, message_data, target):
    message = {
        "cont": container_name,
        "app": app_name,
        "message": {
            "name": message_name,
            "data": message_data
        },
        "target": target
    }
    channel.basic_publish(exchange='', routing_key='my_queue', body=json.dumps(message))
    print(f"Отправлено сообщение: {message}", file=sys.stderr)

def callback(ch, method, properties, body, channel):
    message = json.loads(body)
    print(f"Получено сообщение: {message}", file=sys.stderr)
    if message['cont'] == 'cont1' and message['target'] == 'cont2':
        data = int(message['message']['data']) * 10
        send_message(channel, "cont2", "app2.py", "counter", data, 'cont3')

def main():
    print("Скрипт запущен", file=sys.stderr)
    connection, channel = prepare_all()

    on_message_callback = lambda ch, method, properties, body: callback(ch, method, properties, body, channel)
    channel.basic_consume(queue='my_queue', on_message_callback=on_message_callback, auto_ack=True)
    try:
        print("Начало потребления сообщений", file=sys.stderr)
        channel.start_consuming()
    except KeyboardInterrupt:
        print("Программа остановлена пользователем", file=sys.stderr)
    finally:
        connection.close()

if __name__ == "__main__":
    print("Начало выполнения скрипта app2.py", file=sys.stderr)
    main()


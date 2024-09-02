import pika
import json
import time
import sys

# app3.py

connection = None
channel = None

def prepare_all():
    global connection, channel
    # Инициализация подключения к RabbitMQ
    connection_params = pika.ConnectionParameters(
        host='rabbitmq',
        credentials=pika.PlainCredentials('rmuser', 'rmpassword'),
        connection_attempts=10,
        retry_delay=5
    )
    # Устанавливаем соединение с RabbitMQ
    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()
    # Объявляем очередь
    channel.queue_declare(queue='my_queue')
    # Подписываемся на очередь для получения сообщений
    channel.basic_consume(queue='my_queue', on_message_callback=callback, auto_ack=True)


# Функция для отправки сообщения
def send_message(container_name, app_name, message_name, message_data, target):
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


def callback(ch, method, properties, body):
    message = json.loads(body)
    return message



def process_message(message):
    if message['cont'] == 'cont2':  # Проверяем, что сообщение от второго контейнера
#        counter = int(message['message']['data']) - 10
#        send_message("cont3", "app3.py", "counter-minus10", counter, target='cont1')
        print(f"Получено: {message['message']['data']}", file=sys.stderr)
    return message




def main():
    print(f"До prepare_all()", file=sys.stderr) 
    prepare_all()

    print(f"До while True:", file=sys.stderr) 
    while True:
        # Ожидание сообщения от второго контейнера
        method_frame, header_frame, body = channel.basic_get(queue='my_queue', auto_ack=True)
        
        print(f"До проверки body") 
        if body:
            received_message = callback(None, None, None, body)
            processed_message = process_message(received_message)
            
            # Извлечение счетчика и вычитание 10
            counter = int(received_message['message']['data']) - 10
            
            # Отправка сообщения третьему контейнеру
            send_message("cont3", "app3.py", "counter-minus10", counter, "cont1")
            
            print(f"Получено: {received_message['message']['data']}, Отправлено: {counter}", file=sys.stderr)
        
        time.sleep(1)  # Небольшая задержка для избежания перегрузки


if __name__ == "__main__":
    print(f"До main()", file=sys.stderr) 
    try:
        main()
    except KeyboardInterrupt:
        print("Программа остановлена пользователем")
    finally:
        if connection:
            connection.close()


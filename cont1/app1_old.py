import pika
import json
import time
import sys

# app1.py

global connection
global channel

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
    print(f"Отправлено сообщение: {message}")


# Функция получения и, если надо, обработки сообщения
def callback(ch, method, properties, body):
    message = json.loads(body)
    return message


def process_message(message):
    # Проверяем, что сообщение от третьего контейнера
    if message['cont'] == 'cont3':  
        get_data = int(message['message']['data']) 
        print(f"Получено: {get_data}", file=sys.stderr)        
    return message


def main():
    print("Скрипт  запущен", file=sys.stderr)
    prepare_all()

    # Самая первая отправка сообщения второму контейнеру, который
    # должен умножить счетчик на 10 и отправить сообщение в 3-й контейнер
    counter = 0
    send_message("cont1", "app1.py", "counter", counter, 'cont2')

    print(f"Метка отладки: До while", file=sys.stderr)
    while True:
  
        # Ожидание сообщения от третьего контейнера
        method_frame, header_frame, body = channel.basic_get(queue='my_queue', auto_ack=True)
        
        if body:
            received_message = callback(None, None, None, body)
            processed_message = process_message(received_message)
            
            # Вывод в консоль отправленного и полученного сообщения
            print(f"Отправлено: {counter}, Получено: {received_message['message']['data']}", file=sys.stderr)
            
            # Увеличение исходного счетчика и отправка сообщения 2-му контейнеру
            counter += 1
            send_message("cont1", "app1.py", "counter", counter, 'cont2')
        
        time.sleep(1)  # Небольшая задержка для избежания перегрузки


if __name__ == "__main__":
    print("Начало выполнения скрипта app1.py", file=sys.stderr)
    try:
        main()
    except KeyboardInterrupt:
        print("Программа остановлена пользователем")
    finally:
        if connection:
            connection.close()


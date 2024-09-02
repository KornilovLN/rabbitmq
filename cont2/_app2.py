import pika
import json
import time
import sys

# app2.py

def main():
    print("Скрипт app2.py запущен", file=sys.stderr)
    counter = 0
    print(f"До while", file=sys.stderr)
    while True:
        print(f"cont2 => {counter}", file=sys.stderr)
        sys.stderr.flush()
        time.sleep(4)
        counter += 1

if __name__ == "__main__":
    print("Начало выполнения скрипта", file=sys.stderr)
    main()

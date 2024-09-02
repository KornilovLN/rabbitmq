import pika
import json
import time
import sys

# app1.py

def main():
    print("Скрипт app1py запущен", file=sys.stderr)
    counter = 0
    print(f"До while", file=sys.stderr)
    while True:
        print(f"cont1 => {counter}", file=sys.stderr)
        sys.stderr.flush()
        time.sleep(6)
        counter += 1

if __name__ == "__main__":
    print("Начало выполнения скрипта", file=sys.stderr)
    main()



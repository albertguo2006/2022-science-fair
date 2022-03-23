import secrets
import hashlib
import RPi.GPIO as GPIO
from helper import *

BLANK_INSTRUCTION = "0" * 176
BLANK_SP = "00"
START_SP = "01"
END_SP = "01"
RESENT_SP = "02"

PORT = 25564

KEY = input("Input a key: ")
KEY = hashlib.sha256(KEY.encode("utf-8"))
KEY = KEY.hexdigest()

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(23, GPIO.OUT)
GPIO.setup(4, GPIO.OUT)

while True:
    server = Server(KEY, PORT)

    while True:
        msg = server.receive(BLANK_INSTRUCTION, BLANK_SP)

        if msg == 0:
            GPIO.output(23, GPIO.LOW)
            GPIO.output(4, GPIO.LOW)

            server.close()
            print("Connection termimated by client")

            break

        msg = bytes.fromhex(msg[0:176]).decode('utf-8')

        if msg[0] == 'g':
            GPIO.output(23, GPIO.HIGH)
        else:
            GPIO.output(23, GPIO.LOW)

        if msg[1] == 'r':
            GPIO.output(4, GPIO.HIGH)
        else:
            GPIO.output(4, GPIO.LOW)

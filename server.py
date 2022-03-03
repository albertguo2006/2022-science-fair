import secrets
import hashlib
import RPi.GPIO as GPIO
from helper import *

BLANK_INSTRUCTION = "0" * 48
BLANK_SP = "00"
START_SP = "01"
END_SP = "01"
RESENT_SP = "02"

PORT = 2000

KEY = input("Input a key: ")
KEY = hashlib.sha256(KEY.encode("utf-8"))
KEY = KEY.hexdigest()

server = Server(KEY, PORT)

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(13, GPIO.OUT)
GPIO.setup(21, GPIO.OUT)

while True:
    msg = server.receive(BLANK_INSTRUCTION, BLANK_SP)

    if msg == 0:
        GPIO.output(13, GPIO.LOW)
        GPIO.output(21, GPIO.LOW)

        print("Connection termimated by client")
        break

    msg = bytes.fromhex(msg[64:112]).decode('utf-8')

    if msg[0] == 'g':
        GPIO.output(13, GPIO.HIGH)
    else:
        GPIO.output(13, GPIO.LOW)

    if msg[1] == 'r':
        GPIO.output(21, GPIO.HIGH)
    else:
        GPIO.output(21, GPIO.LOW)

import secrets
import hashlib
from helper import *

BLANK_INSTRUCTION = "0" * 176
BLANK_SP = "00"
START_SP = "01"
END_SP = "01"
RESENT_SP = "02"

PORT = 25564
SERVER_IP = "127.0.0.1"

KEY = input("Input a key: ")
KEY = hashlib.sha256(KEY.encode("utf-8"))
KEY = KEY.hexdigest()

client = Client(KEY, PORT, SERVER_IP)

while True:
    while True:
        msg = input("Input a message: ")

        if len(msg) <= 88:
            break
        else:
            print("Message too long!")

    msg = msg.ljust(88, '\0')
    msg = msg.encode("utf-8").hex()

    msg = client.send(msg, BLANK_SP)

    if msg == 0:
        break

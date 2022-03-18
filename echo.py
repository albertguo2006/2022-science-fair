import secrets
import hashlib
from helper import *

BLANK_INSTRUCTION = "0" * 176
BLANK_SP = "00"
START_SP = "01"
END_SP = "01"
RESENT_SP = "02"

PORT = 2000

KEY = input("Input a key: ")
KEY = hashlib.sha256(KEY.encode("utf-8"))
KEY = KEY.hexdigest()

while True:
    server = Server(KEY, PORT)

    msg = BLANK_INSTRUCTION

    while True:
        msg = server.receive(BLANK_INSTRUCTION, BLANK_SP)

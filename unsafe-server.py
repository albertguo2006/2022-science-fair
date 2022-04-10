import secrets
import hashlib
import socket

from helper import *

BLANK_INSTRUCTION = "0" * 176
BLANK_SP = "00"
START_SP = "01"
END_SP = "01"
RESENT_SP = "02"

PORT = 25564

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.bind(("0.0.0.0", PORT))
s.listen()

conn, addr = s.accept()

while True:
    msg = conn.recv(1024)
    msg = conn.send(msg)

    if msg == 0:
        s.close()
        print("Connection termimated by client")

        break

    print(msg)

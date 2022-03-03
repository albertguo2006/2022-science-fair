import secrets
import hashlib
from helper import *

print("Hi! This program is designed as a interative demo to help you understand the methodology of this project.")
print("Just follow allong with the steps and press enter to continue.")

SEED = input("Input a seed for the encyption keys: ")

# Seed is used to generate two hashes. One is used to seed the encyption and the other is used to salt the rolling hash.
SEED = hashlib.sha256(SEED.encode("utf-8"))
SEED = SEED.hexdigest()

DIGITAL_KEY = hashlib.sha256(bytes.fromhex(SEED))
DIGITAL_KEY = DIGITAL_KEY.hexdigest()

Demo_Romote = Demo_Romote(DIGITAL_KEY, SEED)
Demo_Reciver = Demo_Reciver(DIGITAL_KEY, SEED)

Demo_Romote.attachReciver(Demo_Reciver)
Demo_Reciver.attachRemote(Demo_Romote)

while True:
    msg = input("Input a string to send (24 character limit): ")

    if len(msg) <= 24:
        break

msg = msg.ljust(24, '\0')

Demo_Romote.send(msg.encode("utf-8").hex())

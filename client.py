import secrets
import hashlib
import time
import pygame

from helper import *
from pygame.locals import QUIT

BLANK_INSTRUCTION = "0" * 48
BLANK_SP = "00"
START_SP = "01"
END_SP = "01"
RESENT_SP = "02"

PORT = 2000
SERVER_IP = "192.168.1.66"

GRAY = (128, 128, 128)
BLACK = (0, 0, 0)
SCREEN_SIZE = (600, 600)

KEY = input("Input a key: ")
KEY = hashlib.sha256(KEY.encode("utf-8"))
KEY = KEY.hexdigest()

client = Client(KEY, PORT, SERVER_IP)

pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode(SCREEN_SIZE)
screen.fill(BLACK)

running = True

while running:
    g = "0"
    r = "0"

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

    keys = pygame.key.get_pressed()

    if keys[pygame.K_g]:
        g = "g"

    if keys[pygame.K_r]:
        r = "r"

    msg = g + r

    msg = msg.ljust(24, '\0')
    msg = msg.encode("utf-8").hex()

    print(msg)

    msg = client.send(msg, BLANK_SP)

    if msg == 0:
        print("Connection termimated by server")
        break

    clock.tick(50)

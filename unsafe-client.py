import secrets
import hashlib
import time
import pygame
import socket

from helper import *
from pygame.locals import QUIT

BLANK_INSTRUCTION = "0" * 176
BLANK_SP = "00"
START_SP = "01"
END_SP = "01"
RESENT_SP = "02"

PORT = 25564

SERVER_IP = "127.0.0.1"
# SERVER_IP = "192.168.1.64"

GRAY = (128, 128, 128)
BLACK = (0, 0, 0)
SCREEN_SIZE = (600, 600)

TICK_TIME = 20

pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE)
screen.fill(BLACK)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((SERVER_IP, PORT))

ROLLING_TIMER_LENGTH = 1024
TIMELIST = [0.001] * ROLLING_TIMER_LENGTH

counter = 0
running = True

while running:
    start_time = time.time()

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

    msg += '0' * 126
    msg = msg.encode("utf-8")

    s.send(msg)
    msg = s.recv(1024)

    if msg == 0:
        print("Connection termimated by server")

        s.close()

        break

    run_time = time.time() - start_time
    TIMELIST[counter % ROLLING_TIMER_LENGTH] = run_time
    counter += 1

    print(f"TRANSFER SPEED: {704 * ROLLING_TIMER_LENGTH / sum(TIMELIST)}")

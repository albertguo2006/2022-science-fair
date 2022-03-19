import secrets
import hashlib
import time
import pygame

from helper import *
from pygame.locals import QUIT

BLANK_INSTRUCTION = "0" * 176
BLANK_SP = "00"
START_SP = "01"
END_SP = "01"
RESENT_SP = "02"

PORT = 2000
SERVER_IP = "127.0.0.1"
# SERVER_IP = "192.168.1.64"

GRAY = (128, 128, 128)
BLACK = (0, 0, 0)
SCREEN_SIZE = (600, 600)

TICK_TIME = 0

KEY = input("Input a key: ")
KEY = hashlib.sha256(KEY.encode("utf-8"))
KEY = KEY.hexdigest()

client = Client(KEY, PORT, SERVER_IP)

pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode(SCREEN_SIZE)
screen.fill(BLACK)

ROLLING_TIMER_LENGTH = 256
TIMELIST = [0.01] * ROLLING_TIMER_LENGTH

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

    msg = msg.ljust(88, '\0')
    msg = msg.encode("utf-8").hex()

    msg = client.send(msg, BLANK_SP)

    if msg == 0:
        print("Connection termimated by server")
        break

    if TICK_TIME != 0:
        clock.tick(TICK_TIME)

    run_time = time.time() - start_time
    TIMELIST[counter % ROLLING_TIMER_LENGTH] = run_time
    counter += 1

    print(f"TRANSFER SPEED: {704 * ROLLING_TIMER_LENGTH / sum(TIMELIST)}")

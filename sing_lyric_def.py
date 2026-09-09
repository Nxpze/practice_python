import time
from animate_text import animate_text


def sing_lyric(lyric, delay, speed):
    time.sleep(delay)
    animate_text(lyric, speed)
import time
from threading import Thread, Lock
import sys
from animate_text import animate_text
from sing_lyric_def import sing_lyric


def sing():
    lyrics = [
        ("\n""Beautiful girl",0.09),
        ("Around over the world",0.09),
        ("I coud be chasing, But my time",0.09),
        ("Would be wasted",0.08),
        ("They got nothing on you, baby",0.08),
        ("Nothing on you, baby",0.12),

    ]
    delays = [0.3, 2.8, 5.6, 8.6, 9.8, 14.0]  # Delays for each line in seconds

    threads = []
    for i in range(len(lyrics)):
        lyric, speed = lyrics[i]
        t = Thread(target=sing_lyric, args=(lyric, delays[i], speed))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

if __name__ == "__main__":
    sing()

#end of file


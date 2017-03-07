from pygame import mixer
import time
import os

def main() :
    print(1)
    mixer.init()
    mixer.music.load('/home/codebhendi/Documents/github/pro/alarm/alarm.mp3')
    mixer.music.play()
    time.sleep(10)
    print(2)

if __name__ == "__main__" :
    main()

import STWobject 
from gtts import gTTS
import playsound


class voice(STWobject.stwObject):

    def Init(self):

        super().Init()

    def SayHello(self):

        tts = gTTS('Starte Tracking', lang='de', slow=False)
        with open('hello.mp3', 'wb') as f:
            tts.write_to_fp(f)
        
        playsound.playsound('hello.mp3', True)


import logging

def main():
    print("Class voice")
    print("Runtests ...")
    
    v = voice(logging.getLogger())
    v.Init()
    v.SayHello()

if __name__ == "__main__":
    main()
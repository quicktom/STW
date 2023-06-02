
from gtts import gTTS
import playsound


class voice():

    def Init(self):
        pass

    def SayHello(self):

        tts = gTTS('Referenzpunkt gesetzt', lang='de', slow=False)
        with open('hello.mp3', 'wb') as f:
            tts.write_to_fp(f)
        
        playsound.playsound('hello.mp3', True)



def main():
    print("Class voice")
    print("Runtests ...")
    
    v = voice()
    v.Init()
    v.SayHello()

if __name__ == "__main__":
    main()
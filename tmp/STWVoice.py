
from gtts import gTTS
import playsound


class voice():

    def Init(self):
        pass

    def SayHello(self):

        tts = gTTS('Referenzpunkt gesetzt', lang='de', slow=False)
        with open('referenz.mp3', 'wb') as f:
            tts.write_to_fp(f)

        tts = gTTS('Fahre zum Ziel', lang='de', slow=False)
        with open('Ziel.mp3', 'wb') as f:
            tts.write_to_fp(f)
        
        tts = gTTS('Fehler', lang='de', slow=False)
        with open('Fehler.mp3', 'wb') as f:
            tts.write_to_fp(f)

        tts = gTTS('Koordinate erhalten', lang='de', slow=False)
        with open('Koordinate.mp3', 'wb') as f:
            tts.write_to_fp(f)

        tts = gTTS('Es kann los gehen!', lang='de', slow=False)
        with open('Los.mp3', 'wb') as f:
            tts.write_to_fp(f)

        tts = gTTS('Programm startet', lang='de', slow=False)
        with open('Start.mp3', 'wb') as f:
            tts.write_to_fp(f)


        #playsound.playsound('../hello.mp3', True)



def main():
    print("Class voice")
    print("Runtests ...")
    
    v = voice()
    v.Init()
    v.SayHello()

if __name__ == "__main__":
    main()
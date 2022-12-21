
import STWobject

import logging

import queue

from pynput import keyboard

class STWKeyBoard(STWobject.stwObject):

    def Config(self):
        self.OnPressedQuene = queue.Queue()
        #self.OnReleasedQuene = queue.Queue()

        self.listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=lambda __:0)

        self.listener.start()
        return super().Config()

    def Filter(self, key):
        try:
            if key.char == 'A':
                return True
        except AttributeError:
            pass
        
        return False

    def on_press(self, key):
        if self.Filter(key):
            try:
                with self.OnPressedQuene.mutex: 
                    self.OnPressedQuene.put(key.char,block=False)
            except AttributeError:
                with self.OnPressedQuene.mutex:
                    self.OnPressedQuene.put(key,block=False)

    def listenPressed(self):
        with self.OnPressedQuene.mutex:
            if self.OnPressedQuene.empty():
                return False
            else:
                return self.OnPressedQuene.get(block=False)

    # def listenReleased(self):
    #     if self.OnPressedQuene.empty():
    #         return False
    #     else:
    #         return self.OnReleasedQuene.get(block=False)

    def Shutdown(self):
        self.listener.join()
        with self.OnPressedQuene.mutex:
            self.OnPressedQuene.queue.clear()
            
        return super().Shutdown()
    
def main():
    logger = logging.getLogger(__name__)
    k = STWKeyBoard(logger)
    k.Config()

    while True:
        pressed = k.listenPressed() 
        if pressed:
            print(pressed)



if __name__ == "__main__":      
    main()
 
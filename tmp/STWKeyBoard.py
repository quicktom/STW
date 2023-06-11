
import STWobject
import queue

from pynput import keyboard

class STWKeyBoard(STWobject.stwObject):
    
    # https://learn.microsoft.com/de-de/windows/win32/inputdev/virtual-key-codes?redirectedfrom=MSDN
    # virtual key mapping for numpad on
    # 8 0x68, 2 0x62, 4 0x64, 6 0x66, 5 0x65, 7 0x67, 9 0x69, 1 0x61, 8 0x68 
    keys = [0x68, 0x62, 0x64, 0x66, 0x65, 0x67, 0x69, 0x61, 0x68]

    def Config(self):
        self.OnPressedQuene = queue.Queue()
        self.OnReleasedQuene = queue.Queue()

        self.listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release)
        self.listener.start()
        
        return super().Config()

    def Filter(self, key):
        if hasattr(key, 'vk'):
            if key.vk in self.keys:
                return key
        else:
            return False

    def on_press(self, key):        
        if self.Filter(key):
            self.OnPressedQuene.put(key)

    def on_release(self, key):
        if self.Filter(key):
            self.OnReleasedQuene.put(key)

    def listenPressed(self):
        if self.OnPressedQuene.empty():
            return False
        else:
            return self.OnPressedQuene.get(block=False)

    def listenReleaseded(self):
        if self.OnReleasedQuene.empty():
            return False
        else:
            return self.OnReleasedQuene.get(block=False)

    def Shutdown(self):
        self.listener.stop()
        self.OnPressedQuene.queue.clear()
        self.OnReleasedQuene.queue.clear()
        self.listener.join()

        return super().Shutdown()

import logging

def main():
    logger = logging.getLogger(__name__)
    k = STWKeyBoard(logger)
    k.Config()

    while True:
        pressed = k.listenPressed() 
        if pressed:
            print('pressed')
            print( pressed)

        pressed = k.listenReleaseded()
        if pressed:
            print('released')
            print(pressed)

            if pressed.vk == 104:
                k.Shutdown()
                return

if __name__ == "__main__":      
    main()
 
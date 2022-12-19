# -*- coding: utf-8 -*-
""" STWstellarium module of the observator project.

This module abstracts stellarium functions.

Todo:

__author__ = "Thomas Rinder"
__copyright__ = "Copyright 2023, The observator Group"
__credits__ = ["Thomas Rinder"]
__license__ = "GPL"
__version__ = "0.1.0"
__maintainer__ = "Thomas Rinder"
__email__ = "thomas.rinder@fh-kiel.de"
__status__ = "alpha"

"""

"""

https://free-astro.org/images/b/b7/Stellarium_telescope_protocol.txt

-----------------------
server->client:
MessageCurrentPosition (type = 0):

LENGTH (2 bytes,integer): length of the message
TYPE   (2 bytes,integer): 0
TIME   (8 bytes,integer): current time on the server computer in microseconds
           since 1970.01.01 UT. Currently unused.
RA     (4 bytes,unsigned integer): right ascension of the telescope (J2000)
           a value of 0x100000000 = 0x0 means 24h=0h,
           a value of 0x80000000 means 12h
DEC    (4 bytes,signed integer): declination of the telescope (J2000)
           a value of -0x40000000 means -90degrees,
           a value of 0x0 means 0degrees,
           a value of 0x40000000 means 90degrees
STATUS (4 bytes,signed integer): status of the telescope, currently unused.
           status=0 means ok, status<0 means some error


---------------------

client->server:
MessageGoto (type =0)
LENGTH (2 bytes,integer): length of the message
TYPE   (2 bytes,integer): 0
TIME   (8 bytes,integer): current time on the client computer in microseconds
                  since 1970.01.01 UT. Currently unused.
RA     (4 bytes,unsigned integer): right ascension of the telescope (J2000)
           a value of 0x100000000 = 0x0 means 24h=0h,
           a value of 0x80000000 means 12h
DEC    (4 bytes,signed integer): declination of the telescope (J2000)
           a value of -0x40000000 means -90degrees,
           a value of 0x0 means 0degrees,
           a value of 0x40000000 means 90degrees
"""


import STWobject

import struct, socket, select, threading, logging, queue, datetime, time

class stellarium(STWobject.stwObject):

    def Init(self):
        self.log.info("Initialize Stellarium.")
        return super().Init()

    def Config(self):

        self.open_sockets = []
        self.open_sockets_lock =  threading.Lock()

        self.listening_socket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        self.listening_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listening_socket.setblocking(False)
        self.listening_socket.bind( ("localhost", 10001) )
        self.listening_socket.listen(1)

        self.listenQuene = queue.Queue()
        self.SendQuene = queue.Queue()

        self.listening_thread_event = threading.Event()
        self.listening_thread       = threading.Thread(target=self.listen)
        
        self.send_thread_event      = threading.Event()
        self.send_thread_thread     = threading.Thread(target=self.send)
        
        self.listening_thread.start()
        self.send_thread_thread.start()

        return super().Config()

    def SendToStellarium(self, ra_deg, de_deg):
        self.SendQuene.put([ra_deg, de_deg], block=False)

    def ReceiveFromStellarium(self):
        if not self.listenQuene.empty():
            ret = self.listenQuene.get(block=False)
            return True, ret[0], ret[1]
        else:
            return False, 0, 0  

    def listen(self):
        while not self.listening_thread_event.is_set():
            
            readable, __, __ = select.select([self.listening_socket] + self.open_sockets, [], [], 1)

            if not readable:
                continue

            for i in readable:
                if i is self.listening_socket:
                    # listening_socket accepts incoming connection
                    new_socket, __ = self.listening_socket.accept()
                    # add to list of open connections
                    self.open_sockets.append(new_socket)
                    self.log.info("Connection open to Stellarium")
                else:
                    try:
                        data = i.recv(1024)
                    except:
                        continue

                    if not data:
                        # if no data was returned then close connection
                        with self.open_sockets_lock:
                            self.open_sockets.remove(i)                        
                        i.close()
                        self.log.info("Connection closed to Stellarium")                           
                    else:

                        if len(data) == struct.calcsize("3iIi"): 
                            data = struct.unpack("=hhQIi", data)
                            
                            ra = float(data[3]*(180.0/0x80000000))
                            de = float(data[4]*( 90.0/0x40000000))

                            self.listenQuene.put([ra,de])
                        else:
                            self.log.debug("Stellarium connection wrong data received.")                            

    def send(self):
        while not self.send_thread_event.is_set():

            if not self.SendQuene.empty():
                ret = self.SendQuene.get(block=False)

                if ret:
                    ra = int(ret[0]*(0x80000000/180.0))
                    de = int(ret[1]*(0x40000000/ 90.0))

                    status = struct.pack("=hhQIii", 24, 0, 0, ra, de, 0)

                    # send data to all open connections
                    with self.open_sockets_lock:    
                        for i in self.open_sockets:
                            i.send(status)

    def Shutdown(self):
        self.isConfigured = False
      
        self.listening_thread_event.set()
        self.listening_thread.join()

        self.send_thread_event.set()
        self.send_thread_thread.join()

        for i in self.open_sockets:
            self.open_sockets.remove(i)
            i.close()

        self.listening_socket.close()

        return super().Shutdown()        

import logging

def main():


    g = stellarium(logging.getLogger())

    g.Config()

    ra_a = 0
    de_a = 0

    while True:
        
        ret, ra, de = g.ReceiveFromStellarium()
        if ret:
            ra_a = ra
            de_a = de
            
        time.sleep(0.5)        
        g.SendToStellarium(ra_a, de_a)

    g.Shutdown()
        
if __name__ == "__main__":
    main()



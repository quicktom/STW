#!/usr/bin/python3
import tkinter as tk
import tkinter.ttk as ttk

import json

class StickyApp:
    def __init__(self, master=None):

        # build ui
        astrostyle = ttk.Style(master)
        astrostyle.configure("TButton", foreground="red", background="black")
        astrostyle.configure("TLabel", foreground="green", background="black")
        astrostyle.configure('TFrame', background='black')

        frame = ttk.Frame(master)

        self.exit = ttk.Button(frame)
        self.exit.configure(text='Exit')
        self.exit.grid(column=1, row=0)
        self.exit.bind('<ButtonPress>', self.quit)
    
        self.banner = ttk.Label(frame)  
        
        self.banner.configure(
            text='STW state monitor',
            width=45,
            font=("Arial", 12))
        self.banner.grid(column=0, row = 0, padx=10)

        self.status = ttk.Label(frame)  

        self.status.configure(
            text='status',
            width=45,
            font=("Arial", 12))
        self.status.grid(column=0, row = 1, padx=10)

        self.data = ttk.Label(frame)  

        self.data.configure(
            text='data',
            width=45,
            font=("Arial", 12))
        self.data.grid(column=0, row = 2, padx=10)

        self.action = ttk.Label(frame)  

        self.action.configure(
            text='action',
            width=45,
            font=("Arial", 12))
        self.action.grid(column=0, row = 3, padx=10)

        self.vsep = ttk.Label(frame)  

        self.vsep.configure(
            text='vsep',
            width=45,
            font=("Arial", 12))
        self.vsep.grid(column=0, row = 4, padx=10)

        frame.grid(column=2, row=4)

        # Main widget
        self.mainwindow = frame

    def update_clock(self):
        # get current time as text
        try:
            f = open('actual.json', 'r')
            file_data = json.load(f)
            f.close()
            self.status["text"] =  "J2000 Telescope " + file_data["state"][0]["telescopeJ2000Str"]
            self.data  ["text"] =  "J2000 Target    " + file_data["state"][0]["targetJ2000Str"]
            self.banner["text"] =  file_data["state"][0]["UTC"] 
            self.action["text"] =  file_data["state"][0]["ActionStr"]
            self.vsep  ["text"] =  "Telescope to target separation " +  file_data["state"][0]["AngularSeparation"]

            root.after(1000, app.update_clock)
        except:  
            root.after(250, app.update_clock)
            
    def run(self):
        self.mainwindow.mainloop()

    def quit(self):
        pass

if __name__ == "__main__":
    root = tk.Tk()

    app = StickyApp(root)

    # make window overlay
    root.overrideredirect(True)
    root.wm_attributes("-topmost", True)
 
    # put window left top aligned
    root.update()
    screen_width = root.winfo_screenwidth()
    window_width = root.winfo_width()
    window_height = root.winfo_height()

    root.geometry('%dx%d+%d+%d' % (window_width, window_height, (screen_width - window_width)/2, 0))

    # setup periodic task
    app.update_clock()

    # run
    app.run()

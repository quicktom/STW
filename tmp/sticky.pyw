#!/usr/bin/python3
import tkinter as tk
import tkinter.ttk as ttk

import datetime, json

class StickyApp:
    def __init__(self, master=None):
        # build ui
        astrostyle = ttk.Style(master)
        astrostyle.configure("TButton", foreground="red", background="black")
        astrostyle.configure("TLabel", foreground="red", background="black")
        astrostyle.configure('TFrame', background='black')

        frame = ttk.Frame(master)

        frame.configure(height=80, width=1180)

        self.exit = ttk.Button(frame)
        self.exit.configure(text='Exit')
        self.exit.grid(column=1, row=0)
        self.exit.bind("<ButtonPress>", self.callbackExit, add="")
        
        self.status = ttk.Label(frame)  
        
        self.status.configure(
            text='status',
            width=90,
            font=("Arial", 16))
        self.status.grid(column=0, row = 0, padx=10)

        self.data = ttk.Label(frame)  

        self.data.configure(
            text='data',
            width=90,
            font=("Arial", 16))
        self.data.grid(column=0, row = 1, padx=10)

        self.action = ttk.Label(frame)  

        self.action.configure(
            text='action',
            width=90,
            font=("Arial", 16))
        self.action.grid(column=0, row = 2, padx=10)

        frame.grid(column=2, row=3)

        # Main widget
        self.mainwindow = frame

        try:
            self.f = open('actual.json', 'r')
        except: 
            self.f = False

    def update_clock(self):
        # get current time as text
        try:
            self.f.seek(0)
            file_data = json.load(self.f)
            self.status['text'] =   file_data["state"]["UTC"] + " " + \
                                    "J2000 Target " +        file_data["state"]["targetJ2000Str"]                
            self.data['text']   =   "Telescope " +          file_data["state"]["telescopeActualStr"] + " " + \
                                    "Telescope target " +   file_data["state"]["targetActualStr"]
            self.action['text'] =   file_data["state"]["ActualActionStr"]
            root.after(250, app.update_clock)
        except:  
            root.after(25, app.update_clock)

    def run(self):
        self.mainwindow.mainloop()

    def callbackExit(self, event=None):

        self.mainwindow.quit()


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

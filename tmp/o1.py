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

        frame = ttk.Frame(master)

        frame.configure(height=25, width=1180)


        
        self.exit = ttk.Button(frame)
        self.exit.configure(text='Exit')
        self.exit.grid(column=1, row=0)
        self.exit.bind("<ButtonPress>", self.callbackExit, add="")
        
        self.status = ttk.Label(frame)  
        self.Status = tk.StringVar(value='status')
        self.status.configure(
            text='status',
            width=180)
        self.status.grid(column=0, padx=10, row=0)
        frame.grid(column=1, row=1)

        # Main widget
        self.mainwindow = frame
        
    def update_clock(self):
        # get current time as text

        try:
            with open('../actual.json', 'r') as f:
                file_data = json.load(f)
                self.status['text'] =   file_data["state"]["UTC"] + " " + \
                                        "J2000 " + file_data["state"]["targetJ2000Str"] + " " + \
                                        "Telescope " + file_data["state"]["telescopeActualStr"] + " " + \
                                        "Telescope target " + file_data["state"]["targetActualStr"] 
                f.close()
        except: # may master locks, so try again later 
            pass

        # run itself again after 1000 ms
        root.after(1000, self.update_clock) 

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

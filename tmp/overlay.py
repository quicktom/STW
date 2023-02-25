import tkinter as tk



class Overlay:
    """
    Creates an overlay window using tkinter
    Uses the "-topmost" property to always stay on top of other Windows
    """
    def __init__(self):
        self.initial_text = "initial_text TOLL WAhnsinn"
        self.root = tk.Tk()



        # Set up Ping Label
        self.ping_text = tk.StringVar()
        self.ping_label = tk.Label(
            self.root,
            textvariable=self.ping_text,
            font=('Consolas', '14'),
            fg='green3',
            bg='grey19'
        )
        self.ping_label.grid(row=0, column=1)


        # Define Window Geometry
        self.root.overrideredirect(True)
        self.root.geometry("+5+5")
        self.root.lift()
        self.root.wm_attributes("-topmost", True)

        self.root.geometry('100x100+1200+100')

    def run(self) -> None:
        self.ping_text.set(self.initial_text)
        
        self.root.mainloop()


def main():
    o = Overlay()

    o.run()
    

if __name__ == "__main__":
    main()
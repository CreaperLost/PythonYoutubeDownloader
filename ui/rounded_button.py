import tkinter as tk


class RoundedButton(tk.Canvas):
    def __init__(self, parent, width, height, cornerradius, padding, color, text='', command=None):
        tk.Canvas.__init__(self, parent, borderwidth=0,
                           relief="flat", highlightthickness=0, bg=parent["bg"])
        self.command = command

        if cornerradius > 0.5 * width:
            cornerradius = 0.5 * width
        if cornerradius > 0.5 * height:
            cornerradius = 0.5 * height

        self.shapes = []
        self.shapes.append(self.create_polygon((padding, height - cornerradius - padding, padding,
                                                cornerradius + padding, padding + cornerradius, padding,
                                                width - padding - cornerradius, padding, width - padding,
                                                cornerradius + padding, width - padding,
                                                height - cornerradius - padding, width - padding - cornerradius,
                                                height - padding, padding + cornerradius, height - padding), fill=color,
                                               outline=color))

        self.configure(width=width, height=height)
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)

        self.textid = self.create_text(width / 2, height / 2, text=text, fill='white', font=("Helvetica", 10))

    def _on_press(self, event):
        self.configure(relief="sunken")

    def _on_release(self, event):
        self.configure(relief="raised")
        if self.command is not None:
            self.command()

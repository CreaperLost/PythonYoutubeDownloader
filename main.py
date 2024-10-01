import tkinter as tk

from download_youtube import VideoDownloader

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoDownloader(root)
    root.mainloop()

import os
import conf
from pytube import YouTube as pytubeYT, cipher
from moviepy.editor import VideoFileClip, AudioFileClip
import tkinter as tk
from PIL import Image, ImageTk
import requests
from io import BytesIO
from tkinter import filedialog, messagebox, ttk
from ui.rounded_button import RoundedButton
from utils.youtube_utils import is_valid_youtube_url, get_throttling_function_name, sanitize_filename

cipher.get_throttling_function_name = get_throttling_function_name


class VideoDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("Aero YouTube Downloader")
        self.root.geometry("400x400")
        self.root.configure(bg="#1e1e1e")
        self.output_dir = None
        self.style = ttk.Style()
        self.setup_styles()
        self.create_main_menu()

    def setup_styles(self):
        self.style.theme_use("clam")
        self.style.configure("TFrame", background="#1e1e1e")
        self.style.configure("TLabel", foreground="white", background="#1e1e1e", font=("Helvetica", 10))
        self.style.configure("TEntry", fieldbackground="#2e2e2e", foreground="white", insertcolor="white",
                             font=("Helvetica", 10))
        self.style.configure("Rounded.TEntry", borderwidth=0, relief="flat")
        self.style.layout("Rounded.TEntry",
                          [('Entry.plain.field', {'children': [(
                              'Entry.background', {'children': [(
                                  'Entry.padding', {'children': [(
                                      'Entry.textarea', {'sticky': 'nswe'})],
                                      'sticky': 'nswe'})], 'sticky': 'nswe'})],
                              'border': '2', 'sticky': 'nswe'})])

    def create_rounded_frame(self, parent, color):
        frame = tk.Frame(parent, bg=color, bd=0, highlightthickness=0)
        frame.grid_propagate(False)
        return frame

    def create_main_menu(self):
        self.clean_up()

        main_frame = self.create_rounded_frame(self.root, "#1e1e1e")
        main_frame.pack(padx=20, pady=20)

        ttk.Label(main_frame, text="YouTube Video Downloader", font=("Helvetica", 16, "bold")).pack(padx=20,
                                                                                                    pady=(0, 10))

        # YouTube URL input
        ttk.Label(main_frame, text="Enter YouTube URL:").pack(padx=20, pady=(10, 5))
        self.url_entry = ttk.Entry(main_frame, width=50, style="Rounded.TEntry")
        self.url_entry.pack(padx=20, pady=(0, 10), ipady=5)
        RoundedButton(main_frame, 120, 30, 15, 2, "#3e3e3e", text="Check URL", command=self.check_url).pack(
            pady=(0, 10))

        # Video preview
        self.preview_frame = self.create_rounded_frame(main_frame, "#2e2e2e")
        self.preview_frame.pack(padx=20, pady=10)

        # Output directory selection
        ttk.Label(main_frame, text="Output Directory:").pack(pady=(20, 5))
        self.output_dir_var = tk.StringVar(self.root)
        ttk.Entry(main_frame, textvariable=self.output_dir_var, width=50, state='readonly',
                  style="Rounded.TEntry").pack(pady=(0, 10), ipady=5)
        RoundedButton(main_frame, 180, 30, 15, 2, "#3e3e3e", text="Select Output Directory",
                      command=self.select_output_directory).pack(pady=(0, 10))

        # Download button
        self.download_button = RoundedButton(main_frame, 150, 40, 20, 2, "#3e3e3e", text="Download Video",
                                             command=self.download_video)
        self.download_button.pack(pady=(0, 20))
        self.download_button.configure(state='disabled')

    def clean_up(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def check_url(self):
        url = self.url_entry.get()
        if is_valid_youtube_url(url):
            self.show_video_preview(url)
            self.root.geometry("400x600")
        else:
            messagebox.showerror("Invalid URL", "Please enter a valid YouTube URL.")

    def show_video_preview(self, url):
        try:
            yt = pytubeYT(url)
            # Fetch thumbnail
            response = requests.get(yt.thumbnail_url)
            img = Image.open(BytesIO(response.content))
            img.thumbnail((200, 200))  # Resize thumbnail
            photo = ImageTk.PhotoImage(img)

            # Clear previous preview
            for widget in self.preview_frame.winfo_children():
                widget.destroy()

            # Display thumbnail
            tk.Label(self.preview_frame, image=photo).pack()
            self.preview_frame.image = photo  # Keep a reference

            # Display title
            tk.Label(self.preview_frame, text=yt.title, wraplength=300).pack()

            # Enable download button
            self.download_button.config(state=tk.NORMAL)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch video info: {str(e)}")

    def select_output_directory(self):
        self.output_dir = filedialog.askdirectory()
        self.output_dir_var.set(self.output_dir)

    def download_video(self):
        if not self.output_dir:
            messagebox.showerror("Error", "Please select an output directory.")
            return

        url = self.url_entry.get()
        try:
            yt = pytubeYT(url)

            base_filename = sanitize_filename(yt.title)

            video = yt.streams.filter(adaptive=True, file_extension='mp4').first()
            audio = yt.streams.filter(only_audio=True).first()

            if video is None:
                print("Something went wrong")
                return

            print(f"Downloading: {yt.title}")
            video.download(self.output_dir, filename=f"{base_filename}.mp4")
            print("Downloading Audio")
            audio.download(self.output_dir, filename=f"{base_filename}.mp3")

            video = VideoFileClip(os.path.join(self.output_dir, f"{base_filename}.mp4"))
            audio = AudioFileClip(os.path.join(self.output_dir, f"{base_filename}.mp3"))
            final_clip = video.set_audio(audio)
            output_file = os.path.join(self.output_dir, f"{yt.title}_final.mp4")
            print(f"Download completed: {yt.title}")
            final_clip.write_videofile(output_file, audio=True, preset='veryslow', threads=None)

            # Close the clips
            video.close()
            audio.close()
            final_clip.close()

            # Remove temporary files
            os.remove(os.path.join(self.output_dir, f"{base_filename}.mp4"))
            os.remove(os.path.join(self.output_dir, f"{base_filename}.mp3"))
            print(f"Compression completed: {output_file}")
            messagebox.showinfo("Success", f"Video downloaded successfully to {self.output_dir}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to download video: {str(e)}")

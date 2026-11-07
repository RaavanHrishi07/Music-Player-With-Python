
import os
import tkinter as tk
from tkinter import filedialog, messagebox
import pygame


class MusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("My Music Player")
        self.root.geometry("550x500")
        self.root.minsize(450, 400)
        self.root.configure(bg="#1E1E2E")

        pygame.init()
        pygame.mixer.init()

        self.music_directory = ""
        self.current_song = None
        self.supported_formats = (".mp3", ".wav", ".ogg")

        self.setup_ui()

    def setup_ui(self):
        title = tk.Label(
            self.root,
            text="♫ MY MUSIC PLAYER",
            font=("Segoe UI", 22, "bold"),
            bg="#1E1E2E",
            fg="#CBA6F7"
        )
        title.pack(pady=20)

        self.song_title = tk.Label(
            self.root,
            text="No song selected",
            font=("Segoe UI", 11),
            bg="#1E1E2E",
            fg="#CDD6F4",
            wraplength=450
        )
        self.song_title.pack(pady=10)

        self.play_list = tk.Listbox(
            self.root,
            font=("Segoe UI", 11),
            bg="#313244",
            fg="#CDD6F4",
            selectbackground="#CBA6F7",
            selectforeground="#1E1E2E",
            relief="flat",
            height=12
        )
        self.play_list.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=10
        )

        self.play_list.bind(
            "<Double-Button-1>",
            lambda event: self.play()
        )

        tk.Button(
            self.root,
            text="📁  Choose Music Folder",
            command=self.choose_folder,
            font=("Segoe UI", 10, "bold"),
            bg="#45475A",
            fg="white",
            relief="flat",
            cursor="hand2",
            pady=9
        ).pack(fill="x", padx=25, pady=5)

        controls = tk.Frame(self.root, bg="#1E1E2E")
        controls.pack(pady=15)

        buttons = [
            ("▶ PLAY", self.play, "#A6E3A1"),
            ("⏸ PAUSE", self.pause, "#F9E2AF"),
            ("▶ RESUME", self.resume, "#89B4FA"),
            ("⏹ STOP", self.stop, "#F38BA8")
        ]

        for text, command, color in buttons:
            tk.Button(
                controls,
                text=text,
                command=command,
                font=("Segoe UI", 9, "bold"),
                bg=color,
                fg="#1E1E2E",
                relief="flat",
                cursor="hand2",
                padx=10,
                pady=10
            ).pack(side="left", padx=4)

        self.status_label = tk.Label(
            self.root,
            text="Select a music folder to get started",
            font=("Segoe UI", 9),
            bg="#1E1E2E",
            fg="#A6ADC8"
        )
        self.status_label.pack(pady=(0, 12))

    def choose_folder(self):
        directory = filedialog.askdirectory(
            title="Select Music Folder"
        )

        if not directory:
            return

        self.music_directory = directory

        songs = [
            file for file in os.listdir(directory)
            if file.lower().endswith(self.supported_formats)
            and os.path.isfile(os.path.join(directory, file))
        ]

        songs.sort(key=str.lower)

        self.play_list.delete(0, tk.END)

        for song in songs:
            self.play_list.insert(tk.END, song)

        if not songs:
            self.song_title.config(text="No supported audio files found")
            self.status_label.config(
                text="Choose a folder containing MP3, WAV or OGG files"
            )
            return

        self.status_label.config(
            text=f"{len(songs)} audio file(s) loaded"
        )
        self.song_title.config(text="Select a song to play")

    def play(self):
        selection = self.play_list.curselection()

        if not selection:
            messagebox.showwarning(
                "No Song Selected",
                "Please select a song from the playlist."
            )
            return

        if not self.music_directory:
            return

        song = self.play_list.get(selection[0])
        song_path = os.path.join(self.music_directory, song)

        try:
            pygame.mixer.music.load(song_path)
            pygame.mixer.music.play()

            self.current_song = song
            self.song_title.config(text=f"♫ Now Playing: {song}")
            self.status_label.config(text="Music is playing")

        except (pygame.error, OSError) as error:
            messagebox.showerror(
                "Playback Error",
                f"Unable to play this audio file.\n\n{error}"
            )

    def pause(self):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            self.status_label.config(text="Music paused")
        else:
            messagebox.showinfo(
                "Playback",
                "No music is currently playing."
            )

    def resume(self):
        if self.current_song:
            pygame.mixer.music.unpause()
            self.status_label.config(text="Music resumed")
        else:
            messagebox.showinfo(
                "Playback",
                "Please play a song first."
            )

    def stop(self):
        pygame.mixer.music.stop()
        self.status_label.config(text="Music stopped")

    def close(self):
        pygame.mixer.music.stop()
        pygame.mixer.quit()
        pygame.quit()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = MusicPlayer(root)
    root.protocol("WM_DELETE_WINDOW", app.close)
    root.mainloop()

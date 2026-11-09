
import os
import tkinter as tk
from tkinter import filedialog, messagebox
import pygame


class MusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("My Music Player")
        self.root.geometry("600x650")
        self.root.minsize(500, 550)
        self.root.configure(bg="#1E1E2E")

        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.set_volume(0.7)

        self.music_directory = ""
        self.current_song = None
        self.current_index = -1
        self.supported_formats = (".mp3", ".wav", ".ogg")

        self.song_duration = 0
        self.is_seeking = False
        self.was_playing_before_seek = False
        self.seek_offset = 0
        self.progress_job = None

        self.setup_ui()
        self.update_progress()

    def setup_ui(self):
        tk.Label(
            self.root,
            text="♫ MY MUSIC PLAYER",
            font=("Segoe UI", 22, "bold"),
            bg="#1E1E2E",
            fg="#CBA6F7"
        ).pack(pady=15)

        self.song_title = tk.Label(
            self.root,
            text="No song selected",
            font=("Segoe UI", 11),
            bg="#1E1E2E",
            fg="#CDD6F4",
            wraplength=480
        )
        self.song_title.pack(pady=8)

        self.play_list = tk.Listbox(
            self.root,
            font=("Segoe UI", 11),
            bg="#313244",
            fg="#CDD6F4",
            selectbackground="#CBA6F7",
            selectforeground="#1E1E2E",
            relief="flat",
            height=10
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

        # Volume control
        volume_frame = tk.Frame(self.root, bg="#1E1E2E")
        volume_frame.pack(fill="x", padx=25, pady=10)

        tk.Label(
            volume_frame,
            text="🔊 Volume",
            font=("Segoe UI", 10, "bold"),
            bg="#1E1E2E",
            fg="#CDD6F4"
        ).pack(side="left")

        self.volume_value = tk.Label(
            volume_frame,
            text="70%",
            font=("Segoe UI", 10, "bold"),
            bg="#1E1E2E",
            fg="#CBA6F7"
        )
        self.volume_value.pack(side="right")

        self.volume_slider = tk.Scale(
            volume_frame,
            from_=0,
            to=100,
            orient="horizontal",
            command=self.change_volume,
            bg="#1E1E2E",
            fg="#CDD6F4",
            troughcolor="#45475A",
            activebackground="#CBA6F7",
            highlightthickness=0,
            relief="flat",
            showvalue=False
        )
        self.volume_slider.set(70)
        self.volume_slider.pack(
            side="left",
            fill="x",
            expand=True,
            padx=15
        )

        # Playback progress
        progress_frame = tk.Frame(self.root, bg="#1E1E2E")
        progress_frame.pack(fill="x", padx=25, pady=8)

        time_frame = tk.Frame(progress_frame, bg="#1E1E2E")
        time_frame.pack(fill="x")

        self.current_time_label = tk.Label(
            time_frame,
            text="00:00",
            font=("Segoe UI", 9),
            bg="#1E1E2E",
            fg="#CDD6F4"
        )
        self.current_time_label.pack(side="left")

        self.total_time_label = tk.Label(
            time_frame,
            text="00:00",
            font=("Segoe UI", 9),
            bg="#1E1E2E",
            fg="#CDD6F4"
        )
        self.total_time_label.pack(side="right")

        self.progress_slider = tk.Scale(
            progress_frame,
            from_=0,
            to=100,
            orient="horizontal",
            showvalue=False,
            command=self.seek_song,
            bg="#1E1E2E",
            fg="#CDD6F4",
            troughcolor="#45475A",
            activebackground="#CBA6F7",
            highlightthickness=0,
            relief="flat",
            state="disabled"
        )
        self.progress_slider.pack(fill="x")

        self.progress_slider.bind(
            "<ButtonPress-1>",
            self.start_seeking
        )
        self.progress_slider.bind(
            "<ButtonRelease-1>",
            self.finish_seeking
        )

        # Playback controls
        controls = tk.Frame(self.root, bg="#1E1E2E")
        controls.pack(pady=12)

        buttons = [
            ("⏮ PREV", self.previous_song, "#89B4FA"),
            ("▶ PLAY", self.play, "#A6E3A1"),
            ("⏭ NEXT", self.next_song, "#89B4FA"),
            ("⏸ PAUSE", self.pause, "#F9E2AF"),
            ("▶ RESUME", self.resume, "#CBA6F7"),
            ("⏹ STOP", self.stop, "#F38BA8")
        ]

        for text, command, color in buttons:
            tk.Button(
                controls,
                text=text,
                command=command,
                font=("Segoe UI", 8, "bold"),
                bg=color,
                fg="#1E1E2E",
                relief="flat",
                cursor="hand2",
                padx=7,
                pady=10
            ).pack(side="left", padx=2)

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

        pygame.mixer.music.stop()

        self.music_directory = directory
        self.current_song = None
        self.current_index = -1
        self.song_duration = 0
        self.seek_offset = 0

        self.reset_progress()

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

    def change_volume(self, value):
        volume = float(value) / 100
        pygame.mixer.music.set_volume(volume)
        self.volume_value.config(text=f"{int(float(value))}%")

    def format_time(self, seconds):
        seconds = max(0, int(seconds))
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{minutes:02d}:{remaining_seconds:02d}"

    def get_duration(self, song_path):
        try:
            sound = pygame.mixer.Sound(song_path)
            return sound.get_length()
        except (pygame.error, OSError):
            return 0

    def reset_progress(self):
        self.progress_slider.configure(
            state="disabled",
            to=100
        )
        self.progress_slider.set(0)
        self.current_time_label.config(text="00:00")
        self.total_time_label.config(text="00:00")

    def play_song(self, index):
        total_songs = self.play_list.size()

        if total_songs == 0:
            messagebox.showwarning(
                "Empty Playlist",
                "Please select a folder containing music files."
            )
            return

        index = index % total_songs
        song = self.play_list.get(index)
        song_path = os.path.join(self.music_directory, song)

        try:
            pygame.mixer.music.load(song_path)

            self.song_duration = self.get_duration(song_path)
            pygame.mixer.music.play()

            self.current_index = index
            self.current_song = song
            self.seek_offset = 0
            self.is_seeking = False

            self.play_list.selection_clear(0, tk.END)
            self.play_list.selection_set(index)
            self.play_list.activate(index)
            self.play_list.see(index)

            self.progress_slider.configure(
                state="normal",
                to=max(1, self.song_duration)
            )
            self.progress_slider.set(0)

            self.current_time_label.config(text="00:00")
            self.total_time_label.config(
                text=self.format_time(self.song_duration)
            )

            self.song_title.config(text=f"♫ Now Playing: {song}")
            self.status_label.config(text="Music is playing")

        except (pygame.error, OSError) as error:
            messagebox.showerror(
                "Playback Error",
                f"Unable to play this audio file.\n\n{error}"
            )

    def play(self):
        selection = self.play_list.curselection()

        if selection:
            index = selection[0]
        elif self.current_index >= 0:
            index = self.current_index
        else:
            messagebox.showwarning(
                "No Song Selected",
                "Please select a song from the playlist."
            )
            return

        self.play_song(index)

    def next_song(self):
        total_songs = self.play_list.size()

        if total_songs == 0:
            messagebox.showwarning(
                "Empty Playlist",
                "Please load a music folder first."
            )
            return

        if self.current_index == -1:
            self.play_song(0)
        else:
            self.play_song(
                (self.current_index + 1) % total_songs
            )

    def previous_song(self):
        total_songs = self.play_list.size()

        if total_songs == 0:
            messagebox.showwarning(
                "Empty Playlist",
                "Please load a music folder first."
            )
            return

        if self.current_index == -1:
            self.play_song(total_songs - 1)
        else:
            self.play_song(
                (self.current_index - 1) % total_songs
            )

    def start_seeking(self, event):
        if not self.current_song or self.song_duration <= 0:
            return

        self.is_seeking = True
        self.was_playing_before_seek = pygame.mixer.music.get_busy()

    def seek_song(self, value):
        if self.is_seeking:
            position = float(value)
            self.current_time_label.config(
                text=self.format_time(position)
            )

    def finish_seeking(self, event):
        if not self.current_song or self.song_duration <= 0:
            self.is_seeking = False
            return

        position = self.progress_slider.get()

        try:
            pygame.mixer.music.play(start=position)
            self.seek_offset = position

            if not self.was_playing_before_seek:
                pygame.mixer.music.pause()
                self.status_label.config(text="Music paused")
            else:
                self.status_label.config(text="Music is playing")

        except pygame.error as error:
            messagebox.showerror(
                "Seek Error",
                f"Unable to seek to this position.\n\n{error}"
            )

        self.is_seeking = False

    def update_progress(self):
        if self.current_song and self.song_duration > 0:
            if not self.is_seeking:
                elapsed = pygame.mixer.music.get_pos() / 1000

                if elapsed >= 0:
                    current_position = min(
                        self.seek_offset + elapsed,
                        self.song_duration
                    )

                    self.progress_slider.set(current_position)
                    self.current_time_label.config(
                        text=self.format_time(current_position)
                    )

        self.progress_job = self.root.after(
            500,
            self.update_progress
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
        self.seek_offset = 0
        self.reset_progress()
        self.status_label.config(text="Music stopped")

    def close(self):
        if self.progress_job is not None:
            self.root.after_cancel(self.progress_job)

        pygame.mixer.music.stop()
        pygame.mixer.quit()
        pygame.quit()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = MusicPlayer(root)
    root.protocol("WM_DELETE_WINDOW", app.close)
    root.mainloop()

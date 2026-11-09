
import os
import json
import random
import tkinter as tk
from tkinter import filedialog, messagebox

import pygame
from PIL import Image, ImageTk, ImageDraw


class MusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Melody - Python Music Player")
        self.root.geometry("850x780")
        self.root.minsize(750, 700)
        self.root.configure(bg="#101014")

        pygame.mixer.init()

        self.songs = []
        self.current_index = -1
        self.filtered_indices = []

        self.favourites = set()
        self.favourites_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "favourites.json"
        )

        self.load_favourites()

        self.song_duration = 0
        self.seek_offset = 0
        self.is_seeking = False
        self.is_paused = False
        self.is_stopped = True
        self.song_finished_handled = True
        self.progress_job = None

        self.shuffle_enabled = False
        self.repeat_mode = "OFF"
        self.show_favourites = False

        self.volume = tk.DoubleVar(value=70)
        self.progress_value = tk.DoubleVar(value=0)
        self.search_text = tk.StringVar()

        self.album_image = None

        self.create_ui()
        self.set_volume()
        self.refresh_playlist()
        self.update_progress()

        self.root.protocol("WM_DELETE_WINDOW", self.close_player)

    # ---------------- UI ----------------

    def create_ui(self):
        header = tk.Frame(self.root, bg="#101014")
        header.pack(fill="x", padx=25, pady=(18, 8))

        tk.Label(
            header,
            text="MELODY",
            font=("Arial", 25, "bold"),
            bg="#101014",
            fg="#1DB954"
        ).pack(side="left")

        tk.Label(
            header,
            text="YOUR PERSONAL MUSIC PLAYER",
            font=("Arial", 9, "bold"),
            bg="#101014",
            fg="#888888"
        ).pack(side="right", pady=10)

        # Album artwork section
        artwork_section = tk.Frame(
            self.root,
            bg="#18181F",
            padx=20,
            pady=15
        )
        artwork_section.pack(fill="x", padx=25, pady=10)

        self.artwork_canvas = tk.Canvas(
            artwork_section,
            width=190,
            height=190,
            bg="#252530",
            highlightthickness=0
        )
        self.artwork_canvas.pack(side="left", padx=(10, 25))

        self.show_default_artwork()

        song_info = tk.Frame(
            artwork_section,
            bg="#18181F"
        )
        song_info.pack(side="left", fill="both", expand=True)

        tk.Label(
            song_info,
            text="NOW PLAYING",
            font=("Arial", 9, "bold"),
            bg="#18181F",
            fg="#1DB954"
        ).pack(anchor="w", pady=(20, 8))

        self.now_playing = tk.Label(
            song_info,
            text="No song selected",
            font=("Arial", 17, "bold"),
            bg="#18181F",
            fg="white",
            wraplength=450,
            justify="left"
        )
        self.now_playing.pack(anchor="w", pady=5)

        self.song_subtitle = tk.Label(
            song_info,
            text="Choose a music folder to begin",
            font=("Arial", 10),
            bg="#18181F",
            fg="#999999"
        )
        self.song_subtitle.pack(anchor="w", pady=5)

        self.status_label = tk.Label(
            song_info,
            text="READY TO PLAY",
            font=("Arial", 9, "bold"),
            bg="#18181F",
            fg="#1DB954"
        )
        self.status_label.pack(anchor="w", pady=15)

        # Search section
        search_frame = tk.Frame(self.root, bg="#101014")
        search_frame.pack(fill="x", padx=25, pady=10)

        tk.Label(
            search_frame,
            text="YOUR LIBRARY",
            font=("Arial", 12, "bold"),
            bg="#101014",
            fg="white"
        ).pack(anchor="w", pady=(0, 8))

        search_row = tk.Frame(search_frame, bg="#101014")
        search_row.pack(fill="x")

        self.search_entry = tk.Entry(
            search_row,
            textvariable=self.search_text,
            bg="#22222B",
            fg="white",
            insertbackground="white",
            relief="flat",
            font=("Arial", 11)
        )
        self.search_entry.pack(
            side="left",
            fill="x",
            expand=True,
            ipady=9,
            padx=(0, 8)
        )

        tk.Button(
            search_row,
            text="CLEAR",
            command=lambda: self.search_text.set(""),
            bg="#30303A",
            fg="white",
            relief="flat",
            padx=12,
            pady=7
        ).pack(side="left")

        self.search_text.trace_add(
            "write",
            lambda *args: self.refresh_playlist()
        )

        # Playlist filters
        filter_frame = tk.Frame(self.root, bg="#101014")
        filter_frame.pack(fill="x", padx=25, pady=5)

        self.all_button = tk.Button(
            filter_frame,
            text="ALL SONGS",
            command=self.show_all_songs,
            bg="#1DB954",
            fg="black",
            relief="flat",
            padx=14,
            pady=7
        )
        self.all_button.pack(side="left", padx=(0, 8))

        self.favourites_button = tk.Button(
            filter_frame,
            text="★ FAVOURITES",
            command=self.show_favourite_songs,
            bg="#30303A",
            fg="white",
            relief="flat",
            padx=14,
            pady=7
        )
        self.favourites_button.pack(side="left")

        self.song_count_label = tk.Label(
            filter_frame,
            text="0 SONGS",
            bg="#101014",
            fg="#999999",
            font=("Arial", 9, "bold")
        )
        self.song_count_label.pack(side="right")

        # Playlist
        playlist_frame = tk.Frame(self.root, bg="#101014")
        playlist_frame.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=8
        )

        scrollbar = tk.Scrollbar(playlist_frame)
        scrollbar.pack(side="right", fill="y")

        self.playlist = tk.Listbox(
            playlist_frame,
            bg="#1B1B23",
            fg="#EEEEEE",
            selectbackground="#1DB954",
            selectforeground="black",
            font=("Arial", 11),
            bd=0,
            highlightthickness=0,
            activestyle="none",
            yscrollcommand=scrollbar.set
        )
        self.playlist.pack(fill="both", expand=True)

        scrollbar.config(command=self.playlist.yview)

        self.playlist.bind(
            "<Double-Button-1>",
            self.play_selected
        )

        # Playlist actions
        action_frame = tk.Frame(self.root, bg="#101014")
        action_frame.pack(fill="x", padx=25, pady=5)

        tk.Button(
            action_frame,
            text="★ TOGGLE FAVOURITE",
            command=self.toggle_favourite,
            bg="#30303A",
            fg="#FFD700",
            relief="flat",
            padx=12,
            pady=8
        ).pack(side="left")

        tk.Button(
            action_frame,
            text="+ OPEN MUSIC FOLDER",
            command=self.load_folder,
            bg="#1DB954",
            fg="black",
            font=("Arial", 9, "bold"),
            relief="flat",
            padx=12,
            pady=8
        ).pack(side="right")

        # Progress section
        progress_frame = tk.Frame(self.root, bg="#101014")
        progress_frame.pack(fill="x", padx=30, pady=8)

        self.current_time_label = tk.Label(
            progress_frame,
            text="00:00",
            bg="#101014",
            fg="#AAAAAA"
        )
        self.current_time_label.pack(side="left")

        self.progress_slider = tk.Scale(
            progress_frame,
            from_=0,
            to=100,
            orient="horizontal",
            variable=self.progress_value,
            command=self.seek_song,
            showvalue=False,
            bg="#101014",
            fg="white",
            troughcolor="#383840",
            activebackground="#1DB954",
            highlightthickness=0,
            sliderlength=15
        )
        self.progress_slider.pack(
            side="left",
            fill="x",
            expand=True,
            padx=10
        )

        self.progress_slider.bind(
            "<ButtonPress-1>",
            self.start_seeking
        )
        self.progress_slider.bind(
            "<ButtonRelease-1>",
            self.finish_seeking
        )

        self.total_time_label = tk.Label(
            progress_frame,
            text="00:00",
            bg="#101014",
            fg="#AAAAAA"
        )
        self.total_time_label.pack(side="right")

        # Playback controls
        controls = tk.Frame(self.root, bg="#101014")
        controls.pack(pady=10)

        style = {
            "bg": "#292933",
            "fg": "white",
            "activebackground": "#1DB954",
            "activeforeground": "black",
            "font": ("Arial", 9, "bold"),
            "relief": "flat",
            "width": 9,
            "pady": 9
        }

        tk.Button(
            controls,
            text="PREV",
            command=self.previous_song,
            **style
        ).grid(row=0, column=0, padx=3)

        tk.Button(
            controls,
            text="PLAY",
            command=self.play_music,
            bg="#1DB954",
            fg="black",
            activebackground="#17A34A",
            font=("Arial", 10, "bold"),
            relief="flat",
            width=9,
            pady=9
        ).grid(row=0, column=1, padx=3)

        tk.Button(
            controls,
            text="PAUSE",
            command=self.pause_music,
            **style
        ).grid(row=0, column=2, padx=3)

        tk.Button(
            controls,
            text="RESUME",
            command=self.resume_music,
            **style
        ).grid(row=0, column=3, padx=3)

        tk.Button(
            controls,
            text="STOP",
            command=self.stop_music,
            **style
        ).grid(row=0, column=4, padx=3)

        tk.Button(
            controls,
            text="NEXT",
            command=self.next_song,
            **style
        ).grid(row=0, column=5, padx=3)

        # Volume
        volume_frame = tk.Frame(self.root, bg="#101014")
        volume_frame.pack(pady=5)

        tk.Label(
            volume_frame,
            text="VOLUME",
            bg="#101014",
            fg="white",
            font=("Arial", 9, "bold")
        ).pack(side="left", padx=10)

        self.volume_slider = tk.Scale(
            volume_frame,
            from_=0,
            to=100,
            orient="horizontal",
            variable=self.volume,
            command=self.set_volume,
            bg="#101014",
            fg="white",
            troughcolor="#383840",
            activebackground="#1DB954",
            highlightthickness=0,
            length=190
        )
        self.volume_slider.pack(side="left")

        self.volume_label = tk.Label(
            volume_frame,
            text="70%",
            bg="#101014",
            fg="#AAAAAA"
        )
        self.volume_label.pack(side="left", padx=8)

        # Shuffle and repeat
        mode_frame = tk.Frame(self.root, bg="#101014")
        mode_frame.pack(pady=8)

        self.shuffle_button = tk.Button(
            mode_frame,
            text="SHUFFLE: OFF",
            command=self.toggle_shuffle,
            bg="#292933",
            fg="white",
            relief="flat",
            padx=15,
            pady=8
        )
        self.shuffle_button.pack(side="left", padx=8)

        self.repeat_button = tk.Button(
            mode_frame,
            text="REPEAT: OFF",
            command=self.toggle_repeat,
            bg="#292933",
            fg="white",
            relief="flat",
            padx=15,
            pady=8
        )
        self.repeat_button.pack(side="left", padx=8)

    # ---------------- ALBUM ART ----------------

    def show_default_artwork(self):
        self.artwork_canvas.delete("all")

        self.artwork_canvas.create_rectangle(
            0, 0, 190, 190,
            fill="#252530",
            outline=""
        )

        self.artwork_canvas.create_text(
            95, 80,
            text="♫",
            font=("Arial", 75, "bold"),
            fill="#1DB954"
        )

        self.artwork_canvas.create_text(
            95, 150,
            text="MELODY",
            font=("Arial", 13, "bold"),
            fill="white"
        )

        self.album_image = None

    def load_album_art(self, song_path):
        folder = os.path.dirname(song_path)
        filename = os.path.splitext(os.path.basename(song_path))[0]

        candidates = [
            os.path.join(folder, filename + ".jpg"),
            os.path.join(folder, filename + ".jpeg"),
            os.path.join(folder, filename + ".png"),
            os.path.join(folder, "cover.jpg"),
            os.path.join(folder, "cover.jpeg"),
            os.path.join(folder, "cover.png"),
            os.path.join(folder, "folder.jpg"),
            os.path.join(folder, "folder.png"),
            os.path.join(folder, "album.jpg"),
            os.path.join(folder, "album.png")
        ]

        for image_path in candidates:
            if os.path.isfile(image_path):
                try:
                    image = Image.open(image_path).convert("RGB")
                    image = image.resize(
                        (190, 190),
                        Image.Resampling.LANCZOS
                    )

                    self.album_image = ImageTk.PhotoImage(image)
                    self.artwork_canvas.delete("all")
                    self.artwork_canvas.create_image(
                        95,
                        95,
                        image=self.album_image
                    )
                    return

                except (OSError, ValueError):
                    continue

        self.show_default_artwork()

    # ---------------- FAVOURITES ----------------

    def load_favourites(self):
        try:
            if os.path.exists(self.favourites_file):
                with open(
                    self.favourites_file,
                    "r",
                    encoding="utf-8"
                ) as file:
                    data = json.load(file)

                if isinstance(data, list):
                    self.favourites = set(data)

        except (OSError, json.JSONDecodeError):
            self.favourites = set()

    def save_favourites(self):
        try:
            with open(
                self.favourites_file,
                "w",
                encoding="utf-8"
            ) as file:
                json.dump(
                    sorted(self.favourites),
                    file,
                    indent=4
                )
        except OSError as error:
            messagebox.showerror(
                "Save Error",
                f"Unable to save favourites:\n{error}"
            )

    def toggle_favourite(self):
        index = self.get_selected_song_index()

        if index is None:
            messagebox.showinfo(
                "Select Song",
                "Please select a song first."
            )
            return

        song_path = self.songs[index]

        if song_path in self.favourites:
            self.favourites.remove(song_path)
            self.status_label.config(text="Removed from favourites")
        else:
            self.favourites.add(song_path)
            self.status_label.config(text="Added to favourites")

        self.save_favourites()
        self.refresh_playlist()

    def show_all_songs(self):
        self.show_favourites = False
        self.all_button.config(bg="#1DB954", fg="black")
        self.favourites_button.config(bg="#30303A", fg="white")
        self.refresh_playlist()

    def show_favourite_songs(self):
        self.show_favourites = True
        self.all_button.config(bg="#30303A", fg="white")
        self.favourites_button.config(bg="#1DB954", fg="black")
        self.refresh_playlist()

    def get_selected_song_index(self):
        selection = self.playlist.curselection()

        if not selection:
            return None

        visible_index = selection[0]

        if visible_index >= len(self.filtered_indices):
            return None

        return self.filtered_indices[visible_index]

    # ---------------- SEARCH AND PLAYLIST ----------------

    def refresh_playlist(self):
        if not hasattr(self, "playlist"):
            return

        self.playlist.delete(0, tk.END)
        self.filtered_indices = []

        query = self.search_text.get().strip().lower()

        for index, song_path in enumerate(self.songs):
            filename = os.path.basename(song_path)

            if self.show_favourites and song_path not in self.favourites:
                continue

            if query and query not in filename.lower():
                continue

            display_name = filename

            if song_path in self.favourites:
                display_name = "★ " + display_name

            self.playlist.insert(tk.END, display_name)
            self.filtered_indices.append(index)

        if self.current_index in self.filtered_indices:
            visible_index = self.filtered_indices.index(
                self.current_index
            )
            self.playlist.selection_set(visible_index)
            self.playlist.activate(visible_index)

        self.song_count_label.config(
            text=f"{len(self.filtered_indices)} SONGS"
        )

    # ---------------- MUSIC LIBRARY ----------------

    def load_folder(self):
        folder = filedialog.askdirectory()

        if not folder:
            return

        self.stop_music()
        self.songs = []
        self.current_index = -1

        supported_formats = (".mp3", ".wav", ".ogg")

        for filename in sorted(os.listdir(folder)):
            if filename.lower().endswith(supported_formats):
                self.songs.append(
                    os.path.join(folder, filename)
                )

        self.refresh_playlist()
        self.show_default_artwork()

        self.now_playing.config(text="No song selected")
        self.song_subtitle.config(
            text="Choose a song from your library"
        )

        if self.songs:
            self.status_label.config(
                text=f"{len(self.songs)} SONGS LOADED"
            )
        else:
            self.status_label.config(text="NO MUSIC FILES FOUND")
            messagebox.showinfo(
                "No Music Found",
                "No MP3, WAV or OGG files were found."
            )

    def play_selected(self, event=None):
        index = self.get_selected_song_index()

        if index is not None:
            self.play_song(index)

    # ---------------- PLAYBACK ----------------

    def play_music(self):
        if not self.songs:
            messagebox.showwarning(
                "No Songs",
                "Please open a music folder first."
            )
            return

        index = self.get_selected_song_index()

        if index is not None:
            self.play_song(index)
        elif self.current_index >= 0 and not self.is_stopped:
            self.resume_music()
        else:
            self.play_song(0)

    def play_song(self, index):
        if not self.songs or not 0 <= index < len(self.songs):
            return

        try:
            pygame.mixer.music.stop()

            song_path = self.songs[index]
            pygame.mixer.music.load(song_path)

            self.current_index = index
            self.seek_offset = 0
            self.is_paused = False
            self.is_stopped = False
            self.song_finished_handled = False

            try:
                self.song_duration = pygame.mixer.Sound(
                    song_path
                ).get_length()
            except pygame.error:
                self.song_duration = 0

            pygame.mixer.music.play()

            self.now_playing.config(
                text=os.path.basename(song_path)
            )
            self.song_subtitle.config(
                text=os.path.dirname(song_path)
            )

            self.load_album_art(song_path)
            self.refresh_playlist()
            self.reset_progress()

            self.status_label.config(text="PLAYING")

        except (pygame.error, OSError) as error:
            self.is_stopped = True
            self.song_finished_handled = True

            messagebox.showerror(
                "Playback Error",
                f"Unable to play this song:\n{error}"
            )

    def pause_music(self):
        if not self.is_stopped and not self.is_paused:
            pygame.mixer.music.pause()
            self.is_paused = True
            self.status_label.config(text="PAUSED")

    def resume_music(self):
        if self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False
            self.status_label.config(text="PLAYING")
        elif self.is_stopped and self.current_index >= 0:
            self.play_song(self.current_index)

    def stop_music(self):
        pygame.mixer.music.stop()
        self.is_paused = False
        self.is_stopped = True
        self.song_finished_handled = True
        self.seek_offset = 0
        self.reset_progress()
        self.status_label.config(text="STOPPED")

    def next_song(self):
        if not self.songs:
            return

        if self.shuffle_enabled and len(self.songs) > 1:
            choices = [
                i for i in range(len(self.songs))
                if i != self.current_index
            ]
            next_index = random.choice(choices)
        else:
            next_index = (self.current_index + 1) % len(self.songs)

        self.play_song(next_index)

    def previous_song(self):
        if not self.songs:
            return

        if self.current_index < 0:
            self.play_song(0)
            return

        previous_index = (self.current_index - 1) % len(self.songs)
        self.play_song(previous_index)

    # ---------------- SHUFFLE AND REPEAT ----------------

    def toggle_shuffle(self):
        self.shuffle_enabled = not self.shuffle_enabled

        if self.shuffle_enabled:
            self.shuffle_button.config(
                text="SHUFFLE: ON",
                fg="#1DB954"
            )
            self.status_label.config(text="SHUFFLE ENABLED")
        else:
            self.shuffle_button.config(
                text="SHUFFLE: OFF",
                fg="white"
            )
            self.status_label.config(text="SHUFFLE DISABLED")

    def toggle_repeat(self):
        modes = ["OFF", "ONE", "ALL"]
        current_position = modes.index(self.repeat_mode)

        self.repeat_mode = modes[
            (current_position + 1) % len(modes)
        ]

        self.repeat_button.config(
            text=f"REPEAT: {self.repeat_mode}",
            fg="#1DB954" if self.repeat_mode != "OFF" else "white"
        )

        self.status_label.config(
            text=f"REPEAT {self.repeat_mode}"
        )

    def handle_song_finished(self):
        if self.song_finished_handled:
            return

        self.song_finished_handled = True

        if self.repeat_mode == "ONE":
            self.play_song(self.current_index)

        elif self.repeat_mode == "ALL":
            if self.shuffle_enabled:
                self.next_song()
            else:
                next_index = (self.current_index + 1) % len(self.songs)
                self.play_song(next_index)

        elif self.current_index < len(self.songs) - 1:
            if self.shuffle_enabled:
                self.next_song()
            else:
                self.play_song(self.current_index + 1)

        else:
            self.is_stopped = True
            self.is_paused = False
            self.status_label.config(text="PLAYLIST FINISHED")
            self.reset_progress()

    # ---------------- VOLUME ----------------

    def set_volume(self, value=None):
        volume_value = self.volume.get() / 100
        pygame.mixer.music.set_volume(volume_value)
        self.volume_label.config(
            text=f"{int(self.volume.get())}%"
        )

    # ---------------- PROGRESS AND SEEK ----------------

    def format_time(self, seconds):
        seconds = max(0, int(seconds))
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{minutes:02d}:{remaining_seconds:02d}"

    def reset_progress(self):
        self.progress_value.set(0)
        self.current_time_label.config(text="00:00")
        self.total_time_label.config(
            text=self.format_time(self.song_duration)
        )

    def start_seeking(self, event):
        if self.current_index >= 0 and self.song_duration > 0:
            self.is_seeking = True

    def seek_song(self, value):
        if self.is_seeking and self.song_duration > 0:
            self.current_time_label.config(
                text=self.format_time(float(value))
            )

    def finish_seeking(self, event):
        if not self.is_seeking:
            return

        self.is_seeking = False

        if self.song_duration <= 0 or self.current_index < 0:
            return

        position = min(
            self.progress_value.get(),
            self.song_duration
        )

        was_playing = not self.is_paused and not self.is_stopped

        try:
            pygame.mixer.music.play(start=position)
            self.seek_offset = position
            self.song_finished_handled = False
            self.is_stopped = False

            if not was_playing:
                pygame.mixer.music.pause()
                self.is_paused = True
            else:
                self.is_paused = False

            self.current_time_label.config(
                text=self.format_time(position)
            )

        except pygame.error as error:
            messagebox.showerror(
                "Seek Error",
                f"Unable to seek in this audio file:\n{error}"
            )

    def update_progress(self):
        if (
            self.current_index >= 0
            and not self.is_stopped
            and not self.is_paused
        ):
            if not pygame.mixer.music.get_busy():
                self.handle_song_finished()

            elif not self.is_seeking:
                elapsed = pygame.mixer.music.get_pos() / 1000

                if elapsed >= 0:
                    current_position = min(
                        self.seek_offset + elapsed,
                        self.song_duration
                    )

                    self.progress_value.set(current_position)
                    self.current_time_label.config(
                        text=self.format_time(current_position)
                    )
                    self.total_time_label.config(
                        text=self.format_time(self.song_duration)
                    )

        self.progress_job = self.root.after(
            500,
            self.update_progress
        )

    # ---------------- CLOSE PLAYER ----------------

    def close_player(self):
        if self.progress_job is not None:
            self.root.after_cancel(self.progress_job)

        pygame.mixer.music.stop()
        pygame.mixer.quit()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = MusicPlayer(root)
    root.mainloop()

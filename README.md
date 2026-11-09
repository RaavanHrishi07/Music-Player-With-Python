# 🎵 Melody – Music Player With Python

A feature-rich desktop music player built using **Python, Tkinter, Pygame and Pillow**. Melody provides a modern dark interface with music playback, playlist management, search, favourites, shuffle, repeat, volume control, progress tracking and album artwork.

## ✨ Features

- 🎶 **Music Playback** – Play, pause, resume and stop audio.
- ⏭️ **Next & Previous** – Navigate between songs.
- 🔊 **Volume Control** – Adjust playback volume.
- 🔍 **Song Search** – Quickly find songs by filename.
- ⭐ **Favourites** – Add or remove favourite songs.
- 💾 **Persistent Favourites** – Save favourite selections in `favourites.json`.
- 🔀 **Shuffle Mode** – Play songs in random order.
- 🔁 **Repeat Modes** – Repeat One, Repeat All or turn repeat off.
- ⏱️ **Progress Bar** – Track playback progress.
- ⏩ **Seek Control** – Jump to a specific position in a song.
- 🖼️ **Album Artwork** – Display local album cover images.
- 🌙 **Modern Dark UI** – Clean interface with green accents.
- 🎧 **Multiple Audio Formats** – Supports MP3, WAV and OGG.

## 🛠️ Technologies Used

- Python 3
- Tkinter
- Pygame
- Pillow
- JSON

## 📋 Requirements

- Python 3.11 or later recommended
- Pygame
- Pillow

## 🚀 Installation

**1. Clone the repository**

```bash
git clone https://github.com/RaavanHrishi07/Music-Player-With-Python.git
```

**2. Open the project directory**

```bash
cd Music-Player-With-Python
```

**3. Install dependencies**

```bash
pip install pygame pillow
```

**4. Run the application**

```bash
python "Music Player With Python.py"
```

## 🎼 How to Use

1. Launch the application.
2. Click **OPEN MUSIC FOLDER**.
3. Select a folder containing your music files.
4. Double-click a song to play it.
5. Use playback controls to play, pause, resume, stop or navigate between songs.
6. Adjust the volume using the volume slider.
7. Search for songs using the search box.
8. Select a song and click **TOGGLE FAVOURITE** to save it.
9. Use Shuffle and Repeat controls to customise playback.
10. Drag the progress slider to seek through a song.

## 🖼️ Album Artwork

Melody automatically looks for local album artwork in the selected music folder.

Supported image formats:

- JPG
- JPEG
- PNG

Recognised image filenames include:

```text
cover.jpg
cover.png
folder.jpg
folder.png
album.jpg
album.png
Song Name.jpg
```

If no matching image is found, the application displays default artwork.

## 📁 Project Structure

```text
Music-Player-With-Python/
│
├── Music Player With Python.py
├── README.md
├── LICENSE
├── .gitignore
└── favourites.json
```

**Note:** `favourites.json` is generated automatically when favourites are saved. It stores your favourite song paths locally.

## 🔮 Future Improvements

- Internet-based music streaming
- Audio metadata extraction
- Embedded album artwork support
- Keyboard shortcuts
- Playlist creation and export
- Windows executable packaging

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Hrishikesh Sharma**

GitHub: [RaavanHrishi07](https://github.com/RaavanHrishi07)

---

⭐ If you find this project useful, consider giving the repository a star!
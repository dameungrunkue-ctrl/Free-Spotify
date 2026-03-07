import os
import sys
import yt_dlp
import vlc

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QListWidget, QLabel, QSlider
)
from PyQt6.QtCore import Qt, QTimer

# Fix for VLC DLL location (Windows)
os.add_dll_directory(r"C:\Program Files\VideoLAN\VLC")


class SpotifyClone(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("YouTube Music Player")
        self.setGeometry(200, 200, 600, 500)

        self.tracks = []
        self.current_url = None
        self.repeat = False

        self.player = vlc.MediaPlayer("--no-video")

        # allow keyboard input
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        layout = QVBoxLayout()

        title = QLabel("Spotify-style YouTube Music Player")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # SEARCH BAR
        search_layout = QHBoxLayout()

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search for a song...")
        search_layout.addWidget(self.search_box)

        search_button = QPushButton("Search")
        search_button.clicked.connect(self.search_music)
        search_layout.addWidget(search_button)

        layout.addLayout(search_layout)

        # RESULTS LIST
        self.results = QListWidget()
        self.results.itemClicked.connect(self.play_music)
        layout.addWidget(self.results)

        # CONTROLS
        controls = QHBoxLayout()

        play_btn = QPushButton("Play")
        play_btn.clicked.connect(self.resume_music)
        controls.addWidget(play_btn)

        pause_btn = QPushButton("Pause")
        pause_btn.clicked.connect(self.pause_music)
        controls.addWidget(pause_btn)

        stop_btn = QPushButton("Stop")
        stop_btn.clicked.connect(self.stop_music)
        controls.addWidget(stop_btn)

        # REPEAT BUTTON
        self.repeat_btn = QPushButton("Repeat OFF")
        self.repeat_btn.clicked.connect(self.toggle_repeat)
        controls.addWidget(self.repeat_btn)

        layout.addLayout(controls)

        # VOLUME
        volume_layout = QHBoxLayout()

        volume_label = QLabel("Volume")
        volume_layout.addWidget(volume_label)

        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(70)
        self.volume_slider.valueChanged.connect(self.change_volume)

        volume_layout.addWidget(self.volume_slider)

        layout.addLayout(volume_layout)

        self.setLayout(layout)

        # TIMER to detect song ending
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_song_end)
        self.timer.start(1000)

    # SEARCH MUSIC
    def search_music(self):

        query = self.search_box.text()

        if not query:
            return

        self.results.clear()
        self.tracks.clear()

        ydl_opts = {
            "quiet": True,
            "extract_flat": True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch15:{query}", download=False)

        for entry in info["entries"]:

            title = entry["title"]
            url = f"https://youtube.com/watch?v={entry['id']}"

            self.tracks.append(url)
            self.results.addItem(title)

    # PLAY MUSIC
    def play_music(self, item):

        index = self.results.row(item)
        url = self.tracks[index]

        ydl_opts = {"quiet": True}

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        stream_url = None

        for f in info["formats"]:
            if f.get("acodec") != "none":
                stream_url = f["url"]
                break

        if stream_url:
            self.current_url = stream_url
            media = vlc.Media(stream_url)
            self.player.set_media(media)
            self.player.play()

    # CONTROLS
    def pause_music(self):
        self.player.pause()

    def resume_music(self):
        self.player.play()

    def stop_music(self):
        self.player.stop()

    def change_volume(self, value):
        self.player.audio_set_volume(value)

    # REPEAT TOGGLE
    def toggle_repeat(self):

        self.repeat = not self.repeat

        if self.repeat:
            self.repeat_btn.setText("Repeat ON")
        else:
            self.repeat_btn.setText("Repeat OFF")

    # CHECK SONG END
    def check_song_end(self):

        if self.repeat and self.current_url:
            state = self.player.get_state()

            if state == vlc.State.Ended:
                media = vlc.Media(self.current_url)
                self.player.set_media(media)
                self.player.play()

    # SPACEBAR PLAY/PAUSE
    def keyPressEvent(self, event):

        if event.key() == Qt.Key.Key_Space:

            state = self.player.get_state()

            if state == vlc.State.Playing:
                self.player.pause()
            else:
                self.player.play()


# RUN APP
app = QApplication(sys.argv)

window = SpotifyClone()
window.show()

sys.exit(app.exec())
import os
import shutil
from tkinter import Listbox, filedialog, simpledialog, ttk, DoubleVar, Tk, END
import vlc  # pip install python-vlc
from tinytag import TinyTag
from db import database as db  # your database module

SONG_DIR = os.path.join(os.path.dirname(__file__), "..", "songs")
os.makedirs(SONG_DIR, exist_ok=True)

class PlayerGUI:
    def __init__(self, parent, app):
        self.app = app
        self.frame = ttk.LabelFrame(parent, text="Songs")
        self.frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        # Library listbox
        self.listbox = Listbox(self.frame, height=10)
        self.listbox.pack(fill="both", expand=True, padx=5, pady=5)

        # Playback buttons
        self.add_to_playlist_btn = ttk.Button(self.frame, text="Add to Playlist", command=self.add_song_to_playlist)
        self.play_btn = ttk.Button(self.frame, text="Play", command=self.play_song)
        self.stop_btn = ttk.Button(self.frame, text="Stop", command=self.stop_song)
        self.add_to_playlist_btn.pack(side="right", padx=5)
        self.play_btn.pack(side="left", padx=5)
        self.stop_btn.pack(side="left", padx=5)

        # Progress bar (seek)
        self.progress_var = DoubleVar()
        self.progress_var.set(0)
        self.progress = ttk.Scale(self.frame, from_=0, to=100, variable=self.progress_var, orient="horizontal")
        self.progress.pack(fill="x")

        # VLC player
        self.player = None
        self.current_song = None
        self.update_job = None
        self.repeat = False
        self.seeking = False
        self.playing = False
        self.song_length = 0
        self.paused = False
        self.current_pos = 0  # in milliseconds

        # Load library songs
        self.load_library_songs()

    # Load all songs from DB
    def load_library_songs(self):
        self.listbox.delete(0, "end")
        self.songs = db.get_songs()
        for s in self.songs:
            self.listbox.insert("end", s["title"] or s["filename"])

    # Play selected song
    def play_song(self):
        sel = self.listbox.curselection()
        if not sel:
            return

        index = sel[0]
        song = self.songs[index]
        filepath = os.path.join(SONG_DIR, song["filename"])

        self.player = vlc.MediaPlayer(filepath)
        self.player.play()
        
        self.playing = True
        self.song_length = 0  # temporarily unknown
        self.progress.set(0)

        # Start updating progress
        self.update_progress()


    # Stop playback
    def stop_song(self):
        if self.player:
            self.player.stop()
        self.playing = False
        self.progress.set(0)
        if self.update_job:
            self.frame.after_cancel(self.update_job)
            self.update_job = None

    # Update progress bar
    def update_progress(self):
        if self.player and self.playing and not self.seeking:
            length_ms = self.player.get_length()
            pos_ms = self.player.get_time()

            if length_ms > 0:
                self.song_length = length_ms / 1000
                self.progress.config(to=self.song_length)

            if pos_ms > 0 and self.song_length > 0:
                pos_s = pos_ms / 1000
                pos_s = min(pos_s, self.song_length)  # clamp
                self.progress.set(pos_s)

                # Check for end-of-song with tolerance
                if pos_s >= self.song_length - 0.5:
                    self.stop_song()
                    return

        self.update_job = self.frame.after(200, self.update_progress)

    # Seek song
    def seek_song(self, value):
        if self.player:
            self.seeking = True
            self.player.set_time(int(float(value) * 1000))
            self.seeking = False

    # Add song to playlist
    def add_song_to_playlist(self):
        sel = self.listbox.curselection()
        if not sel:
            return
        song_index = sel[0]
        song = self.songs[song_index]
        song_id = song["id"]

        playlists = db.get_playlists()
        if not playlists:
            return

        playlist_names = [pl["name"] for pl in playlists]
        choice = simpledialog.askstring(
            "Add to Playlist",
            "Choose playlist:\n" + "\n".join(f"{i+1}. {n}" for i, n in enumerate(playlist_names))
        )
        if not choice:
            return

        try:
            index = int(choice) - 1
            playlist_id = playlists[index]["id"]
        except (ValueError, IndexError):
            return

        db.add_song_to_playlist(playlist_id, song_id)
        self.app.playlists.load_playlists()

    # Add new songs to library
    def add_songs_to_library(self):
        filepaths = filedialog.askopenfilenames(
            title="Select Songs",
            filetypes=[("MP3 files", "*.mp3"), ("All files", "*.*")]
        )

        os.makedirs(SONG_DIR, exist_ok=True)

        for path in filepaths:
            filename = os.path.basename(path)
            dest = os.path.join(SONG_DIR, filename)

            if not os.path.exists(dest):
                shutil.copy(path, dest)

            # Extract metadata
            tag = TinyTag.get(path)
            title = tag.title or filename
            artist = tag.artist or ""
            album = tag.album or ""
            duration = tag.duration or 0

            db.add_song(path, title=title, artist=artist, album=album, duration=duration)

        self.load_library_songs()


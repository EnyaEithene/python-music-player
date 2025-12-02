import os
import shutil
from tkinter import Listbox, filedialog, simpledialog, ttk, DoubleVar, END
import vlc
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

        # Buttons
        self.add_to_playlist_btn = ttk.Button(self.frame, text="Add to Playlist", command=self.add_song_to_playlist)
        self.play_btn = ttk.Button(self.frame, text="Play", command=self.toggle_play)
        self.stop_btn = ttk.Button(self.frame, text="Stop", command=self.stop_song)
        self.add_to_playlist_btn.pack(side="right", padx=5)
        self.play_btn.pack(side="left", padx=5)
        self.stop_btn.pack(side="left", padx=5)

        # Progress bar (seek)
        self.progress_var = DoubleVar()
        self.progress_var.set(0)
        self.progress = ttk.Scale(self.frame, from_=0, to=100, variable=self.progress_var, orient="horizontal", command=self.seek_song)
        self.progress.pack(fill="x")

        # VLC player
        self.player = None
        self.current_song = None
        self.update_job = None
        self.repeat = False
        self.seeking = False
        self.playing = False
        self.paused = False
        self.current_pos = 0  # in milliseconds
        self.song_length = 0

        # Load songs from DB
        self.load_library_songs()

    # Load songs
    def load_library_songs(self):
        self.listbox.delete(0, END)
        library_songs = db.get_songs()
        self.songs = library_songs  # keep self.songs synced
        for s in library_songs:
            self.listbox.insert(END, s["title"] or s["filename"])

    def load_songs_for_playlist(self, playlist_id):
        self.listbox.delete(0, END)
        playlist_songs = db.get_songs_in_playlist(playlist_id)
        self.songs = playlist_songs  # update current songs list
        for song in playlist_songs:
            self.listbox.insert(END, song["title"] or song["filename"])

    # Play / resume toggle
    def toggle_play(self):
        sel = self.listbox.curselection()
        if not sel:
            return

        index = sel[0]
        song = self.songs[index]
        new_song_path = os.path.join(SONG_DIR, song["filename"])

        # If a different song is selected, stop old and play new
        if self.current_song != new_song_path:
            if self.player:
                self.player.stop()
            self.player = vlc.MediaPlayer(new_song_path)
            self.current_song = new_song_path
            self.current_pos = 0
            self.player.play()
            self.playing = True
            self.paused = False
            self.update_progress()
            return

        # Otherwise handle play/pause/restart for the same song
        state = self.player.get_state() if self.player else vlc.State.Stopped

        if state in (vlc.State.Ended, vlc.State.Stopped):
            self.player.stop()
            self.player = vlc.MediaPlayer(self.current_song)
            self.current_pos = 0
            self.player.play()
            self.playing = True
            self.paused = False
            self.update_progress()
        elif state == vlc.State.Playing:
            self.player.pause()
            self.paused = True
            self.playing = False
        elif state == vlc.State.Paused:
            self.player.play()
            self.paused = False
            self.playing = True

    # Stop completely
    def stop_song(self):
        if self.player:
            self.player.stop()
        self.playing = False
        self.paused = False
        self.current_pos = 0
        self.progress_var.set(0)
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

            if pos_ms >= 0 and self.song_length > 0:
                pos_s = pos_ms / 1000
                pos_s = min(pos_s, self.song_length)
                self.progress_var.set(pos_s)

                # End-of-song
                if pos_s >= self.song_length - 0.5:
                    if self.repeat:
                        self.toggle_play()  # replay
                    else:
                        self.stop_song()
                        return

        self.update_job = self.frame.after(200, self.update_progress)

    # Seek
    def seek_song(self, value):
        if self.player:
            self.seeking = True
            self.player.set_time(int(float(value) * 1000))
            self.current_pos = self.player.get_time()
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


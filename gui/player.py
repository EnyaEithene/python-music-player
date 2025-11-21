from tkinter import *
from tkinter import ttk
from tkinter import filedialog, simpledialog
from tinytag import TinyTag
import db.database as db

class PlayerGUI:
    # Initializare GUI pentru lista de melodii si meniul de redare
    def __init__(self, parent, app):
        # Fereastra player
        self.app = app
        self.frame = ttk.LabelFrame(parent, text="Songs")
        self.frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        # Lista melodii
        self.listbox = Listbox(self.frame, height=10)
        self.listbox.pack(fill="both", expand=True, padx=5, pady=5)

        # Butoane player
        self.add_to_playlist_btn = ttk.Button(self.frame, text="Add to Playlist", command=self.add_song_to_playlist)
        self.play_btn = ttk.Button(self.frame, text="Play", command=self.play_song)
        self.stop_btn = ttk.Button(self.frame, text="Stop", command=self.stop_song)
        self.add_to_playlist_btn.pack(side="right", padx=5)
        self.play_btn.pack(side="left", padx=5)
        self.stop_btn.pack(side="left", padx=5)
        
        # Incarca melodiile din BD
        self.load_songs()
    
    # Actualizare lista melodii
    def load_songs(self):
        self.listbox.delete(0, END)
        for song in db.get_songs():  # you would need a get_songs() in database.py
            self.listbox.insert(END, song["title"])

    # Redare melodie
    def play_song(self):
        print("Play song")

    # Oprire redare melodie
    def stop_song(self):
        print("Stop song")

    # Adaugare melodie la playlist selectat
    def add_song_to_playlist(self):
        # 1. Get selected song
        sel = self.listbox.curselection()
        if not sel:
            return
        song_index = sel[0]
        song = db.get_songs()[song_index]  # from the library
        song_id = song["id"]

        # 2. Ask user to choose a playlist
        playlists = db.get_playlists()
        if not playlists:
            return  # no playlists exist

        # Make a simple list of playlist names
        playlist_names = [pl["name"] for pl in playlists]
        choice = simpledialog.askstring(
            "Add to Playlist",
            "Choose playlist:\n" + "\n".join(f"{i+1}. {n}" for i, n in enumerate(playlist_names))
        )

        if not choice:
            return  # user cancelled

        try:
            # Convert user input to index
            index = int(choice) - 1
            playlist_id = playlists[index]["id"]
        except (ValueError, IndexError):
            return  # invalid input

        # 3. Add song to playlist
        db.add_song_to_playlist(playlist_id, song_id)
        # Optional: refresh playlist view
        self.app.playlists.load_playlists()

    # Afiseaza melodii pentru playlist selectat
    def load_songs_for_playlist(self, playlist_id):
        self.listbox.delete(0, END)
        songs = db.get_songs_in_playlist(playlist_id)
        for song in songs:
            self.listbox.insert(END, song["title"])

    # Afiseaza toate melodiile din librarie
    def load_library_songs(self):
        self.listbox.delete(0, "end")
        songs = db.get_songs()
        for s in songs:
            self.listbox.insert("end", s["title"] or s["filename"])

    # Adauga melodie in librarie
    def add_songs_to_library(self):
        filepaths = filedialog.askopenfilenames(
            title="Select Songs",
            filetypes=[("MP3 files", "*.mp3"), ("All files", "*.*")]
        )

        for path in filepaths:
            # Check if song already exists
            song = db.get_song_by_filename(path)
            if not song:
                # Extract metadata
                tag = TinyTag.get(path)
                title = tag.title or path.split("/")[-1]   # fallback to filename
                artist = tag.artist or ""
                album = tag.album or ""
                duration = tag.duration or 0

                # Add to database with metadata
                db.add_song(path, title=title, artist=artist, album=album, duration=duration)

        self.load_library_songs()

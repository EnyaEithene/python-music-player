# Importari
import os
import shutil
from tkinter import ttk, simpledialog, Listbox, messagebox, filedialog
from tkinter import *
import vlc
from tinytag import TinyTag
from db import database as db  
from gui.rightclick_menu import setup_library_menu

# Director pentru salvare melodii
SONG_DIR = os.path.join(os.path.dirname(__file__), "..", "songs")
os.makedirs(SONG_DIR, exist_ok=True)

class PlayerGUI:
    #--------------- Initializare clasa ---------------
    def __init__(self, parent, app):
        # Sectiune fereastra aplicatie pentru melodii
        self.app = app
        self.frame = ttk.LabelFrame(parent, text="Songs")
        self.frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        # Lista melodii
        self.listbox = Listbox(self.frame, height=10)
        self.listbox.pack(fill="both", expand=True, padx=5, pady=5)

        # Bara progres melodie (seek)
        self.progress_var = DoubleVar()
        self.progress_var.set(0)
        self.progress = ttk.Scale(self.frame, from_=0, to=100, variable=self.progress_var, orient="horizontal", command=self.seek_song)
        self.progress.pack(fill="x", pady=(5,5))

        # Butoane
        self.add_to_playlist_btn = ttk.Button(self.frame, text="Add to Playlist", command=self.add_song_to_playlist)
        self.play_btn = ttk.Button(self.frame, text="Play/Pause", command=self.toggle_play)
        self.stop_btn = ttk.Button(self.frame, text="Stop", command=self.stop_song)
        self.add_to_playlist_btn.pack(side="right", padx=10)
        self.play_btn.pack(side="left", padx=10)
        self.stop_btn.pack(side="left", padx=10)

        # Optiuni de repetare melodii/playlist
        self.repeat_var = StringVar()
        self.repeat_var.set("No Repeat")        # Optiune default

        self.repeat_menu = ttk.OptionMenu(
            self.frame,
            self.repeat_var,
            "No Repeat",                        # Optiune default
            "No Repeat",
            "Repeat Playlist",
            "Repeat Song"
        )
        self.repeat_menu.pack(side="right", padx=10)

        # Variabile pentru VLC player
        self.player = None                      # Este pornit player-ul?
        self.current_song = None                # Melodia redata
        self.update_job = None                  # Actualizare bara de progres
        # self.repeat = False                     # Optiunea de repetare aleasa
        self.seeking = False                    # Progresul melodiei este masurat sau nu
        self.playing = False                    # Melodia este activ redata sau nu
        self.paused = False                     # Melodia este pusa pe pauza sau nu
        self.current_pos = 0                    # Progres melodie in ms
        self.song_length = 0                    # Durata melodie

        # Preluare și afișare melodii stocate în BD
        self.load_library_songs()

        # Right-click menu
        setup_library_menu(self.listbox, lambda: self.songs, db, self.load_library_songs, self.add_song_to_playlist)

    #--------------- Preluare și afișare toate melodiile stocate în BD --------------- 
    def load_library_songs(self):
        self.listbox.delete(0, END)
        library_songs = db.get_songs()
        self.songs = library_songs
        for s in library_songs:
            self.listbox.insert(END, s["title"] or s["filename"])

    #--------------- Preluare și afișare melodii playlist stocate în BD --------------- 
    def load_songs_for_playlist(self, playlist_id):
        self.listbox.delete(0, END)
        playlist_songs = db.get_songs_in_playlist(playlist_id)
        self.songs = playlist_songs 
        for song in playlist_songs:
            self.listbox.insert(END, song["title"] or song["filename"])

    #--------------- Oprire completa a melodiei --------------- 
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

    #--------------- Redare/Punere pe pauza a melodiei --------------- 
    def toggle_play(self):
        sel = self.listbox.curselection()
        if not sel:                                         # Se reda prima melodie daca nu este niciuna din lista selectata
            if not self.songs:
                return
            index = 0
        else:
            index = sel[0]

        song = self.songs[index]
        new_song_path = os.path.join(SONG_DIR, song["filename"])

        if self.current_song != new_song_path:              # Reda o alta melodie in locul celei curente daca e selectata si este apasat butonul play
            if self.player:
                self.player.stop()
            self.current_song = new_song_path
            self.current_index = index
            self.player = vlc.MediaPlayer(self.current_song)
            self.current_pos = 0
            self.player.play()
            self.playing = True
            self.paused = False
            self.update_progress()
            return

        # Verificare stare melodie curenta
        state = self.player.get_state() if self.player else vlc.State.Stopped

        if state in (vlc.State.Ended, vlc.State.Stopped):   # Melodia s-a incheiat sau a fost oprita => o reda din nou
            if self.player:
                self.player.stop()
            self.player = vlc.MediaPlayer(self.current_song)
            self.current_pos = 0
            self.player.play()
            self.playing = True
            self.paused = False
            self.update_progress()
        elif state == vlc.State.Playing:                    # Melodia este in redare => o pune in pauza
            self.player.pause()
            self.paused = True
            self.playing = False
        elif state == vlc.State.Paused:                     # Melodia este pe pauza => continua redarea
            self.player.play()
            self.paused = False
            self.playing = True

    #--------------- Redare melodie urmatoare ---------------
    def play_next_song(self):
        repeat_option = self.repeat_var.get()               # "No Repeat", "Repeat Song", "Repeat Playlist"

        if repeat_option == "Repeat Song":                  # "Repeat Song" => Repetare melodie dupa ce se incheie
            if self.player:
                self.player.stop()
            self.player = vlc.MediaPlayer(self.current_song)
            self.player.play()
            self.playing = True
            self.paused = False
            self.progress_var.set(0)
            self.update_progress()
            return

        # Redare melodie urmatoare daca exista (nu e ultima din lista)
        if self.current_index is not None and self.current_index + 1 < len(self.songs):
            self.current_index += 1
            next_song = self.songs[self.current_index]
            self.current_song = os.path.join(SONG_DIR, next_song["filename"])
            if self.player:
                self.player.stop()
            self.player = vlc.MediaPlayer(self.current_song)
            self.player.play()

            self.playing = True
            self.paused = False
            self.progress_var.set(0)
            self.update_progress()
        else:
            if repeat_option == "Repeat Playlist":          # "Repeat playlist" => Repetare playlist de la capat 
                self.current_index = 0
                first_song = self.songs[self.current_index]
                self.current_song = os.path.join(SONG_DIR, first_song["filename"])
                if self.player:
                    self.player.stop()
                self.player = vlc.MediaPlayer(self.current_song)
                self.player.play()

                self.playing = True
                self.paused = False
                self.progress_var.set(0)
                self.update_progress()
            else:                                           # "No Repeat" => Se opreste redarea complet
                self.stop_song()
                self.current_index = None
                self.current_song = None

    #--------------- Actualizare bara de redare melodie --------------- 
    def update_progress(self):
        # Daca este redata o melodie dar nu are progresul masurat
        if self.player and self.playing and not self.seeking:
            length_ms = self.player.get_length()            # Durata melodie curenta
            pos_ms = self.player.get_time()                 # Progres redare melodie

            if length_ms > 0:                               # Traducere a duratei pentru afisare corecta a barei de progres
                self.progress.config(to=length_ms / 1000)

            if pos_ms >= 0 and length_ms > 0:               # Aproximare progres redare melodie pentru afisare
                pos_s = min(pos_ms / 1000, length_ms / 1000)
                self.progress_var.set(pos_s)

                # Redare melodie urmatoare daca s-a incheiat cea curenta
                if pos_s >= (length_ms / 1000) - 0.2:
                    self.play_next_song()
                    return

        # Actualizare progres la fiecare 200ms
        self.update_job = self.frame.after(200, self.update_progress)

    #--------------- Posibilitate de sarire la anumite parti din melodie --------------- 
    def seek_song(self, value):
        if self.player:
            self.seeking = True
            self.player.set_time(int(float(value) * 1000))
            self.current_pos = self.player.get_time()
            self.seeking = False

    #---------------  Adaugare melodie la playlist --------------- 
    def add_song_to_playlist(self, song_id=None):
        sel = self.listbox.curselection()                   # Selectare melodie din lista si preluare id
        if not sel:
            return 
        song = self.songs[sel[0]]
        song_id = song["id"]
        
        playlists = db.get_playlists()                      # Preluare playlist-uri disponibile
        if not playlists:
            return
 
        win = Toplevel(self.frame)                          # Fereastra selectie playlist
        win.title("Add to Playlist")
        win.geometry("250x300")
        win.transient(self.frame)
        win.grab_set()

        ttk.Label(win, text="Choose playlist:").pack(pady=5)

        lb = Listbox(win)
        lb.pack(fill="both", expand=True, padx=10, pady=5)

        for pl in playlists:
            lb.insert(END, pl["name"])
         
        def confirm():                                      # Functie confirmare selectie
            sel = lb.curselection()
            if not sel:
                return
            playlist = playlists[sel[0]]
            db.add_song_to_playlist(playlist["id"], song_id)
            win.destroy()
            self.app.playlists.load_playlists()

        btn_frame = ttk.Frame(win)                          # Butoane
        btn_frame.pack(fill="x", pady=10)
        ttk.Button(btn_frame, text="Add", command=confirm).pack(side="left", expand=True, padx=10)
        ttk.Button(btn_frame, text="Cancel", command=win.destroy).pack(side="right", expand=True, padx=10)

    #--------------- Adaugare melodii in aplicatie (library) ----------------
    def add_songs_to_library(self):
        filepaths = filedialog.askopenfilenames(            # Selectie melodie din memorie
            title="Select Songs",
            filetypes=[("MP3 files", "*.mp3"), ("All files", "*.*")]
        )
        os.makedirs(SONG_DIR, exist_ok=True)

        for path in filepaths:                              # Copiere melodie in folder-ul "songs"
            filename = os.path.basename(path)
            dest = os.path.join(SONG_DIR, filename)
            if not os.path.exists(dest):
                shutil.copy(path, dest)

            tag = TinyTag.get(path)                         # Extragere metadata
            title = tag.title or filename
            artist = tag.artist or ""
            album = tag.album or ""
            duration = tag.duration or 0

            db.add_song(path, title=title, artist=artist, album=album, duration=duration)       # Adaugare melodie in BD

        self.load_library_songs()                           # Actualizare lista melodii


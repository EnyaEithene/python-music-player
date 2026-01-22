# ---------- IMPORTURI ----------
import os
import shutil
from pathlib import Path
from tkinter import ttk, Listbox, DoubleVar, StringVar, Toplevel, END, filedialog
import pygame
from PIL import Image, ImageTk
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
import io
from tinytag import TinyTag
from db import database as db
from gui.rightclick_menu import setup_library_menu

# ---------- DIRECTOR MELODII ----------
SONG_DIR = os.path.join(os.path.dirname(__file__), "..", "songs")
os.makedirs(SONG_DIR, exist_ok=True)

# ---------- CLASA PLAYER GUI ----------
class PlayerGUI:
    def __init__(self, parent, app):
        # Fereastra principală și frame-ul de melodii
        self.app = app
        self.frame = ttk.LabelFrame(parent, text="Songs")
        self.frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        # Lista melodii
        self.listbox = Listbox(self.frame, height=10)
        self.listbox.pack(fill="both", expand=True, padx=5, pady=5)

        
        # ---------- Afisare melodie redata + cover art ----------
        self.song_frame = ttk.Frame(self.frame)
        self.song_frame.pack(fill="x", pady=5)

        # Cover art stanga
        self.cover_label = ttk.Label(self.song_frame)
        self.cover_label.pack(side="left", padx=5)

        # Frame pentru titlu si timp
        self.info_frame = ttk.Frame(self.song_frame)
        self.info_frame.pack(side="left", fill="x", expand=True)

        # Titlu melodie
        self.song_title_var = StringVar()
        self.song_title_var.set("No song playing")
        self.song_title_label = ttk.Label(self.info_frame, textvariable=self.song_title_var, anchor="center", font=("TkDefaultFont", 10, "bold"))
        self.song_title_label.pack(fill="x")

        # Timp melodie
        self.time_var = StringVar()
        self.time_var.set("00:00 / 00:00")
        self.time_label = ttk.Label(self.info_frame, textvariable=self.time_var, anchor="center")
        self.time_label.pack(fill="x")


        # Afisare timp redare
        self.time_var = StringVar()
        self.time_var.set("00:00 / 00:00")
        self.time_label = ttk.Label(self.frame, textvariable=self.time_var)
        self.time_label.pack(pady=(0,5))

        # Bara de progres
        self.progress_var = DoubleVar(value=0)
        self.progress = ttk.Scale(
            self.frame, from_=0, to=100, variable=self.progress_var,
            orient="horizontal", command=self.seek_song
        )
        self.progress.pack(fill="x", pady=(5,5))

        # Butoane control
        self.add_to_playlist_btn = ttk.Button(self.frame, text="Add to Playlist", command=self.add_song_to_playlist)
        self.play_btn = ttk.Button(self.frame, text="Play/Pause", command=self.toggle_play)
        self.stop_btn = ttk.Button(self.frame, text="Stop", command=self.stop_song)
        self.add_to_playlist_btn.pack(side="right", padx=10)
        self.play_btn.pack(side="left", padx=10)
        self.stop_btn.pack(side="left", padx=10)

        # Meniu repetare melodii
        self.repeat_var = StringVar(value="No Repeat")
        self.repeat_menu = ttk.OptionMenu(
            self.frame, self.repeat_var, "No Repeat",
            "No Repeat", "Repeat Playlist", "Repeat Song"
        )
        self.repeat_menu.pack(side="right", padx=10)

        # Initializare Pygame Mixer
        pygame.mixer.init()

        # Variabile stare player
        self.current_song = None
        self.current_index = None
        self.playing = False
        self.paused = False
        self.song_length = 0
        self.current_pos = 0
        self.update_job = None
        self.seeking = False

        # Încarcare melodii din biblioteca BD
        self.load_library_songs()

        
        # Right-click menu
        self.current_playlist_id = None
        setup_library_menu(
            self.listbox,
            lambda: self.songs,
            db,
            self.load_library_songs,                   # reload func
            self.add_song_to_playlist,                 # funcția de "Add to Playlist"
            delete_from_playlist_func=db.delete_song_from_playlist,   # funcția de ștergere din playlist
            playlist_id_getter=lambda: self.current_playlist_id      # returnează playlist-ul selectat, sau None dacă e librăria
        )

    # ---------- ÎNCĂRCARE MELODII ----------
    def load_library_songs(self):
        self.current_playlist_id = None
        self.listbox.delete(0, END)
        self.songs = db.get_songs()  # preia toate melodiile din BD

        valid_songs = []

        for s in self.songs:
            file_path = os.path.join(SONG_DIR, s["filename"])
            if os.path.exists(file_path):
                self.listbox.insert(END, s["title"] or s["filename"])
                valid_songs.append(s)
            else:
                # Lipsește fișierul → adaugă în history
                db.add_history(
                    entity_type="song",
                    entity_id=s["id"],
                    action="song_deleted"
                )

        # Înlocuiește lista originală cu cea filtrată
        self.songs = valid_songs

    def load_songs_for_playlist(self, playlist_id):
        self.current_playlist_id = playlist_id
        self.listbox.delete(0, END)
        songs = db.get_songs_in_playlist(playlist_id)
        valid_songs = []

        for song in songs:
            file_path = os.path.join(SONG_DIR, song["filename"])
            if os.path.exists(file_path):
                self.listbox.insert(END, song["title"] or song["filename"])
                valid_songs.append(song)
            else:
                # Melodie lipsă → marchează în istoric
                db.add_history(
                    entity_type="song",
                    entity_id=song["id"],
                    action="song_deleted"
                )
                # Stergere melodia din playlist
                db.delete_song_from_playlist(playlist_id, song["id"])

        self.songs = valid_songs

    # ---------- STOP ----------
    def stop_song(self):
        pygame.mixer.music.stop()
        self.playing = False
        self.paused = False
        self.current_song = None
        self.current_index = None
        self.song_length = 0
        self.current_pos = 0
        self.progress_var.set(0)
        if self.update_job:
            self.frame.after_cancel(self.update_job)
            self.update_job = None

    # ---------- PLAY / PAUSE ----------
    def toggle_play(self):
        sel = self.listbox.curselection()
        index = sel[0] if sel else None

        # Dacă nu e selectată nicio melodie și nu e nimic în redare
        if index is None and self.current_song is None:
            return  # nu avem ce reda

        # Dacă e selectată o melodie în listbox
        if index is not None:
            song = self.songs[index]
            song_path = os.path.join(SONG_DIR, song["filename"])

            # Dacă e o melodie diferită de cea curentă → schimbăm melodia
            if self.current_song != song_path:
                if self.playing:
                    pygame.mixer.music.stop()

                self.current_song = song_path
                self.current_index = index

                # Afisare titlu + cover art
                tag = TinyTag.get(self.current_song)
                self.song_length = tag.duration or 0
                self.current_pos = 0
                self.progress_var.set(0)
                self.progress.config(to=self.song_length)

                self.song_title_var.set(tag.title or Path(self.current_song).stem)
                self.load_cover_from_mp3(self.current_song)

                # Redare
                pygame.mixer.music.load(self.current_song)
                pygame.mixer.music.play()

                self.playing = True
                self.paused = False
                self.update_progress()
                return

        # Dacă ajungem aici → Play/Pause pe melodia curentă
        if self.playing and not self.paused:
            pygame.mixer.music.pause()
            self.paused = True
            self.playing = False
        elif self.paused:
            pygame.mixer.music.unpause()
            self.paused = False
            self.playing = True
            self.update_progress()

    # ---------- REDARE URMĂTOARE ----------
    def play_next_song(self):
        repeat_option = self.repeat_var.get()

        # Repeat song
        if repeat_option == "Repeat Song" and self.current_song:
            pygame.mixer.music.stop()
            pygame.mixer.music.play()
            self.current_pos = 0
            self.progress_var.set(0)
            self.playing = True
            self.paused = False
            self.update_progress()
            return

        # Redare următoare melodie
        if self.current_index is not None and self.current_index + 1 < len(self.songs):
            self.current_index += 1
            next_song = self.songs[self.current_index]
            self.current_song = os.path.join(SONG_DIR, next_song["filename"])

            # Afisare titlu + cover art
            tag = TinyTag.get(self.current_song)
            self.song_length = tag.duration or 0

            # Titlu melodie
            self.song_title_var.set(tag.title or Path(self.current_song).stem)

            # Cover art
            self.load_cover_from_mp3(self.current_song)

            # Schimbare melodie redata
            pygame.mixer.music.stop()
            pygame.mixer.music.load(self.current_song)
            pygame.mixer.music.play()

            tag = TinyTag.get(self.current_song)
            self.song_length = tag.duration or 0
            self.current_pos = 0
            self.progress_var.set(0)
            self.progress.config(to=self.song_length)

            self.playing = True
            self.paused = False
            self.update_progress()
        else:
            # Ultima melodie
            if repeat_option == "Repeat Playlist":
                self.current_index = 0
                first_song = self.songs[self.current_index]
                self.current_song = os.path.join(SONG_DIR, first_song["filename"])

                pygame.mixer.music.stop()
                pygame.mixer.music.load(self.current_song)
                pygame.mixer.music.play()

                tag = TinyTag.get(self.current_song)
                self.song_length = tag.duration or 0
                self.current_pos = 0
                self.progress_var.set(0)
                self.progress.config(to=self.song_length)

                self.playing = True
                self.paused = False
                self.update_progress()
            else:
                # No repeat → reset complet
                self.stop_song()

    # ---------- PRELUARE IMAGINE DIN FISIER MP3 ----------
    def load_cover_from_mp3(self, song_path):
        """Încarcă cover art-ul embedded în MP3 (ID3)"""
        try:
            audio = MP3(song_path, ID3=ID3)
            apic_tags = [tag for tag in audio.tags.values() if isinstance(tag, APIC)]
            if apic_tags:
                apic = apic_tags[0]  # folosim primul cover găsit
                image_data = io.BytesIO(apic.data)
                img = Image.open(image_data)
                img = img.resize((150, 150))  # dimensiune dorită
                self.cover_img = ImageTk.PhotoImage(img)
                self.cover_label.config(image=self.cover_img)
            else:
                self.cover_label.config(image="")
        except Exception as e:
            print("No cover found or error:", e)
            self.cover_label.config(image="")

    # ---------- ACTUALIZARE BARA DE PROGRES ----------
    def update_progress(self):
        if self.current_song and self.playing and not self.seeking:
            pos = pygame.mixer.music.get_pos()
            pos_s = max(pos / 1000, 0) + self.current_pos
            pos_s = min(pos_s, self.song_length)
            self.progress_var.set(pos_s)

            # Update timp curent / durata
            cur_min, cur_sec = divmod(int(pos_s), 60)
            tot_min, tot_sec = divmod(int(self.song_length), 60)
            self.time_var.set(f"{cur_min:02}:{cur_sec:02} / {tot_min:02}:{tot_sec:02}")

            if pos_s >= self.song_length - 0.2:
                self.play_next_song()
                return

        self.update_job = self.frame.after(200, self.update_progress)

    # ---------- SEEK ----------
    def seek_song(self, value):
        if self.current_song and self.song_length > 0:
            self.seeking = True
            pygame.mixer.music.pause()

            new_pos = float(value)
            pygame.mixer.music.play(start=new_pos)

            self.current_pos = new_pos
            self.progress_var.set(new_pos)
            self.seeking = False

            if not self.paused:
                pygame.mixer.music.unpause()

    # ---------- ADD TO PLAYLIST ----------
    def add_song_to_playlist(self, song_id=None):
        sel = self.listbox.curselection()
        if not sel: return
        song = self.songs[sel[0]]
        song_id = song["id"]
        playlists = db.get_playlists()
        if not playlists: return

        win = Toplevel(self.frame)
        win.title("Add to Playlist")
        win.geometry("250x300")
        win.transient(self.frame)
        win.grab_set()

        ttk.Label(win, text="Choose playlist:").pack(pady=5)
        lb = Listbox(win)
        lb.pack(fill="both", expand=True, padx=10, pady=5)

        for pl in playlists:
            lb.insert(END, pl["name"])

        def confirm():
            sel = lb.curselection()
            if not sel: return
            playlist = playlists[sel[0]]
            db.add_song_to_playlist(playlist["id"], song_id)
            win.destroy()
            self.app.playlists.load_playlists()

        btn_frame = ttk.Frame(win)
        btn_frame.pack(fill="x", pady=10)
        ttk.Button(btn_frame, text="Add", command=confirm).pack(side="left", expand=True, padx=10)
        ttk.Button(btn_frame, text="Cancel", command=win.destroy).pack(side="right", expand=True, padx=10)

    # ---------- ADD SONGS TO LIBRARY ----------
    def add_songs_to_library(self):
        filepaths = filedialog.askopenfilenames(
            title="Select Songs",
            filetypes=[("MP3 files", "*.mp3"), ("All files", "*.*")]
        )
        os.makedirs(SONG_DIR, exist_ok=True)
        for path in filepaths:
            # Numele fișierului și destinația în folder-ul songs
            filename = os.path.basename(path)
            dest = os.path.join(SONG_DIR, filename)

            # Copiere fișier în songs dacă nu există deja
            if not os.path.exists(dest):
                shutil.copy(path, dest)

            # Preluare metadata
            tag = TinyTag.get(dest)  # ⚠ folosim acum fișierul din songs
            title = tag.title or filename
            artist = tag.artist or ""
            album = tag.album or ""
            duration = tag.duration or 0

            # Salvare în BD folosind **numele din songs**, nu calea originală
            db.add_song(filename, title=title, artist=artist, album=album, duration=duration)

        self.load_library_songs()


import tkinter as tk
from tkinter import ttk
from tkinter import Menu, messagebox, filedialog, Toplevel, Listbox
from pathlib import Path
from gui.player import PlayerGUI
from gui.playlist import PlaylistGUI
from gui.history import HistoryWindow
import db.database as db
from services.playlist_service import PlaylistService
from services.export_service import PlaylistExporter

class MusicApp:
    #--------------- Initializare clasa ---------------
    def __init__(self, root, exporter):
        self.root = root
        self.exporter = exporter
        self.root.title("Music Player")

        # Frame pentru continut
        self.content = root

        # Initializare componente
        self.playlists = PlaylistGUI(self.content, self)
        self.player = PlayerGUI(self.content, self)

        # Director cu melodii
        self.songs_dir = Path(__file__).resolve().parent.parent / "songs"
        self.playlist_service = PlaylistService(db.db, self.songs_dir)
        self.exporter = PlaylistExporter(self.playlist_service)
        
        # Bara meniuri
        self.root.option_add('*tearOff', False)
        self.root.tk.call('tk', 'windowingsystem')
        self.menu_bar = Menu(root)
        root.config(menu=self.menu_bar)

        # Meniu "File"
        file_menu = Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="Add Songs", command=self.player.add_songs_to_library)
        file_menu.add_command(label="Add Playlist", command=self.playlists.add_playlist)
        file_menu.add_separator()
        file_menu.add_command(label="Export Playlist", command=self.export_playlist)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=root.quit)
        self.menu_bar.add_cascade(label="File", menu=file_menu)

        # Meniu "Help"
        help_menu = Menu(self.menu_bar, tearoff=0)
        help_menu.add_command(label="View Modifications", command=self.show_modifications)
        help_menu.add_command(label="About", command=self.show_about)
        self.menu_bar.add_cascade(label="Help", menu=help_menu)
        
    #--------------- Adaugare melodie ---------------    
    def add_songs(self):
        filepaths = filedialog.askopenfilenames(
            title="Select Songs",
            filetypes=[("MP3 files", "*.mp3"), ("All files", "*.*")]
        )
        print("Selected files:", filepaths)

    #--------------- Exportare playlist ---------------
    def export_playlist(self):
        # Selectează playlist
        sel = self.playlists.listbox.curselection()
        if not sel:
            return
        index = sel[0]

        # Obține id-ul playlist-ului din DB
        playlists = db.get_playlists()
        playlist_id = playlists[index]["id"]
        playlist_name = playlists[index]["name"]

        # Alege locația de salvare ZIP
        file_path = filedialog.asksaveasfilename(
            defaultextension=".zip",
            filetypes=[("ZIP files", "*.zip")],
            initialfile=f"{playlist_name}.zip"
        )
        if not file_path:
            return

        # Export
        self.exporter.export_zip(playlist_id, playlist_name, Path(file_path))
        messagebox.showinfo("Export", f"Playlist '{playlist_name}' exported successfully!")

    #--------------- Redare melodie selectata ---------------
    def play_selected_song(self):
        selection = self.library_listbox.curselection()
        if not selection:
            return

        index = selection[0]
        song_path = self.library_songs[index]["filepath"]

        self.player.play_song(song_path)
    
    #--------------- Afisare modificari (history.py) ---------------
    def show_modifications(self):
        HistoryWindow(self.root)

    #--------------- Afisare detalii aplicatie ---------------
    def show_about(self):
        messagebox.showinfo("About", "Music Player v0.1 by Enya Donisan, gr. AID-1")

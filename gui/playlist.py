from tkinter import *
from tkinter import ttk
from tkinter import simpledialog
from tkinter import messagebox
import db.database as db

class PlaylistGUI:
    # Definire GUI pentru lista de playlist-uri
    def __init__(self, parent, app):
        self.app = app
        self.frame = ttk.LabelFrame(parent, text="Playlists")
        self.frame.pack(side="left", fill="y", padx=5, pady=5)

        self.listbox = Listbox(self.frame, height=10)
        self.listbox.pack(fill="both", expand=True, padx=5, pady=5)

        self.add_btn = ttk.Button(self.frame, text="Add", command=self.add_playlist)
        self.del_btn = ttk.Button(self.frame, text="Delete", command=self.delete_playlist)
        self.add_btn.pack(side="left", padx=5)
        self.del_btn.pack(side="left", padx=5)

        self.listbox.bind("<<ListboxSelect>>", self.on_playlist_select)

        self.load_playlists()
    
    # Actualizare lista playlist-uri
    def load_playlists(self):                       
        # Sterge lista acuala playlist-uri
        self.listbox.delete(0, END)
        
        # Preluare playlist-uri din BD
        playlists = db.get_playlists()
        
        # Afiseaza lista actuala
        for pl in playlists:
            self.listbox.insert(END, pl["name"]) 

    def on_playlist_select(self, event):
        # Get the selected playlist index
        selection = self.listbox.curselection()
        if not selection:
            return
        
        index = selection[0]
        playlists = db.get_playlists()
        playlist_id = playlists[index]["id"]

        # Tell the PlayerGUI to load songs for this playlist
        self.app.player.load_songs_for_playlist(playlist_id)

    def load_songs_for_playlist(self, playlist_id):
        self.listbox.delete(0, "end")
        songs = db.get_songs_in_playlist(playlist_id)
        for s in songs:
            display_name = f"{s['title']} - {s['artist']}" if s['artist'] else s['title']
            self.listbox.insert("end", display_name)

    # Adaugare playlist
    def add_playlist(self):
        # Cere nume playlist
        name = simpledialog.askstring(title="New Playlist", prompt="Enter playlist name:")
        
        # Adauga in BD daca a fost introdus nume
        if name:
            db.add_playlist(name)  
            self.load_playlists()        

    # Stergere playlist
    def delete_playlist(self):
        # Preluare playlist selectat
        selected = self.listbox.curselection()
        # Daca nu a fost selectat niciun playlist
        if not selected:
            return
        
        # Preluare date playlist
        index = selected[0]
        playlists = db.get_playlists()
        pl_id = playlists[index]["id"]
        pl_name = playlists[index]["name"]
        
        # Cere confirmare stergere
        confirm = messagebox.askyesno(
            title="Delete Playlist",
            message=f"Are you sure you want to delete '{pl_name}'?"
        )
        
        # Se sterge melodia daca se confirma
        if confirm:
            db.delete_playlist(pl_id)  # Delete from DB
            self.load_playlists()            # Refresh Listbox

    

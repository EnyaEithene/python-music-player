from tkinter import ttk, simpledialog, Listbox, messagebox
from tkinter import *
import db.database as db

class PlaylistGUI:
    #--------------- Initializare clasa ---------------
    def __init__(self, parent, app):
        # Sectiune fereastra playlist-uri
        self.app = app
        self.frame = ttk.LabelFrame(parent, text="Playlists")
        self.frame.pack(side="left", fill="y", padx=5, pady=5)
        
        # Lista playlist-uri
        self.listbox = Listbox(self.frame, height=10)
        self.listbox.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Butoane
        self.add_btn = ttk.Button(self.frame, text="Add", command=self.add_playlist)
        self.del_btn = ttk.Button(self.frame, text="Delete", command=self.delete_playlist)
        self.show_all_btn = ttk.Button(self.frame, text="All Songs", command=self.show_all_songs)
        self.add_btn.pack(side="left", padx=5)
        self.del_btn.pack(side="left", padx=5)
        self.show_all_btn.pack(fill="x", pady=(0,5))
        
        # Selectare playlist
        self.listbox.bind("<<ListboxSelect>>", self.on_playlist_select)

        # Preluare si afisare playlist-uri din BD
        self.load_playlists()
    
    #--------------- Actualizare lista playlist-uri --------------- 
    def load_playlists(self):                       
        self.listbox.delete(0, END)
        playlists = db.get_playlists()
        for pl in playlists:
            self.listbox.insert(END, pl["name"]) 

    #--------------- Selectare playlist ---------------
    def on_playlist_select(self, event):
        # Preluare index playlist
        selection = self.listbox.curselection()
        if not selection:
            return
        index = selection[0]
        playlists = db.get_playlists()
        playlist_id = playlists[index]["id"]

        # Afisare melodii ale playlist-ului selectat
        self.app.player.load_songs_for_playlist(playlist_id)

    #--------------- Afisare melodii din playlist selectat ---------------
    def load_songs_for_playlist(self, playlist_id):
        self.listbox.delete(0, "end")
        songs = db.get_songs_in_playlist(playlist_id)
        for s in songs:
            display_name = f"{s['title']} - {s['artist']}" if s['artist'] else s['title']
            self.listbox.insert("end", display_name)

    #--------------- Adaugare playlist ---------------
    def add_playlist(self):
        # Cere nume playlist
        name = simpledialog.askstring(title="New Playlist", prompt="Enter playlist name:")
        
        # Adauga in BD daca a fost introdus nume
        if name:
            db.add_playlist(name)  
            self.load_playlists()        

    #--------------- Stergere playlist ---------------
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
            db.delete_playlist(pl_id)
            self.load_playlists()       

    #--------------- Afisare melodii salvate in BD ---------------
    def show_all_songs(self):
        self.app.player.load_library_songs()

    #--------------- Preluare si afisare melodii din library ---------------
    def load_library_songs(self):
            self.song_list.delete(0, END)

            songs = db.get_all_songs()
            for s in songs:
                self.song_list.insert(END, f"{s[2]} - {s[3]}")  # title - artist

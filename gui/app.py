from tkinter import Tk
from tkinter import Menu, messagebox, filedialog
from gui.player import PlayerGUI
from gui.playlist import PlaylistGUI
import db.database

class MusicApp:
    # Definire fereastra aplicatie
    def __init__(self, root):
        self.root = root
        self.root.title("Music Player")

        # Frame pentru continut
        self.content = root

        # Initializare componente
        self.playlists = PlaylistGUI(self.content, self)
        self.player = PlayerGUI(self.content, self)
        
        # Bara meniuri
        self.root.option_add('*tearOff', False)
        self.root.tk.call('tk', 'windowingsystem')
        self.menu_bar = Menu(root)
        root.config(menu=self.menu_bar)

        # File menu
        file_menu = Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="Add Songs", command=self.player.add_songs_to_library)
        file_menu.add_command(label="Add Playlist", command=self.playlists.add_playlist)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=root.quit)
        self.menu_bar.add_cascade(label="File", menu=file_menu)

        # Help menu
        help_menu = Menu(self.menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        self.menu_bar.add_cascade(label="Help", menu=help_menu)

    def add_songs(self):
        filepaths = filedialog.askopenfilenames(
            title="Select Songs",
            filetypes=[("MP3 files", "*.mp3"), ("All files", "*.*")]
        )
        print("Selected files:", filepaths)

    def play_selected_song(self):
        selection = self.library_listbox.curselection()
        if not selection:
            return

        index = selection[0]
        song_path = self.library_songs[index]["filepath"]

        self.player.play_song(song_path)

    def show_about(self):
        messagebox.showinfo("About", "Music Player v1.0")

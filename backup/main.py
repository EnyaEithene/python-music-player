# ---------- IMPORTARI ----------
import sqlite3              # Baza de date
import tinytag              # Preluare metadata

from tkinter import *       # Interfata grafica
from tkinter import ttk


# ---------- INTERFATA ----------
# Fereastra aplicatie
root = Tk()                                     # initializare
root.title("Music Player")                      # denumire fereastra
root.columnconfigure(0, weight=1)               # redimensionare automata
root.rowconfigure(0, weight=1)


# Frame - Continut GUI
content = ttk.Frame(root, padding=(3,3,12,12))  # Initializare
# padding=(left,top,right,bottom)
content.columnconfigure(0, weight=1)            # Redimensionare automata       
content.columnconfigure(1, weight=3)            
content.columnconfigure(2, weight=3)            
content.columnconfigure(3, weight=3)            
content.columnconfigure(4, weight=1)            
content.rowconfigure(0, weight=1)               


# Widget - Lista playlist-uri
playlist_lf = ttk.LabelFrame(content, text="Playlists")     # Labelframe
playlist_list = Listbox(playlist_lf, height=10)             # Lista


playlist_list.columnconfigure(0, weight=1)                  # redimensionare
playlist_list.pack(fill="both", expand=True)                # adaugare in Labelframe

# - butoane playlist-uri
playlist_pane = ttk.PanedWindow(playlist_lf, orient=HORIZONTAL) # Pane butoane
playlist_add_btn = ttk.Button(playlist_pane, text="Add")      # Buton adaugare
playlist_del_btn = ttk.Button(playlist_pane, text="Delete")   # Buton stergere

playlist_pane.pack(fill="both", padx=5, pady=5)
playlist_pane.add(playlist_add_btn)                          # adaugare in Pane
playlist_pane.add(playlist_del_btn)


# Widget - Lista melodii
music_lf = ttk.LabelFrame(content, text="Songs")            # Labelframe
music_list = Listbox(music_lf, height=10)                    # Lista

music_list.columnconfigure(0, weight=1)                     # redimensionare
music_list.pack(fill="both", expand=True)                   # adaugare in Labelframe


# ----- ARANJARE ELEMENTE GUI -----
content.grid(column=0, row=0, sticky="nsew")
playlist_lf.grid(column=0, row=0, columnspan=1, rowspan=4, sticky="nsew", padx=5, pady=5)
music_lf.grid(column=1, row=0, columnspan=3, rowspan=4, sticky="nsew", padx=5, pady=5)


# ---------- RULARE ----------
root.mainloop()


import tkinter as tk
from tkinter import messagebox

def setup_library_menu(listbox, get_songs_func, db, reload_func, add_to_playlist_func, delete_from_playlist_func=None, playlist_id_getter=None):
    menu = tk.Menu(listbox, tearoff=0)
    menu.add_command(label="Add to Playlist", command=lambda: add_song_context(listbox, get_songs_func(), add_to_playlist_func))
    menu.add_command(label="Delete Song", command=lambda: delete_song_context(listbox, get_songs_func(), db, reload_func))
    listbox.bind("<Button-3>", lambda event: show_menu(event, listbox, menu))

def show_menu(event, widget, menu):
    try:
        index = widget.nearest(event.y)
        widget.selection_clear(0, tk.END)
        widget.selection_set(index)
    except Exception:
        return
    menu.tk_popup(event.x_root, event.y_root)

def add_song_context(listbox, songs, add_to_playlist_func):
    sel = listbox.curselection()
    if not sel:
        return
    index = sel[0]
    song = songs[index]
    add_to_playlist_func(song["id"])

def delete_song_context(listbox, songs, db, reload_func):
    sel = listbox.curselection()
    if not sel:
        return
    index = sel[0]
    song = songs[index]
    if messagebox.askyesno("Delete Song", f"Delete '{song['title']}'?"):
        db.delete_song(song["id"])
        reload_func()



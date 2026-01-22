# Importari
import tkinter as tk
from tkinter import ttk
from db import database as db  # your DB module

class HistoryWindow:
    # --------------- Initializare clasa ---------------
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)                               # Fereastra separata pentru tabel cu modificari
        self.window.title("Modifications History")

        self.history_table = ttk.Treeview(self.window)
        self.history_table['columns'] = ("Timestamp", "Entity", "Action", "Details")
        self.history_table.column("#0", width=0, stretch=tk.NO)
        for col in self.history_table['columns']:
            self.history_table.column(col, anchor=tk.W, width=100)
            self.history_table.heading(col, text=col, anchor=tk.W)
        self.history_table.pack(fill="both", expand=True, padx=10, pady=10)

        self.load_history()

    #---------------- Formatare istoric modificari ---------------
    def format_history_row(self, h):
        action = h["action"]

        if action == "created":
            return f"Playlist '{h['playlist_name']}' created"
        if action == "deleted":
            return f"Playlist '{h['playlist_name']}' deleted"
        if action == "song_added":
            return f"Added '{h['song_title']}' to '{h['playlist_name']}'"
        if action == "song_removed":
            return f"Removed '{h['song_title']}' from '{h['playlist_name']}'"
        if action == "song_deleted_playlist":
            return f"Deleted '{h['song_title']}' from playlist '{h['playlist_name']}'"

        return "Unknown event"

    #--------------- Preluare istoric din BD ---------------
    def load_history(self):
        self.history_table.delete(*self.history_table.get_children())       # Curatare tabel
        rows = db.get_history()

        for h in rows:
            location = h["playlist_name"] if h["playlist_name"] else "Library"
            song_title = h["song_title"] or ""

            if h["action"] == "created":        # Descriere coerenta a modificarii
                details = f"Playlist '{location}' created"
            elif h["action"] == "deleted":
                details = f"Playlist '{location}' deleted"
            elif h["action"] == "song_added":
                details = f"Added '{song_title}' to '{location}'"
            elif h["action"] == "song_removed":
                details = f"Removed '{song_title}' from '{location}'"
            elif h["action"] == "song_deleted":
                details = f"Deleted song '{song_title}' from Library"
            elif h["action"] == "song_deleted_playlist":
                details = f"Deleted '{song_title}' from playlist '{location}'"
            else:
                details = "Unknown event"
            
            self.history_table.insert(                                      # Inserare date in tabel
                "",
                "end",
                values=(
                    h["timestamp"],
                    h["entity_type"].capitalize(),
                    h["action"].replace("_", " ").capitalize(),
                    details
                )
            )
        self.auto_resize_columns()

    #--------------- Redimensionare a coloanelor pentru a se potrivi continutului ---------------
    def auto_resize_columns(self):
        for col in self.history_table['columns']:
            max_width = max(
                [len(str(self.history_table.set(item, col))) for item in self.history_table.get_children()] + [len(col)]
            )
            self.history_table.column(col, width=max_width*10)


from tkinter import Tk
from pathlib import Path
import sqlite3

from gui.app import MusicApp
from db.database import init_db
from services.playlist_service import PlaylistService
from services.export_service import PlaylistExporter

def main():
    root = Tk()

    # DB
    conn = sqlite3.connect("music.db")
    init_db()

    # Services
    playlist_service = PlaylistService(conn, Path("songs"))
    exporter = PlaylistExporter(playlist_service)

    # GUI (dependency injection)
    app = MusicApp(root, exporter)

    root.mainloop()

if __name__ == "__main__":
    main()


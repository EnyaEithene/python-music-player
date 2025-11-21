# ---------- IMPORTARI ----------
import sqlite3

# ---------- Baza de date ----------
db = sqlite3.connect("music.db")   # conectare la BD
db.row_factory = sqlite3.Row
cur = db.cursor()                  # cursor pentru acces BD

def init_db():

    # Creare tabel songs
    cur.execute("""
        CREATE TABLE IF NOT EXISTS songs(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            title VARCHAR(100) NOT NULL,
            artist VARCHAR(100),
            album VARCHAR(100),
            duration REAL,
            deleted INTEGER DEFAULT 0,
            date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            date_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")

    # Creare tabel playlists
    cur.execute("""
        CREATE TABLE IF NOT EXISTS playlists(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCGAR(100) NOT NULL,
            deleted INTEGER DEFAULT 0,
            date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            date_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")

    # Creare tabel playlist_songs
    cur.execute("""
        CREATE TABLE IF NOT EXISTS playlist_songs(
            id_playlist INTEGER NOT NULL,
            id_song INTEGER NOT NULL,
            deleted INTEGER DEFAULT 0,
            date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            date_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY(id_playlist, ID_song),
            FOREIGN KEY(id_playlist) REFERENCES playlists(id),
            FOREIGN KEY(id_song) REFERENCES songs(id)
        )""")
    db.commit()

# Verificare creere tabele
def list_tables():
    cur = db.cursor()
    return cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()

# Functii playlist-uri
def get_playlists():
    return cur.execute("SELECT * FROM playlists WHERE deleted=0").fetchall()

def add_playlist(name):
    cur.execute("INSERT INTO playlists (name) VALUES (?)", (name,))
    db.commit()

def delete_playlist(playlist_id):
    cur.execute("UPDATE playlists SET deleted=1 WHERE id=?", (playlist_id,))
    db.commit()

# Functii melodii
def get_songs():
    return cur.execute("SELECT * FROM songs WHERE deleted=0").fetchall()

def add_song(filename, title=None, artist=None, album=None, duration=None):
    cur.execute("""
        INSERT INTO songs (filename, title, artist, album, duration)
        VALUES (?, ?, ?, ?, ?)
    """, (filename, title or "", artist or "", album or "", duration or 0))
    db.commit()

def add_song_to_playlist(playlist_id, song_id):
    cur.execute(
        "INSERT OR IGNORE INTO playlist_songs (id_playlist, id_song) VALUES (?, ?)",
        (playlist_id, song_id)
    )
    db.commit()

def get_songs_in_playlist(playlist_id):
    return cur.execute(
        """
        SELECT s.*
        FROM songs s
        JOIN playlist_songs ps ON s.id = ps.id_song
        WHERE ps.id_playlist=? AND s.deleted=0
        """,
        (playlist_id,)
    ).fetchall()

def get_song_by_filename(filename):
    res = cur.execute(
        "SELECT * FROM songs WHERE filename=? AND deleted=0",
        (filename,)
    ).fetchone()
    return res

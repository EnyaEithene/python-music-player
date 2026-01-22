# ---------- IMPORTARI ----------
import sqlite3
from pathlib import Path

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
            name VARCHAR(100) NOT NULL,
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

    # Creare tabel history
    cur.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_type TEXT NOT NULL,   
            entity_id INTEGER,
            related_id INTEGER,
            playlist_id INTEGER,
            song_id INTEGER,
            action TEXT NOT NULL,        
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
    # entity_type = tabelul in care s-a facut modificarea (playlist/song/playlist_song)
    # action = added/deleted/song_added/song_removed
    db.commit()

# Verificare creere tabele
def list_tables():
    cur = db.cursor()
    return cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()

#--------------- PT. PLAYLIST-URI ---------------
# Preluare playlist-uri "nesterse"
def get_playlists():
    return cur.execute("SELECT * FROM playlists WHERE deleted=0").fetchall()

# Adaugare playlist
def add_playlist(name):
    cur.execute("INSERT INTO playlists (name) VALUES (?)", (name,))
    playlist_id = cur.lastrowid
    cur.execute("INSERT INTO history (entity_type, entity_id, action) VALUES ('playlist', ?, 'created')", (playlist_id,))
    db.commit()

# Stergere playlist
def delete_playlist(playlist_id):
    cur.execute("UPDATE playlists SET deleted=1, date_modified=CURRENT_TIMESTAMP WHERE id=?", (playlist_id,))
    cur.execute("INSERT INTO history (entity_type, entity_id, action) VALUES ('playlist', ?, 'deleted')", (playlist_id,))
    db.commit()

#--------------- PT. MELODII ---------------
# Preluare melodii
def get_songs():
    return cur.execute("SELECT * FROM songs WHERE deleted=0").fetchall()

# Adaugare melodie in librarie
def add_song(filename, title=None, artist=None, album=None, duration=None):
    cur.execute("INSERT INTO songs (filename, title, artist, album, duration) VALUES (?, ?, ?, ?, ?)", (filename, title or "", artist or "", album or "", duration or 0))
    song_id = cur.lastrowid
    cur.execute("INSERT INTO history (entity_type, entity_id, action) VALUES ('song', ?, 'song_added')", (song_id,))
    db.commit()

# Adaugare melodie la playlist
def add_song_to_playlist(playlist_id, song_id):
    cur.execute("INSERT OR IGNORE INTO playlist_songs (id_playlist, id_song) VALUES (?, ?)", (playlist_id, song_id))
    cur.execute("INSERT INTO history (entity_type, entity_id, related_id, action) VALUES ('playlist_song', ?, ?, 'song_added')", (song_id,playlist_id))
    db.commit()

# Preluare melodii din playlist selectat
def get_songs_in_playlist(playlist_id):
    return cur.execute(
        """
        SELECT s.*
        FROM songs s
        JOIN playlist_songs ps ON s.id = ps.id_song
        WHERE ps.id_playlist=? AND s.deleted=0 AND ps.deleted=0
        """,
        (playlist_id,)
    ).fetchall()

# Preluare melodie dupa nume fisier
def get_song_by_filename(filename):
    return cur.execute(
        "SELECT * FROM songs WHERE filename=? AND deleted=0",
        (filename,)
    ).fetchone()

# Stergere melodie
def delete_song(song_id):
    cur.execute("UPDATE songs SET deleted = 1, date_modified = CURRENT_TIMESTAMP WHERE id = ?", (song_id,))
    cur.execute("INSERT INTO history (entity_type, entity_id, action) VALUES ('song', ?, 'song_deleted')", (song_id,))
    db.commit()

# Stergere melodie din playlist
def delete_song_from_playlist(playlist_id, song_id):
    cur.execute(
        """
        UPDATE playlist_songs 
        SET deleted = 1, date_modified = datetime(current_timestamp, 'localtime')
        WHERE id_playlist = ? AND id_song = ?
        """,
        (playlist_id, song_id)
    )
    entity_ref = f"{playlist_id}:{song_id}"
    cur.execute("INSERT INTO history (entity_type, entity_id, related_id, action) VALUES ('playlist_song', ?, ?, 'song_deleted_playlist')", (song_id,playlist_id))
    db.commit()

#--------------- PT. ISTORIC ----------------
def get_history():
    return cur.execute("""
        SELECT
            h.entity_type,
            h.action,
            h.entity_id,
            h.related_id,
            h.timestamp,
            p.name AS playlist_name,
            s.title AS song_title
        FROM history h
        LEFT JOIN playlists p 
            ON h.related_id = p.id
        LEFT JOIN songs s 
            ON (h.entity_type = 'song' AND h.entity_id = s.id)
            OR (h.entity_type = 'playlist_song' AND h.entity_id = s.id)
        ORDER BY h.timestamp DESC
    """).fetchall()

def add_history(entity_type, entity_id, action):
    if entity_type == "library":
        return
    cur.execute(
        "INSERT INTO history (entity_type, entity_id, action) VALUES (?, ?, ?)",
        (entity_type, entity_id, action)
    )
    db.commit()

#--------------- PT. EXPORTARE ----------------
def get_playlist_filenames(db_path: Path, playlist_id: int) -> list[str]:
    cur.execute("""
        SELECT s.filename
        FROM songs s
        JOIN playlist_songs ps ON ps.id_song = s.id
        WHERE ps.id_playlist = ?
          AND s.deleted = 0
          AND ps.deleted = 0
        ORDER BY ps.date_added
    """, (playlist_id,))

    filenames = [row[0] for row in cur.fetchall()]
    return filenames

# ---------- IMPORTARI ----------
import sqlite3

# ---------- Baza de date ----------
con = sqlite3.connect("music.db")   # conectare la BD
cur = con.cursor()                         # cursor pentru acces BD

# Creare tabel songs
# cur.execute("""
#     CREATE TABLE songs(
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         filename TEXT NOT NULL,
#         title VARCHAR(100) NOT NULL,
#         artist VARCHAR(100),
#         album VARCHAR(100),
#         duration REAL,
#         deleted INTEGER DEFAULT 0,
#         date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#         date_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#     )""")

# Creare tabel playlists
# cur.execute("""
#     CREATE TABLE playlists(
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         name VARCGAR(100) NOT NULL,
#         deleted INTEGER DEFAULT 0,
#         date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#         date_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#     )""")

# Creare tabel playlist_songs
# cur.execute("""
#     CREATE TABLE playlist_songs(
#         id_playlist INTEGER NOT NULL,
#         id_song INTEGER NOT NULL,
#         deleted INTEGER DEFAULT 0,
#         date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#         date_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#         PRIMARY KEY(id_playlist, ID_song),
#         FOREIGN KEY(id_playlist) REFERENCES playlists(id),
#         FOREIGN KEY(id_song) REFERENCES songs(id)
#     )""")

# Verificare creere
res = cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
print(res.fetchall())

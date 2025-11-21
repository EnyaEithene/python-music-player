from db.database import db

def get_all_playlists():
    cur = db.cursor()
    cur.execute("SELECT name FROM playlists WHERE deleted = 0")
    return [row[0] for row in cur.fetchall()]


def add_playlist(name):
    cur = db.cursor()
    cur.execute("INSERT INTO playlists (name) VALUES (?)", (name,))
    db.commit()


def delete_playlist(name):
    cur = db.cursor()
    cur.execute("UPDATE playlists SET deleted = 1 WHERE name = ?", (name,))
    db.commit()


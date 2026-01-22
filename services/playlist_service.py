from pathlib import Path
from db.database import get_playlist_filenames

class PlaylistService:
    def __init__(self, conn, songs_dir: Path):
        self.conn = conn
        self.songs_dir = songs_dir

    def get_song_paths(self, playlist_id: int) -> list[Path]:
        filenames = get_playlist_filenames(self.conn, playlist_id)
        return [self.songs_dir / name for name in filenames]


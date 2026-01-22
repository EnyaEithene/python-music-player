import zipfile
import shutil
from pathlib import Path

class PlaylistExporter:
    def __init__(self, playlist_service):
        self.playlist_service = playlist_service

    def export_zip(self, playlist_id: int, name: str, output_zip: Path):
        temp_dir = output_zip.parent / name
        temp_dir.mkdir(parents=True, exist_ok=True)

        songs = self.playlist_service.get_song_paths(playlist_id)

        # M3U
        m3u = temp_dir / f"{name}.m3u"
        with m3u.open("w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            for song in songs:
                f.write(f"{song.name}\n")

        # Copiere fișiere
        for song in songs:
            shutil.copy2(song, temp_dir / song.name)

        # ZIP
        with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file in temp_dir.iterdir():
                zipf.write(file, arcname=file.name)

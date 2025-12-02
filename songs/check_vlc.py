import vlc
import time

# Path to your song file
filepath = "./songs/03 Madame (feat. Alec Chambers).mp3"

# Create VLC player
player = vlc.MediaPlayer(filepath)
player.play()

# Give VLC a moment to load the media
time.sleep(0.5)

# Loop to print current position and total length
try:
    while True:
        length_ms = player.get_length()      # total duration in ms
        pos_ms = player.get_time()           # current position in ms

        # Convert to seconds for readability
        length_s = length_ms / 1000 if length_ms > 0 else 0
        pos_s = pos_ms / 1000 if pos_ms > 0 else 0

        print(f"Position: {pos_s:.2f}s / {length_s:.2f}s", end="\r")

        # Stop if song ended
        if length_ms > 0 and pos_ms >= length_ms:
            print("\nSong ended.")
            break

        time.sleep(0.2)
except KeyboardInterrupt:
    print("\nStopped by user.")
    player.stop()

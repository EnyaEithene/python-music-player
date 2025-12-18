from tkinter import Tk
from gui.app import MusicApp
from db import database as db

root = Tk()
db.init_db()
app = MusicApp(root)
root.mainloop()

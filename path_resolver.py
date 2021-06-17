import sys
import os

# resolve path for .exe packaging
def resolve(path):
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, path)
    else:
        return path
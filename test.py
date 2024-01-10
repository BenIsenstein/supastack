import os
from main import main as create
from destroy import main as destroy

if __name__ == "__main__":
    create()
    os.chdir("../..")
    destroy()

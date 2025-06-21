import os
# Make sure the current working directory is the directory of this script
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from app import VnestAutopilot

if __name__ == "__main__":
    app = VnestAutopilot()
    app.run()
import os
import time
import random
import string
import subprocess
from datetime import datetime

# Set your repo path
REPO_PATH = subprocess.run("pwd", capture_output=True, text=True).stdout.strip()
BRANCH = "dev"

def generate_random_text():
    """Generate a random string of length 20."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=20))

def create_text_file():
    """Create a new text file with random content."""
    filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    filepath = os.path.join(REPO_PATH, filename)

    with open(filepath, "w") as f:
        f.write(generate_random_text())

    return filename

def git_commit_and_push(filename):
    """Commit and push file to GitHub dev branch."""
    os.chdir(REPO_PATH)
    
    subprocess.run(["git", "checkout", BRANCH], check=True)
    subprocess.run(["git", "add", filename], check=True)
    subprocess.run(["git", "commit", "-m", f"Auto backup: {filename}"], check=True)
    subprocess.run(["git", "push", "origin", BRANCH], check=True)

if __name__ == "__main__":
    while True:
        filename = create_text_file()
        print(f"Created {filename}")

        try:
            git_commit_and_push(filename)
            print(f"Pushed {filename} to {BRANCH}")
        except Exception as e:
            print("Error pushing to GitHub:", e)

        time.sleep(120)  # wait 2 minutes
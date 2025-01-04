import os
import subprocess
import sys
import time

import git


def update_self():
    try:
        print("Pulling latest changes from GitHub...")

        # Run git pull to fetch latest changes
        result = subprocess.run(['git', 'pull'], capture_output=True, text=True)

        if "Already up to date" in result.stdout:
            print("No updates found.")
            return

        print(result.stdout)
        print("Update successful. Restarting bot...")

        # Restart the bot by relaunching the current script
        time.sleep(1)
        python = sys.executable
        os.execl(python, python, *sys.argv)

    except Exception as e:
        print(f"Failed to update: {str(e)}")



def _restart_program():
    """Gracefully restart the current Python program."""
    print("Restarting program...")
    os.execv(sys.executable, [sys.executable] + sys.argv)

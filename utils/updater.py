import os
import sys

def restart_program():
    """Gracefully restart the current Python program."""
    print("Restarting program...")
    os.execv(sys.executable, [sys.executable] + sys.argv)

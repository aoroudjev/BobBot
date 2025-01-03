import os
import sys

import git


def update_self(repo_path):
    """Pulls latest commit from repo."""
    repo = git.Repo(repo_path)
    repo.remotes.origin.pull()
    print("Updated... restarting")
    _restart_program()


def _restart_program():
    """Gracefully restart the current Python program."""
    print("Restarting program...")
    os.execv(sys.executable, [sys.executable] + sys.argv)

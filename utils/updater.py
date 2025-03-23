import os
import sys
import asyncio

TRIGGER_FILE = "update.trigger"


def restart_program():
    """Gracefully restart the current Python program."""
    print("Restarting program...")
    os.execv(sys.executable, [sys.executable] + sys.argv)

async def update_loop():
    """Watch for trigger and restart"""
    while True:
        if os.path.exists(TRIGGER_FILE):
            print("Update trigger detected... Restarting")
            os.remove(TRIGGER_FILE)
            restart_program()
        await asyncio.sleep(10)

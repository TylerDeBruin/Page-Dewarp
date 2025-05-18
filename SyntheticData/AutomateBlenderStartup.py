import subprocess
import time
import os

# === CONFIG ===
BLENDER_EXECUTABLE = r"D:\SteamLibrary\steamapps\common\Blender\blender.exe"
BLENDER_SCRIPT = r"G:\Public\Page-Dewarp\SyntheticData\CreateEnvironment.py"

WAIT_BEFORE_RESTART = 2  # seconds between restarts
MAX_RETRIES = None       # or set to 10, for example

def run_blender_with_console():
    """Launch Blender visibly (not background), returns process object."""
    try:
        return subprocess.Popen(
            [BLENDER_EXECUTABLE, "--python", BLENDER_SCRIPT],
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
    except Exception as e:
        print(f"Failed to launch Blender: {e}")
        return None

def watch_blender():
    retries = 0
    while MAX_RETRIES is None or retries < MAX_RETRIES:
        print(f"\n▶️ Starting Blender... Attempt #{retries + 1}")
        proc = run_blender_with_console()

        if proc is None:
            print("❌ Could not start Blender.")
            retries += 1
            time.sleep(WAIT_BEFORE_RESTART)
            continue

        proc.wait()  # Wait for Blender to exit

        if proc.returncode == 0:
            print("✅ Blender completed successfully.")
            break
        else:
            print(f"❌ Blender crashed (exit code {proc.returncode}). Restarting in {WAIT_BEFORE_RESTART}s...")
            retries += 1
            time.sleep(WAIT_BEFORE_RESTART)

    if MAX_RETRIES is not None and retries >= MAX_RETRIES:
        print("⛔ Max retries reached. Giving up.")

if __name__ == "__main__":
    watch_blender()
import subprocess
import psutil
import time

OLLAMA_MODEL = "llama3.2-vision:11b"

def is_ollama_running():
    """Check if an Ollama 'run' process is active."""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if 'ollama' in proc.info['name'].lower():
                cmdline = ' '.join(proc.info['cmdline']).lower()
                if 'run' in cmdline and OLLAMA_MODEL.lower() in cmdline:
                    return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False

def start_ollama_model():
    """Start Ollama model in a new cmd window."""
    subprocess.Popen(
        ['cmd.exe', '/k', f'ollama run {OLLAMA_MODEL}'],
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )
    print(f"🟢 Started ollama run {OLLAMA_MODEL}")

def wait_for_ollama_startup(timeout=60):
    """Wait until the model is running, or timeout."""
    print(f"⏳ Waiting for Ollama {OLLAMA_MODEL} to start...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        if is_ollama_running():
            print(f"✅ Ollama {OLLAMA_MODEL} is now running!")
            return True
        time.sleep(2)  # Wait a bit before checking again
    print(f"❌ Ollama did not start within {timeout} seconds.")
    return False

def ensure_ollama_running():
    """Full check: if not running, start and wait; if stuck, restart."""
    if not is_ollama_running():
        print("⚠️ Ollama model not detected. Starting it...")
        start_ollama_model()
        success = wait_for_ollama_startup()

        if not success:
            print("🔁 Attempting to restart Ollama...")
            # Kill any remaining ollama processes
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if 'ollama' in proc.info['name'].lower():
                        proc.kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            time.sleep(2)
            start_ollama_model()
            wait_for_ollama_startup()
    else:
        print("✅ Ollama model already running!")

if __name__ == "__main__":
    ensure_ollama_running()

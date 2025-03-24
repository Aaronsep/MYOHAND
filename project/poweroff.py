# poweroff.py
import subprocess

def power_off_myo():
    try:
        result = subprocess.run(
            ["python", "project\suboff.py"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode != 0:
            print("STDERR:", result.stderr)  # TEMPORAL
        return result.returncode == 0
    except Exception as e:
        return False

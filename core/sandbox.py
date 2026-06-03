import subprocess
import tempfile
import os

def run_code_sandboxed(code, timeout=30):
    """
    Run Python code inside a maximally-hardened, throwaway Docker container.
    Returns the captured stdout/stderr. Nothing touches the host; no network.
    """
    # Write the code to a temp file we'll mount read-only into the container.
    with tempfile.TemporaryDirectory() as tmpdir:
        code_path = os.path.join(tmpdir, "script.py")
        with open(code_path, "w") as f:
            f.write(code)

        # Convert Windows path to Docker-friendly mount source.
        mount_src = code_path.replace("\\", "/")

        docker_cmd = [
            "docker", "run",
            "--rm",                          # auto-delete container when done
            "--network", "none",             # NO network access at all
            "--memory", "256m",              # cap RAM (can't exhaust your system)
            "--cpus", "1",                   # cap CPU
            "--pids-limit", "64",            # cap processes (no fork bombs)
            "--read-only",                   # container filesystem is read-only
            "--cap-drop", "ALL",             # drop ALL Linux capabilities
            "--security-opt", "no-new-privileges",  # no privilege escalation
            "--user", "65534:65534",         # run as 'nobody', not root
            "-v", f"{mount_src}:/script.py:ro",     # mount code read-only
            "python:3.12-slim",              # minimal Python image
            "python", "/script.py"
        ]

        try:
            result = subprocess.run(
                docker_cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            output = result.stdout
            if result.stderr:
                output += "\n[stderr]\n" + result.stderr
            return output.strip() if output.strip() else "(no output)"
        except subprocess.TimeoutExpired:
            return f"(execution timed out after {timeout}s)"
        except Exception as e:
            return f"(sandbox error: {e})"


# Self-test when run directly
if __name__ == "__main__":
    test_code = """
import hashlib
print(hashlib.sha256('butler test'.encode('utf-8')).hexdigest())
"""
    print("=== SANDBOX OUTPUT ===")
    print(run_code_sandboxed(test_code))
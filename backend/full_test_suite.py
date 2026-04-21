import subprocess
import sys

def run(command):
    result = subprocess.run(command)
    if result.returncode != 0:
        sys.exit(result.returncode)

if __name__ == "__main__":
    run(["pytest", "-v"])
    run(["behave"])
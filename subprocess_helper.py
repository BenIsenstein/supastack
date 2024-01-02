import subprocess
import sys
import time

def run_command(cmd, **kwargs):
    process = subprocess.Popen(cmd, shell=True, text=True, **kwargs)
    stdout, stderr = process.communicate()

    if process.returncode != 0:
        sys.exit(process.returncode)

    return (stdout, stderr)

def run_command_with_retry(cmd, retries=10, **kwargs):
    try_count = 0

    while True:
        time.sleep(try_count * 2)

        process = subprocess.Popen(cmd, shell=True, text=True, **kwargs)
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            if try_count > retries:
                sys.exit(process.returncode)
            else:
                try_count += 1
                continue
        break

    return (stdout, stderr)

"""
Manual test to see if MCP server starts and what errors it shows
"""
import subprocess
import os
import sys

print("Testing MCP server startup manually...")
print(f"Python: {sys.executable}")
print(f"Project: {os.getcwd()}")

env = os.environ.copy()
env["DBT_PROJECT_DIR"] = r"C:\Rif\dbt_poc\metricflow_poc"
env["DBT_PROFILES_DIR"] = r"C:\Rif\dbt_poc\metricflow_poc"
env["DBT_PATH"] = r"C:\Users\Timer\.local\bin\dbt.exe"

print("\nStarting MCP server (will show output for 10 seconds)...")
print("="*60)

try:
    process = subprocess.Popen(
        [sys.executable, "-m", "dbt_mcp.main"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    # Read output for 10 seconds
    import time
    start_time = time.time()
    while time.time() - start_time < 10:
        if process.poll() is not None:
            # Process ended
            output = process.stdout.read()
            print(output)
            print(f"\nProcess exited with code: {process.returncode}")
            break
        time.sleep(0.5)
    else:
        # Timeout - process still running
        print("\nProcess is still running (this is normal - MCP server runs continuously)")
        print("Killing process...")
        process.terminate()
        process.wait(timeout=5)
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()


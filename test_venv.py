#!/usr/bin/env python3
"""Test with direct venv python"""
import json
import subprocess

initialize_request = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "test", "version": "1.0.0"}
    }
}

proc = subprocess.Popen(
    ["/Users/xhldemac/BlindAuditor/blind-auditor/.venv/bin/python", "-m", "src.main"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    cwd="/Users/xhldemac/BlindAuditor/blind-auditor",
    env={
        "PYTHONPATH": "/Users/xhldemac/BlindAuditor/blind-auditor",
        "PYTHONUNBUFFERED": "1"
    }
)

proc.stdin.write(json.dumps(initialize_request) + "\n")
proc.stdin.flush()

import time
time.sleep(2)

# Read stderr
stderr_output = proc.stderr.read()
if stderr_output:
    print(f"STDERR: {stderr_output}")

stdout_line = proc.stdout.readline()
if stdout_line:
    response = json.loads(stdout_line)
    print(f"✅ Direct venv python works!")
    print(f"Server: {response['result']['serverInfo']['name']}")
else:
    print("❌ No response from direct venv python")
    
proc.terminate()

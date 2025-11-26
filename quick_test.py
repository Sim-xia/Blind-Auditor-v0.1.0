#!/usr/bin/env python3
"""Quick test of MCP server"""
import json
import subprocess
import sys

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
    ["uv", "run", "python", "-m", "src.main"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    cwd="/Users/xhldemac/BlindAuditor/blind-auditor"
)

proc.stdin.write(json.dumps(initialize_request) + "\n")
proc.stdin.flush()

import time
time.sleep(2)

stdout_line = proc.stdout.readline()
if stdout_line:
    response = json.loads(stdout_line)
    print("✅ Server initialized successfully!")
    print(f"Server: {response['result']['serverInfo']['name']}")
else:
    print("❌ No response")
    
proc.terminate()

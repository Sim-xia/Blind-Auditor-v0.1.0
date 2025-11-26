"""
Minimal debug version of Blind Auditor MCP Server
"""
import sys
from pathlib import Path

# Debug output to stderr
print("DEBUG: Starting main_debug.py", file=sys.stderr)

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

print("DEBUG: Importing FastMCP", file=sys.stderr)
from mcp.server.fastmcp import FastMCP

print("DEBUG: Importing state and rules", file=sys.stderr)
from state import SessionState
from rules import RulesLoader

# Initialize the MCP server
print("DEBUG: Creating FastMCP instance", file=sys.stderr)
mcp = FastMCP("Blind Auditor")

# Initialize global state
print("DEBUG: Initializing session state", file=sys.stderr)
session = SessionState()

# Initialize rules loader with proper path
print("DEBUG: Loading rules", file=sys.stderr)
rules_path = Path(__file__).parent.parent / "rules.json"
rules_loader = RulesLoader(str(rules_path))

# Load rules at module level (before defining tools)
try:
    rules_loader.load()
    print(f"DEBUG: Rules loaded successfully from {rules_path}", file=sys.stderr)
except Exception as e:
    print(f"DEBUG: Failed to load rules.json: {e}", file=sys.stderr)


@mcp.tool()
def submit_draft(code: str, language: str = "python") -> str:
    """Submit a code draft for audit."""
    print(f"DEBUG: submit_draft called with code length={len(code)}", file=sys.stderr)
    session.current_code = code
    session.status = "AUDITING"
    
    max_retries = rules_loader.get_max_retries()
    
    if session.retry_count >= max_retries:
        session.status = "APPROVED"
        return f"⚠️ RETRY LIMIT REACHED\n\nCode:\n```{language}\n{code}\n```"
    
    rules_formatted = rules_loader.format_rules_for_prompt()
    
    return f"""🛑 **[SYSTEM INTERVENTION: CONTEXT ISOLATION MODE]**

**STOP GENERATING**. Do not output the code yet.

You are now entering the **Blind Audit Phase**.

**Rulebook:**
{rules_formatted}

**Candidate Code:**
```{language}
{code}
```

**Instructions:**
- Call `submit_audit_result` with your findings.
"""


@mcp.tool()
def submit_audit_result(passed: bool, issues: list[str], score: int = 0) -> str:
    """Submit the audit result."""
    print(f"DEBUG: submit_audit_result called: passed={passed}, score={score}", file=sys.stderr)
    
    session.audit_history.append({
        "passed": passed,
        "issues": issues,
        "score": score,
        "retry_count": session.retry_count
    })
    
    if passed:
        session.status = "APPROVED"
        return f"✅ AUDIT PASSED (Score: {score}/100)\n\n```\n{session.current_code}\n```"
    else:
        session.retry_count += 1
        session.status = "IDLE"
        issues_formatted = "\n".join([f"- {issue}" for issue in issues])
        return f"❌ AUDIT FAILED (Score: {score}/100)\n\n**Issues:**\n{issues_formatted}\n\nRetry count: {session.retry_count}/{rules_loader.get_max_retries()}"


@mcp.tool()
def reset_session() -> str:
    """Reset the current audit session."""
    print("DEBUG: reset_session called", file=sys.stderr)
    session.reset()
    return "✅ Session reset successfully."


if __name__ == "__main__":
    print("DEBUG: About to call mcp.run()", file=sys.stderr)
    sys.stderr.flush()
    mcp.run()
    print("DEBUG: mcp.run() completed (this shouldn't print)", file=sys.stderr)

"""
Blind Auditor MCP Server Entry Point

Run this server with: python -m src.main
or configure it in your MCP client.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from mcp.server.fastmcp import FastMCP
from state import SessionState
from rules import RulesLoader

# Initialize the MCP server
mcp = FastMCP("Blind Auditor")

# Initialize global state
session = SessionState()

# Initialize rules loader with proper path
rules_path = Path(__file__).parent.parent / "rules.json"
rules_loader = RulesLoader(str(rules_path))

# Load rules at module level (before defining tools)
try:
    rules_loader.load()
except Exception as e:
    import sys
    print(f"Warning: Failed to load rules.json: {e}", file=sys.stderr)
    # Continue with empty rules


@mcp.tool()
def submit_draft(code: str, language: str = "python") -> str:
    """
    Submit a code draft for audit. This triggers the blind audit process.
    
    Args:
        code: The complete code content to audit
        language: Programming language (e.g., python, typescript, javascript)
    
    Returns:
        System instruction to enter audit mode or release code if retry limit reached
    """
    # Store the code in session
    session.current_code = code
    session.status = "AUDITING"
    
    max_retries = rules_loader.get_max_retries()
    
    # Circuit breaker: if retry limit reached, force release
    if session.retry_count >= max_retries:
        session.status = "APPROVED"
        return f"""
⚠️ **[SYSTEM: RETRY LIMIT REACHED - FORCING RELEASE]**

Maximum retry attempts ({max_retries}) exceeded.
Releasing code with warning. Please review manually.

**Final Code:**
```{language}
{code}
```
"""
    
    # Otherwise, trigger audit mode
    rules_formatted = rules_loader.format_rules_for_prompt()
    
    return f"""
🛑 **[SYSTEM INTERVENTION: CONTEXT ISOLATION MODE]**

**STOP GENERATING**. Do not output the code yet.

You are now entering the **Blind Audit Phase**.
Forget that you wrote the code below. You are now an external **Code Auditor**.

**Your Task:**
1. Review the "Candidate Code" against the "Rulebook" provided below.
2. Do NOT rewrite the code yet. Just find errors.
3. Call the tool `submit_audit_result` with your findings.

**Rulebook:**
{rules_formatted}

**Candidate Code:**
```{language}
{code}
```

**Instructions:**
- Set `passed=True` if the code fully complies with all CRITICAL rules and has no major violations.
- Set `passed=False` if there are violations. List them in the `issues` parameter.
- Provide a brief score (0-100) based on compliance.
"""


@mcp.tool()
def submit_audit_result(passed: bool, issues: list[str], score: int = 0) -> str:
    """
    Submit the audit result after reviewing the code.
    
    Args:
        passed: Whether the code passed the audit
        issues: List of identified issues (empty if passed)
        score: Quality score from 0-100
    
    Returns:
        System instruction to either release code or request fixes
    """
    # Log the audit
    session.audit_history.append({
        "passed": passed,
        "issues": issues,
        "score": score,
        "retry_count": session.retry_count
    })
    
    if passed:
        session.status = "APPROVED"
        return f"""
✅ **[SYSTEM: AUDIT PASSED]**

Audit complete. Code quality score: {score}/100

**Final Code (Approved):**
```
{session.current_code}
```

You may now present this code to the user.
"""
    
    else:
        # Increment retry counter
        session.retry_count += 1
        session.status = "IDLE"
        
        issues_formatted = "\n".join([f"- {issue}" for issue in issues])
        
        return f"""
❌ **[SYSTEM INTERVENTION: REVISION REQUIRED]**

The audit has **FAILED**. Score: {score}/100

**Detected Issues:**
{issues_formatted}

**Your Task:**
1. Act as a **Senior Developer**.
2. Fix the issues in the code logically and thoroughly.
3. Call `submit_draft` again with the CORRECTED code.

**Constraints:**
- Strictly fix the mentioned issues.
- Do NOT verify it yourself; the Auditor will verify it again in the next step.
- Current retry count: {session.retry_count}/{rules_loader.get_max_retries()}
"""


@mcp.tool()
def reset_session() -> str:
    """
    Reset the current audit session.
    
    Returns:
        Confirmation message
    """
    session.reset()
    return "✅ Session reset successfully. Ready for new code submission."


if __name__ == "__main__":
    mcp.run()

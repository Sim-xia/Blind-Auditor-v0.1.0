"""
Rules Configuration Loader for Blind Auditor
"""

import json
from pathlib import Path
from typing import List, Dict, Any


class RulesLoader:
    """Loads and manages audit rules from rules.json."""
    
    def __init__(self, rules_path: str = "rules.json"):
        self.rules_path = Path(rules_path)
        self.rules_data: Dict[str, Any] = {}
        
    def load(self) -> Dict[str, Any]:
        """Load rules from the JSON file."""
        if not self.rules_path.exists():
            # Return default empty structure
            return {
                "project_name": "Unknown",
                "strict_mode": True,
                "max_retries": 3,
                "rules": []
            }
        
        with open(self.rules_path, 'r', encoding='utf-8') as f:
            self.rules_data = json.load(f)
        
        return self.rules_data
    
    def get_rules(self) -> List[Dict[str, Any]]:
        """Get the list of rules."""
        return self.rules_data.get("rules", [])
    
    def get_max_retries(self) -> int:
        """Get the maximum retry count."""
        return self.rules_data.get("max_retries", 3)
    
    def format_rules_for_prompt(self) -> str:
        """Format rules as a readable string for prompt injection."""
        rules = self.get_rules()
        if not rules:
            return "No rules configured."
        
        formatted = []
        for rule in rules:
            severity = rule.get("severity", "UNKNOWN")
            description = rule.get("description", "")
            rule_id = rule.get("id", "")
            formatted.append(f"[{severity}] {rule_id}: {description}")
        
        return "\n".join(formatted)

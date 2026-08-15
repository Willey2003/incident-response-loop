"""
Rule loader for Detection Engine.
Loads detection rules from YAML files.
"""

import yaml
import json
from pathlib import Path
from typing import List, Optional, Union
import structlog

from aegisforge_policy.rules import DetectionRule, RuleSet
from aegisforge_policy.loader import RuleLoader, load_policies_to_engine

logger = structlog.get_logger()


async def load_rules(rules_path: Optional[str] = None) -> RuleSet:
    """Load detection rules from directory."""
    import os
    
    path = rules_path or os.getenv("DETECTION_RULES_PATH", "/etc/aegisforge/rules")
    rule_loader = RuleLoader(base_path=path)
    
    rule_set = rule_loader.load_rule_set(
        directory=path,
        ruleset_id="default",
        name="Default Detection Rules",
        description="Built-in detection rules for AegisForge",
    )
    
    logger.info("Rules loaded", rule_count=len(rule_set.rules), path=path)
    return rule_set


def create_default_rule_set() -> 'RuleSet':
    """Create a default rule set with built-in rules."""
    from aegisforge_policy.loader import create_default_rule_set
    return create_default_rule_set()


def load_rules_from_yaml(file_path: Union[str, Path]) -> DetectionRule:
    """Load a single rule from YAML file."""
    path = Path(file_path)
    with open(path, 'r') as f:
        if path.suffix in ['.yaml', '.yml']:
            data = yaml.safe_load(f)
        elif path.suffix == '.json':
            data = json.load(f)
        else:
            raise ValueError(f"Unsupported file format: {path.suffix}")
        
        return DetectionRule.model_validate(data)


def load_rules_from_directory(directory: Union[str, Path], 
                              pattern: str = "*.y*ml") -> List[DetectionRule]:
    """Load all rules from a directory."""
    from aegisforge_policy.loader import RuleLoader
    rule_loader = RuleLoader(base_path=directory)
    return rule_loader.load_rules_from_directory(directory)


async def reload_rules_periodically(interval: int = 300):
    """Background task to reload rules periodically."""
    import asyncio
    import structlog
    
    logger = structlog.get_logger()
    
    while True:
        try:
            await asyncio.sleep(300)  # 5 minutes
            # In real implementation, this would trigger rule reload
            # For now, just log
            logger.debug("Periodic rule reload check")
        except asyncio.CancelledError:
            break
        except Exception as e:
            # Log error but continue
            pass
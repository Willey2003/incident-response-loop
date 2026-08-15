"""
Rule and playbook loaders for AegisForge policy engine.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import yaml
import json

from .rules import DetectionRule, RuleSet
from .playbooks import ResponsePlaybook
from .engine import PolicyEngine


class RuleLoader:
    """Load detection rules from files."""
    
    def __init__(self, base_path: Optional[Union[str, Path]] = None):
        self.base_path = Path(base_path) if base_path else Path.cwd()
    
    def load_rule(self, file_path: Union[str, Path]) -> DetectionRule:
        """Load a single rule from YAML file."""
        path = Path(file_path)
        if not path.is_absolute():
            path = self.base_path / path
        
        with open(path, 'r') as f:
            if path.suffix in ['.yaml', '.yml']:
                data = yaml.safe_load(f)
            elif path.suffix == '.json':
                data = json.load(f)
            else:
                raise ValueError(f"Unsupported file format: {path.suffix}")
        
        return DetectionRule.model_validate(data)
    
    def load_rules_from_directory(self, directory: Union[str, Path], 
                                   pattern: str = "*.y*ml") -> List[DetectionRule]:
        """Load all rules from a directory."""
        dir_path = Path(directory)
        if not dir_path.is_absolute():
            dir_path = self.base_path / dir_path
        
        rules = []
        for file_path in dir_path.glob(pattern):
            try:
                rule = self.load_rule(file_path)
                rules.append(rule)
            except Exception as e:
                print(f"Failed to load rule from {file_path}: {e}")
        return rules
    
    def load_rule_set(self, directory: Union[str, Path],
                       ruleset_id: str, name: str, description: str) -> 'RuleSet':
        """Load all rules from directory into a RuleSet."""
        from .rules import RuleSet
        rules = self.load_rules_from_directory(directory)
        return RuleSet(
            ruleset_id=ruleset_id,
            name=name,
            description=description,
            version="1.0.0",
            rules=rules,
        )


class PlaybookLoader:
    """Load response playbooks from files."""
    
    def __init__(self, base_path: Optional[Union[str, Path]] = None):
        self.base_path = Path(base_path) if base_path else Path.cwd()
    
    def load_playbook(self, file_path: Union[str, Path]) -> ResponsePlaybook:
        """Load a single playbook from YAML file."""
        path = Path(file_path)
        if not path.is_absolute():
            path = self.base_path / path
        
        with open(path, 'r') as f:
            if path.suffix in ['.yaml', '.yml']:
                data = yaml.safe_load(f)
            elif path.suffix == '.json':
                data = json.load(f)
            else:
                raise ValueError(f"Unsupported file format: {path.suffix}")
        
        return ResponsePlaybook.model_validate(data)
    
    def load_playbooks_from_directory(self, directory: Union[str, Path],
                                       pattern: str = "*.y*ml") -> List[ResponsePlaybook]:
        """Load all playbooks from a directory."""
        dir_path = Path(directory)
        if not dir_path.is_absolute():
            dir_path = self.base_path / dir_path
        
        playbooks = []
        for file_path in dir_path.glob(pattern):
            try:
                playbook = self.load_playbook(file_path)
                playbooks.append(playbook)
            except Exception as e:
                print(f"Failed to load playbook from {file_path}: {e}")
        return playbooks
    
    def load_playbooks_to_engine(self, engine: 'PolicyEngine', 
                                  directory: Union[str, Path],
                                  pattern: str = "*.y*ml") -> int:
        """Load all playbooks from directory into engine."""
        playbooks = self.load_playbooks_from_directory(directory, pattern)
        count = 0
        for playbook in playbooks:
            engine.register_playbook(playbook)
            count += 1
        return count


def load_policies_to_engine(engine: PolicyEngine,
                           rules_directory: Optional[Union[str, Path]] = None,
                           playbooks_directory: Optional[Union[str, Path]] = None,
                           base_path: Optional[Union[str, Path]] = None) -> Dict[str, int]:
    """Load all rules and playbooks into a PolicyEngine."""
    results = {"rules": 0, "playbooks": 0}
    
    if rules_directory:
        rule_loader = RuleLoader(base_path)
        rule_set = rule_loader.load_rule_set(
            rules_directory,
            ruleset_id="default",
            name="Default Rule Set",
            description="Default detection rules"
        )
        engine.register_rule_set(rule_set)
        results["rules"] = len(rule_set.rules)
    
    if playbooks_directory:
        playbook_loader = PlaybookLoader(base_path)
        count = playbook_loader.load_playbooks_to_engine(engine, playbooks_directory)
        results["playbooks"] = count
    
    return results


def create_default_rule_set() -> RuleSet:
    """Create a default rule set with built-in rules."""
    from .rules import DetectionRule, RuleCondition, RuleConditionGroup, RuleAction, RuleOperator, LogicalOperator
    
    rules = [
        # Brute force detection
        DetectionRule(
            rule_id="DET-001",
            name="Repeated Failed Authentication",
            description="Detects repeated failed login attempts from same source",
            severity="high",
            mitre_techniques=["T1110.001", "T1110.003"],
            condition_group=RuleConditionGroup(
                operator=LogicalOperator.AND,
                conditions=[
                    RuleCondition(field="event_type", operator=RuleOperator.EQUALS, value="login_failed"),
                    RuleCondition(field="source_ip", operator=RuleOperator.EXISTS),
                ]
            ),
            correlation_window_seconds=300,
            correlation_threshold=5,
            correlation_group_by=["source_ip", "username"],
            actions=[RuleAction(action_type="create_alert", severity="high")],
        ),
        
        # Privileged container detection
        DetectionRule(
            rule_id="DET-002",
            name="Privileged Container Creation",
            description="Detects creation of privileged containers",
            severity="high",
            mitre_techniques=["T1611", "T1610"],
            condition_group=RuleConditionGroup(
                operator=LogicalOperator.AND,
                conditions=[
                    RuleCondition(field="event_type", operator=RuleOperator.EQUALS, value="container_create"),
                    RuleCondition(field="privileged", operator=RuleOperator.EQUALS, value=True),
                ]
            ),
            actions=[RuleAction(action_type="create_alert", severity="high")],
        ),
        
        # DNS tunneling detection
        DetectionRule(
            rule_id="DET-003",
            name="DNS Tunneling Detection",
            description="Detects potential DNS tunneling based on entropy and query patterns",
            severity="high",
            mitre_techniques=["T1048.003", "T1572"],
            condition_group=RuleConditionGroup(
                operator=LogicalOperator.AND,
                conditions=[
                    RuleCondition(field="event_type", operator=RuleOperator.EQUALS, value="dns_query"),
                    RuleCondition(field="entropy_score", operator=RuleOperator.GREATER_THAN, value=0.8),
                ]
            ),
            actions=[RuleAction(action_type="create_alert", severity="high")],
        ),
        
        # Crypto mining detection
        DetectionRule(
            rule_id="DET-004",
            name="Cryptocurrency Mining Process",
            description="Detects known cryptominer process names",
            severity="high",
            mitre_techniques=["T1496"],
            condition_group=RuleConditionGroup(
                operator=LogicalOperator.AND,
                conditions=[
                    RuleCondition(field="event_type", operator=RuleOperator.EQUALS, value="process_start"),
                    RuleCondition(
                        field="process_name",
                        operator=RuleOperator.REGEX_MATCH,
                        value=r"(xmrig|minergate|cryptonight|monero|stratum)"
                    ),
                ]
            ),
            actions=[RuleAction(action_type="create_alert", severity="high")],
        ),
        
        # Data exfiltration detection
        DetectionRule(
            rule_id="DET-005",
            name="Large Data Transfer",
            description="Detects unusual large data transfers",
            severity="high",
            mitre_techniques=["T1041", "T1048.003"],
            condition_group=RuleConditionGroup(
                operator=LogicalOperator.AND,
                conditions=[
                    RuleCondition(field="event_type", operator=RuleOperator.EQUALS, value="network_connection"),
                    RuleCondition(field="bytes_total", operator=RuleOperator.GREATER_THAN, value=100_000_000),
                ]
            ),
            actions=[RuleAction(action_type="create_alert", severity="high")],
        ),
        
        # Privileged container escape attempt
        DetectionRule(
            rule_id="DET-006",
            name="Container Escape Attempt",
            description="Detects container escape via privileged operations",
            severity="critical",
            mitre_techniques=["T1611", "T1610", "T1609"],
            condition_group=RuleConditionGroup(
                operator=LogicalOperator.OR,
                conditions=[
                    RuleCondition(field="event_type", operator=RuleOperator.EQUALS, value="container_escape"),
                    RuleCondition(field="event_type", operator=RuleOperator.EQUALS, value="kernel_exploit"),
                    RuleCondition(
                        field="event_type", operator=RuleOperator.EQUALS, value="syscall_anomaly"
                    ),
                ]
            ),
            actions=[RuleAction(action_type="create_alert", severity="critical")],
        ),
    ]
    
    return RuleSet(
        ruleset_id="default",
        name="Default Detection Rules",
        description="Built-in detection rules for AegisForge",
        version="1.0.0",
        rules=rules,
    )


def create_default_playbooks() -> List[ResponsePlaybook]:
    """Create default response playbooks."""
    from .playbooks import (
        ResponsePlaybook, PlaybookStep, PlaybookTrigger, PlaybookStepType,
        PlaybookTriggerType, ApprovalType
    )
    
    return [
        ResponsePlaybook(
            playbook_id="PB-001",
            name="Quarantine Compromised Workload",
            description="Isolate a compromised pod using NetworkPolicy",
            version="1.0.0",
            triggers=[
                PlaybookTrigger(
                    trigger_type=PlaybookTriggerType.ALERT_MATCH,
                    severity_threshold=["critical", "high"],
                    mitre_techniques=["T1021.*", "T1570"],
                )
            ],
            steps=[
                PlaybookStep(
                    step_id="step-1",
                    name="Generate NetworkPolicy",
                    description="Generate deny-all NetworkPolicy for target pod",
                    step_type=PlaybookStepType.EXECUTE_ACTION,
                    order=1,
                    action_type="generate_network_policy",
                    action_parameters={
                        "policy_type": "deny_all",
                        "target_selector": "{{ alert.affected_pods[0] }}",
                    },
                    dry_run_supported=True,
                ),
                PlaybookStep(
                    step_id="step-2",
                    name="Apply NetworkPolicy (Dry Run)",
                    description="Apply NetworkPolicy in dry-run mode",
                    step_type=PlaybookStepType.EXECUTE_ACTION,
                    order=2,
                    depends_on=["step-1"],
                    action_type="apply_network_policy",
                    action_parameters={
                        "policy": "{{ step-1.output.policy }}",
                        "dry_run": True,
                    },
                    approval_required=True,
                ),
                PlaybookStep(
                    step_id="step-3",
                    name="Apply NetworkPolicy (Production)",
                    description="Apply NetworkPolicy after approval",
                    step_type=PlaybookStepType.EXECUTE_ACTION,
                    order=3,
                    depends_on=["step-2"],
                    action_type="apply_network_policy",
                    action_parameters={
                        "policy": "{{ step-1.output.policy }}",
                        "dry_run": False,
                    },
                    approval_required=True,
                ),
            ],
            author="AegisForge Team",
            tags=["containment", "network", "quarantine"],
            tags_mitre=["T1021", "T1570"],
        ),
        
        ResponsePlaybook(
            playbook_id="PB-002",
            name="Scale Suspicious Deployment to Zero",
            description="Scale a suspicious deployment to zero replicas",
            version="1.0.0",
            triggers=[
                PlaybookTrigger(
                    trigger_type=PlaybookTriggerType.ALERT_MATCH,
                    severity_threshold=["critical", "high"],
                    mitre_techniques=["T1499.*", "T1529"],
                )
            ],
            steps=[
                PlaybookStep(
                    step_id="step-1",
                    name="Get Current Replicas",
                    description="Get current replica count for deployment",
                    step_type=PlaybookStepType.EXECUTE_ACTION,
                    order=1,
                    action_type="get_deployment_replicas",
                    action_parameters={
                        "deployment": "{{ alert.affected_deployment }}",
                        "namespace": "{{ alert.namespace }}",
                    },
                ),
                PlaybookStep(
                    step_id="step-2",
                    name="Scale to Zero (Dry Run)",
                    description="Scale deployment to zero in dry-run mode",
                    step_type=PlaybookStepType.EXECUTE_ACTION,
                    order=2,
                    depends_on=["step-1"],
                    action_type="scale_deployment",
                    action_parameters={
                        "deployment": "{{ alert.affected_deployment }}",
                        "namespace": "{{ alert.namespace }}",
                        "replicas": 0,
                        "dry_run": True,
                    },
                    approval_required=True,
                ),
                PlaybookStep(
                    step_id="step-3",
                    name="Scale to Zero (Production)",
                    description="Scale deployment to zero after approval",
                    step_type=PlaybookStepType.EXECUTE_ACTION,
                    order=3,
                    depends_on=["step-2"],
                    action_type="scale_deployment",
                    action_parameters={
                        "deployment": "{{ alert.affected_deployment }}",
                        "namespace": "{{ alert.namespace }}",
                        "replicas": 0,
                        "dry_run": False,
                    },
                    approval_required=True,
                ),
            ],
            author="AegisForge Team",
            tags=["containment", "scale", "deployment"],
            tags_mitre=["T1499", "T1529"],
        ),
    ]
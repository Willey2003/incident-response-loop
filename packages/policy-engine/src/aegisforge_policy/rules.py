"""
Detection rule models for AegisForge platform.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, ConfigDict, field_validator


class RuleSeverity(str, Enum):
    """Rule severity levels."""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RuleOperator(str, Enum):
    """Operators for rule conditions."""
    EQUALS = "eq"
    NOT_EQUALS = "ne"
    GREATER_THAN = "gt"
    GREATER_THAN_OR_EQUAL = "gte"
    LESS_THAN = "lt"
    LESS_THAN_OR_EQUAL = "lte"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    REGEX_MATCH = "regex"
    REGEX_NOT_MATCH = "regex_not"
    IN_LIST = "in"
    NOT_IN_LIST = "not_in"
    EXISTS = "exists"
    NOT_EXISTS = "not_exists"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    IP_IN_CIDR = "ip_in_cidr"
    IP_NOT_IN_CIDR = "ip_not_in_cidr"


class LogicalOperator(str, Enum):
    """Logical operators for combining conditions."""
    AND = "and"
    OR = "or"
    NOT = "not"


class RuleCondition(BaseModel):
    """Single condition in a detection rule."""
    model_config = ConfigDict(extra="allow")
    
    field: str = Field(..., description="Event field to evaluate")
    operator: RuleOperator
    value: Optional[Any] = None
    values: Optional[List[Any]] = None
    case_sensitive: bool = True
    
    @field_validator("values")
    @classmethod
    def check_values(cls, v: Optional[List[Any]]) -> Optional[List[Any]]:
        if v is not None and len(v) == 0:
            raise ValueError("values list cannot be empty")
        return v


class RuleConditionGroup(BaseModel):
    """Group of conditions with logical operator."""
    model_config = ConfigDict(extra="allow")
    
    operator: LogicalOperator = LogicalOperator.AND
    conditions: List[Union[RuleCondition, "RuleConditionGroup"]] = Field(default_factory=list)
    
    def evaluate(self, event: Dict[str, any]) -> bool:
        """Evaluate condition group against event data."""
        results = []
        for condition in self.conditions:
            if isinstance(condition, RuleCondition):
                results.append(self._evaluate_condition(condition, event))
            elif isinstance(condition, RuleConditionGroup):
                results.append(condition.evaluate(event))
        
        if self.operator == LogicalOperator.AND:
            return all(results)
        elif self.operator == LogicalOperator.OR:
            return any(results)
        elif self.operator == LogicalOperator.NOT:
            return not all(results)
        return False
    
    def _evaluate_condition(self, condition: RuleCondition, event: Dict[str, any]) -> bool:
        """Evaluate a single condition against event data."""
        field_value = self._get_nested_value(event, condition.field)
        
        if field_value is None:
            if condition.operator == RuleOperator.EXISTS:
                return False
            elif condition.operator == RuleOperator.NOT_EXISTS:
                return True
            return False
        
        op = condition.operator
        value = condition.value
        values = condition.values
        
        # Handle string case sensitivity
        if isinstance(field_value, str) and isinstance(value, str) and not condition.case_sensitive:
            field_value = field_value.lower()
            value = value.lower()
            if values:
                values = [v.lower() for v in values]
        
        if op == RuleOperator.EQUALS:
            return field_value == value
        elif op == RuleOperator.NOT_EQUALS:
            return field_value != value
        elif op == RuleOperator.GREATER_THAN:
            return field_value > value
        elif op == RuleOperator.GREATER_THAN_OR_EQUAL:
            return field_value >= value
        elif op == RuleOperator.LESS_THAN:
            return field_value < value
        elif op == RuleOperator.LESS_THAN_OR_EQUAL:
            return field_value <= value
        elif op == RuleOperator.CONTAINS:
            return str(value) in str(field_value)
        elif op == RuleOperator.NOT_CONTAINS:
            return str(value) not in str(field_value)
        elif op == RuleOperator.REGEX_MATCH:
            import re
            return bool(re.search(str(value), str(field_value)))
        elif op == RuleOperator.REGEX_NOT_MATCH:
            import re
            return not bool(re.search(str(value), str(field_value)))
        elif op == RuleOperator.IN_LIST:
            return field_value in (values or [])
        elif op == RuleOperator.NOT_IN_LIST:
            return field_value not in (values or [])
        elif op == RuleOperator.STARTS_WITH:
            return str(field_value).startswith(str(value))
        elif op == RuleOperator.ENDS_WITH:
            return str(field_value).endswith(str(value))
        elif op == RuleOperator.IP_IN_CIDR:
            import ipaddress
            try:
                return ipaddress.ip_address(field_value) in ipaddress.ip_network(value)
            except:
                return False
        elif op == RuleOperator.IP_NOT_IN_CIDR:
            import ipaddress
            try:
                return ipaddress.ip_address(field_value) not in ipaddress.ip_network(value)
            except:
                return False
        elif op == RuleOperator.EXISTS:
            return True
        elif op == RuleOperator.NOT_EXISTS:
            return False
        
        return False
    
    def _get_nested_value(self, data: Dict[str, any], path: str) -> Any:
        """Get nested value from dict using dot notation."""
        keys = path.split(".")
        value = data
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            elif isinstance(value, list) and key.isdigit():
                idx = int(key)
                if idx < len(value):
                    value = value[idx]
                else:
                    return None
            else:
                return None
            if value is None:
                return None
        return value


class RuleAction(BaseModel):
    """Action to take when rule matches."""
    model_config = ConfigDict(extra="allow")
    
    action_type: str
    parameters: Dict[str, any] = Field(default_factory=dict)
    severity: str = "medium"
    description: str = ""


class DetectionRule(BaseModel):
    """Detection rule with conditions and actions."""
    model_config = ConfigDict(extra="allow")
    
    # Rule identification
    rule_id: str
    name: str
    description: str
    version: int = 1
    
    # Classification
    severity: str = "medium"  # info, low, medium, high, critical
    enabled: bool = True
    tags: List[str] = Field(default_factory=list)
    
    # MITRE ATT&CK mapping
    mitre_techniques: List[str] = Field(default_factory=list)
    mitre_tactics: List[str] = Field(default_factory=list)
    
    # Rule logic
    condition_group: Optional[RuleConditionGroup] = None
    actions: List[RuleAction] = Field(default_factory=list)
    
    # Correlation
    correlation_window_seconds: Optional[int] = None
    correlation_threshold: Optional[int] = None
    correlation_group_by: List[str] = Field(default_factory=list)
    
    # Suppression
    suppression_window_seconds: int = 300
    suppression_group_by: List[str] = Field(default_factory=list)
    
    # Enrichment
    enrichment_sources: List[str] = Field(default_factory=list)
    
    # Metadata
    author: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    source: str = "user"
    
    # Testing
    test_cases: List[Dict[str, any]] = Field(default_factory=list)
    
    # Deprecation
    deprecated: bool = False
    deprecated_at: Optional[datetime] = None
    replacement_rule_id: Optional[str] = None
    
    def evaluate(self, event: Dict[str, any]) -> bool:
        """Evaluate rule against event."""
        if not self.enabled:
            return False
        if self.condition_group is None:
            return False
        return self.condition_group.evaluate(event)
    
    def get_actions(self) -> List[RuleAction]:
        """Get actions to execute on match."""
        return self.actions
    
    def to_yaml(self) -> str:
        """Serialize rule to YAML."""
        import yaml
        return yaml.dump(self.model_dump(mode="json"), sort_keys=False)
    
    @classmethod
    def from_yaml(cls, yaml_str: str) -> "DetectionRule":
        """Create rule from YAML string."""
        import yaml
        data = yaml.safe_load(yaml_str)
        return cls.model_validate(data)


class RuleSet(BaseModel):
    """Collection of detection rules."""
    model_config = ConfigDict(extra="allow")
    
    ruleset_id: str
    name: str
    description: str
    version: str
    rules: List[DetectionRule] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    def get_enabled_rules(self) -> List[DetectionRule]:
        return [r for r in self.rules if r.enabled and not r.deprecated]
    
    def evaluate_all(self, event: Dict[str, any]) -> List[DetectionRule]:
        matched = []
        for rule in self.get_enabled_rules():
            if rule.evaluate(event):
                matched.append(rule)
        return matched
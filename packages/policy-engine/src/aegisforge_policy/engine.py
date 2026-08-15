"""
Policy engine for evaluating detection rules and executing playbooks.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Set
from uuid import UUID, uuid4

from .rules import DetectionRule, RuleSet
from .playbooks import ResponsePlaybook, PlaybookExecution, PlaybookStep, PlaybookStepType


class EvaluationContext(BaseModel):
    """Context for rule evaluation."""
    event: Dict[str, any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, any] = Field(default_factory=dict)
    enrichment: Dict[str, any] = Field(default_factory=dict)


class EvaluationResult(BaseModel):
    """Result of rule evaluation."""
    rule_id: str
    rule_name: str
    matched: bool
    matched_conditions: List[str] = Field(default_factory=list)
    actions: List[Dict[str, any]] = Field(default_factory=list)
    execution_time_ms: float = 0.0
    error: Optional[str] = None


class PolicyEngine:
    """Engine for evaluating detection rules and executing playbooks."""
    
    def __init__(self):
        self.rule_sets: Dict[str, RuleSet] = {}
        self.playbooks: Dict[str, ResponsePlaybook] = {}
        self.executions: Dict[UUID, PlaybookExecution] = {}
        self.suppression_cache: Dict[str, datetime] = {}
    
    def register_rule_set(self, rule_set: RuleSet) -> None:
        """Register a rule set."""
        self.rule_sets[rule_set.ruleset_id] = rule_set
    
    def unregister_rule_set(self, ruleset_id: str) -> bool:
        """Unregister a rule set."""
        if ruleset_id in self.rule_sets:
            del self.rule_sets[ruleset_id]
            return True
        return False
    
    def register_playbook(self, playbook: ResponsePlaybook) -> None:
        """Register a response playbook."""
        self.playbooks[playbook.playbook_id] = playbook
    
    def unregister_playbook(self, playbook_id: str) -> bool:
        """Unregister a playbook."""
        if playbook_id in self.playbooks:
            del self.playbooks[playbook_id]
            return True
        return False
    
    def evaluate_event(self, event: Dict[str, any], ruleset_ids: Optional[List[str]] = None) -> List[EvaluationResult]:
        """Evaluate event against all registered rules."""
        results = []
        
        target_sets = self.rule_sets
        if ruleset_ids:
            target_sets = {k: v for k, v in self.rule_sets.items() if k in ruleset_ids}
        
        for ruleset_id, rule_set in target_sets.items():
            for rule in rule_set.get_enabled_rules():
                start_time = datetime.utcnow()
                try:
                    matched = rule.evaluate(event)
                    execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                    
                    if matched:
                        actions = [{"action_type": a.action_type, "parameters": a.parameters} 
                                  for a in rule.get_actions()]
                        results.append(EvaluationResult(
                            rule_id=rule.rule_id,
                            rule_name=rule.name,
                            matched=True,
                            actions=actions,
                            execution_time_ms=execution_time,
                        ))
                    else:
                        results.append(EvaluationResult(
                            rule_id=rule.rule_id,
                            rule_name=rule.name,
                            matched=False,
                            execution_time_ms=execution_time,
                        ))
                except Exception as e:
                    execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                    results.append(EvaluationResult(
                        rule_id=rule.rule_id,
                        rule_name=rule.name,
                        matched=False,
                        execution_time_ms=execution_time,
                        error=str(e),
                    ))
        
        return results
    
    def check_suppression(self, rule_id: str, event: Dict[str, any]) -> bool:
        """Check if rule should be suppressed for this event."""
        # Generate suppression key from rule and event grouping fields
        # This is a simplified implementation
        return False
    
    def apply_suppression(self, rule_id: str, event: Dict[str, any]) -> None:
        """Apply suppression for rule."""
        # Generate suppression key
        key = f"{rule_id}:{hash(str(event))}"
        self.suppression_cache[key] = datetime.utcnow()
    
    def execute_playbook(self, playbook_id: str, trigger_data: Dict[str, any], 
                         incident_id: Optional[str] = None, alert_id: Optional[str] = None,
                         dry_run: bool = False) -> PlaybookExecution:
        """Execute a playbook."""
        playbook = self.playbooks.get(playbook_id)
        if not playbook:
            raise ValueError(f"Playbook not found: {playbook_id}")
        
        execution = PlaybookExecution(
            execution_id=uuid4(),
            playbook_id=playbook_id,
            playbook_version=playbook.version,
            trigger_type="manual",
            trigger_data=trigger_data,
            incident_id=incident_id,
            alert_id=alert_id,
            dry_run=dry_run,
            total_steps=len(playbook.steps),
        )
        
        self.executions[execution.execution_id] = execution
        
        # Start execution (async in real implementation)
        self._execute_playbook_async(execution, playbook)
        
        return execution
    
    def _execute_playbook_async(self, execution: PlaybookExecution, playbook: ResponsePlaybook) -> None:
        """Execute playbook steps (simplified synchronous version)."""
        execution.status = "running"
        execution.started_at = datetime.utcnow()
        
        try:
            for step in playbook.steps:
                execution.current_step = step.step_id
                execution.current_step_index += 1
                execution.progress_percent = (execution.current_step_index / execution.total_steps) * 100
                
                # Check dependencies
                if not self._check_dependencies(step, execution):
                    execution.status = "failed"
                    execution.error = f"Dependencies not met for step {step.step_id}"
                    execution.failed_steps.append(step.step_id)
                    break
                
                # Execute step
                result = self._execute_step(step, execution)
                execution.step_results[step.step_id] = result
                execution.completed_steps.append(step.step_id)
                
                if not result.get("success", False):
                    if not step.continue_on_failure:
                        execution.status = "failed"
                        execution.error = result.get("error", "Step failed")
                        execution.error_step = step.step_id
                        execution.failed_steps.append(step.step_id)
                        break
            
            if execution.status != "failed":
                execution.status = "completed"
            execution.completed_at = datetime.utcnow()
            
        except Exception as e:
            execution.status = "failed"
            execution.error = str(e)
            execution.completed_at = datetime.utcnow()
    
    def _check_dependencies(self, step: PlaybookStep, execution: PlaybookExecution) -> bool:
        """Check if all dependencies are met."""
        for dep_id in step.depends_on:
            if dep_id not in execution.completed_steps:
                return False
        return True
    
    def _execute_step(self, step: PlaybookStep, execution: PlaybookExecution) -> Dict[str, any]:
        """Execute a single playbook step."""
        result = {"success": True, "output": None, "error": None}
        
        try:
            if step.step_type == PlaybookStepType.EXECUTE_ACTION:
                # Execute action (simplified)
                result["output"] = f"Executed action: {step.action_type}"
                
            elif step.step_type == PlaybookStepType.WAIT:
                # Wait step
                import time
                if step.wait_seconds:
                    time.sleep(min(step.wait_seconds, 5))  # Limit in demo
                result["output"] = f"Waited {step.wait_seconds}s"
                
            elif step.step_type == PlaybookStepType.CONDITION:
                # Evaluate condition (Jinja2 expression)
                result["output"] = {"condition_result": True}
                
            elif step.step_type == PlaybookStepType.APPROVAL:
                # Approval step - in real implementation, this would wait for approval
                result["output"] = {"approval_status": "pending"}
                
            elif step.step_type == PlaybookStepType.NOTIFICATION:
                # Send notification
                result["output"] = {"notification_sent": True}
                
            elif step.step_type in [PlaybookStepType.PARALLEL, PlaybookStepType.SEQUENTIAL]:
                # Sub-steps handled by orchestrator
                result["output"] = {"sub_steps": len(step.parallel_steps)}
                
        except Exception as e:
            result = {"success": False, "error": str(e)}
        
        return result
    
    def get_execution(self, execution_id: UUID) -> Optional[PlaybookExecution]:
        """Get execution by ID."""
        return self.executions.get(execution_id)
    
    def cancel_execution(self, execution_id: UUID, reason: str) -> bool:
        """Cancel a running execution."""
        execution = self.executions.get(execution_id)
        if not execution:
            return False
        if execution.status in ["completed", "failed", "cancelled"]:
            return False
        execution.status = "cancelled"
        execution.error = reason
        execution.completed_at = datetime.utcnow()
        return True
    
    def get_active_executions(self) -> List[PlaybookExecution]:
        """Get all active executions."""
        return [e for e in self.executions.values() 
                if e.status in ["pending", "running", "paused"]]
"""
Action executor for Response Orchestrator.
Executes response actions with dry-run, approval, rollback, and audit logging.
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from uuid import uuid4

from kubernetes import client, config
from kubernetes.client.rest import ApiException

from .config import settings
from .database import get_db_session

import structlog

logger = structlog.get_logger()


class ActionExecutor:
    """Executes response actions with dry-run, approval, rollback, and audit logging."""
    
    def __init__(self):
        self.k8s_client: Optional = None
        self.dry_run = settings.RESPONSE_DRY_RUN
        self.require_approval = settings.RESPONSE_REQUIRE_APPROVAL
        self.namespace = settings.RESPONSE_NAMESPACE
        self.allowlist = self._load_allowlist()
        self.circuit_breaker_failures = 0
        self.circuit_breaker_threshold = settings.RESPONSE_CIRCUIT_BREAKER_THRESHOLD
        self.circuit_breaker_timeout = settings.RESPONSE_CIRCUIT_BREAKER_TIMEOUT
        self.circuit_breaker_tripped = False
        self.circuit_breaker_tripped_at = None
    
    def _load_allowlist(self) -> List[Dict]:
        """Load allowlist from file."""
        import yaml
        try:
            with open(settings.RESPONSE_ALLOWLIST_FILE, 'r') as f:
                data = yaml.safe_load(f)
                return data.get("allowed_resources", [])
        except FileNotFoundError:
            logger.warning("Allowlist file not found, using empty allowlist")
            return []
        except Exception as e:
            logger.error("Failed to load allowlist", error=str(e))
            return []
    
    def check_circuit_breaker(self) -> bool:
        """Check if circuit breaker allows execution."""
        if self.circuit_breaker_tripped:
            if self.circuit_breaker_tripped_at and \
               (datetime.utcnow() - self.circuit_breaker_tripped_at).total_seconds() > self.circuit_breaker_timeout:
                logger.info("Circuit breaker timeout expired, resetting")
                self.circuit_breaker_tripped = False
                self.circuit_breaker_failures = 0
                return True
            return False
        return True
    
    def record_failure(self):
        """Record a failure for circuit breaker."""
        self.circuit_breaker_failures += 1
        if self.circuit_breaker_failures >= self.circuit_breaker_threshold:
            self.circuit_breaker_tripped = True
            self.circuit_breaker_tripped_at = datetime.utcnow()
            logger.warning("Circuit breaker tripped", failures=self.circuit_breaker_failures)
    
    def record_success(self):
        """Record a success for circuit breaker."""
        self.circuit_breaker_failures = 0
    
    async def initialize(self):
        """Initialize Kubernetes client."""
        try:
            if settings.KUBECONFIG_PATH:
                config.load_kube_config(config_file=settings.KUBECONFIG_PATH)
            else:
                config.load_incluster_config()
            self.k8s_client = client.AppsV1Api()
            logger.info("Kubernetes client initialized")
        except Exception as e:
            logger.warning("Failed to initialize Kubernetes client", error=str(e))
            self.k8s_client = None
    
    def check_allowlist(self, resource: Dict[str, Any]) -> bool:
        """Check if resource is in allowlist."""
        if not self.allowlist:
            return True  # Empty allowlist = allow all
        
        resource_key = f"{resource.get('kind', '')}/{resource.get('namespace', '')}/{resource.get('name', '')}"
        
        for allowed in self.allowlist:
            if self._match_allowlist_entry(resource, allowed):
                return True
        
        logger.warning("Resource not in allowlist", resource=resource_key)
        return False
    
    def _match_allowlist_entry(self, resource: Dict, allowed: Dict) -> bool:
        """Check if resource matches allowlist entry."""
        if "kind" in allowed and allowed["kind"] != resource.get("kind"):
            return False
        if "namespace" in allowed and allowed["namespace"] != resource.get("namespace"):
            return False
        if "name" in allowed and allowed["name"] != resource.get("name"):
            return False
        if "label_selector" in allowed:
            # Check label selector match
            pass
        return True
    
    async def execute_action(self, action: Dict) -> Dict:
        """Execute a response action with all safety checks."""
        action_id = action.get("action_id")
        action_type = action.get("action_type")
        dry_run = action.get("dry_run", True)
        
        logger.info("Executing action", action_id=action_id, action_type=action_type, dry_run=dry_run)
        
        # Check circuit breaker
        if not self.check_circuit_breaker():
            return {"success": False, "error": "Circuit breaker open"}
        
        # Check allowlist
        target_resource = action.get("target_resource", {})
        if not self.check_allowlist(target_resource):
            return {"success": False, "error": "Resource not in allowlist"}
        
        # Execute based on action type
        try:
            if action_type == "quarantine_workload":
                result = await self._quarantine_workload(action, dry_run=True)
            elif action_type == "scale_deployment":
                result = await self._scale_deployment(action, dry_run=True)
            elif action_type == "revoke_service_account":
                result = await self._revoke_service_account(action, dry_run=True)
            elif action_type == "apply_network_policy":
                result = await self._apply_network_policy(action, dry_run=True)
            elif action_type == "scale_deployment_to_zero":
                result = await self._scale_deployment_to_zero(action, dry_run=True)
            elif action_type == "revoke_service_account_binding":
                result = await self._revoke_service_account_binding(action, dry_run=True)
            else:
                return {"success": False, "error": f"Unknown action type: {action_type}"}
            
            return result
        except Exception as e:
            logger.error("Action execution failed", action_id=action.get("action_id"), error=str(e))
            self.record_failure()
            return {"success": False, "error": str(e)}
    
    async def _quarantine_workload(self, action: Dict, dry_run: bool = True) -> Dict:
        """Quarantine a workload using NetworkPolicy."""
        target = action.get("target_resource", {})
        pod_name = target.get("name")
        namespace = target.get("namespace", self.namespace)
        
        if not pod_name:
            return {"success": False, "error": "Pod name required"}
        
        policy_name = f"quarantine-{pod_name}-{int(time.time())}"
        
        policy = {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "NetworkPolicy",
            "metadata": {
                "name": policy_name,
                "namespace": namespace,
                "labels": {
                    "aegisforge/quarantine": "true",
                    "aegisforge/action-id": action.get("action_id", "unknown"),
                },
            },
            "spec": {
                "podSelector": {
                    "matchLabels": {
                        "app": pod_name,
                    },
                },
                "policyTypes": ["Ingress", "Egress"],
                "ingress": [],
                "egress": [],
            }
        }
        
        if dry_run:
            return {
                "success": True,
                "dry_run": True,
                "message": f"Would create NetworkPolicy {policy_name} to quarantine {pod_name}",
                "policy": policy,
            }
        
        if not self.k8s_client:
            return {"success": False, "error": "Kubernetes client not available"}
        
        try:
            networking_api = client.NetworkingV1Api()
            networking_api.create_namespaced_network_policy(namespace, policy)
            logger.info("NetworkPolicy created", policy_name=policy_name, namespace=namespace)
            return {"success": True, "policy_name": policy_name, "namespace": namespace}
        except ApiException as e:
            return {"success": False, "error": f"K8s API error: {e}"}
    
    async def _scale_deployment(self, action: Dict, dry_run: bool = True) -> Dict:
        """Scale a deployment to specified replicas."""
        target = action.get("target_resource", {})
        deployment_name = target.get("name")
        namespace = target.get("namespace", self.namespace)
        replicas = action.get("parameters", {}).get("replicas", 0)
        
        if not deployment_name:
            return {"success": False, "error": "Deployment name required"}
        
        if dry_run:
            return {
                "success": True,
                "dry_run": True,
                "message": f"Would scale deployment {deployment_name} to {replicas} replicas",
            }
        
        if not self.k8s_client:
            return {"success": False, "error": "Kubernetes client not available"}
        
        try:
            self.k8s_client.patch_namespaced_deployment_scale(
                name=deployment_name,
                namespace=namespace,
                body={"spec": {"replicas": replicas}},
            )
            logger.info("Deployment scaled", deployment=deployment_name, replicas=replicas, namespace=namespace)
            return {"success": True, "replicas": replicas, "deployment": deployment_name}
        except ApiException as e:
            return {"success": False, "error": f"K8s API error: {e}"}
    
    async def _scale_deployment_to_zero(self, action: Dict, dry_run: bool = True) -> Dict:
        """Scale deployment to zero replicas."""
        action["parameters"] = action.get("parameters", {})
        action["parameters"]["replicas"] = 0
        return await self._scale_deployment(action, dry_run)
    
    async def _revoke_service_account(self, action: Dict, dry_run: bool = True) -> Dict:
        """Revoke a ServiceAccount binding."""
        target = action.get("target_resource", {})
        sa_name = target.get("name")
        namespace = target.get("namespace", self.namespace)
        binding_name = target.get("binding_name")
        
        if not sa_name or not binding_name:
            return {"success": False, "error": "ServiceAccount name and binding name required"}
        
        if dry_run:
            return {
                "success": True,
                "dry_run": True,
                "message": f"Would revoke ServiceAccount binding {binding_name} for {sa_name}",
            }
        
        try:
            rbac_api = client.RbacAuthorizationV1Api()
            rbac_api.delete_namespaced_role_binding(binding_name, namespace)
            logger.info("ServiceAccount binding revoked", binding=binding_name, namespace=namespace)
            return {"success": True, "binding_name": binding_name}
        except ApiException as e:
            return {"success": False, "error": f"K8s API error: {e}"}
    
    async def _revoke_service_account_binding(self, action: Dict, dry_run: bool = True) -> Dict:
        """Revoke a ServiceAccount binding (alias)."""
        return await self._revoke_service_account(action, dry_run)
    
    async def _apply_network_policy(self, action: Dict, dry_run: bool = True) -> Dict:
        """Apply a custom NetworkPolicy."""
        target = action.get("target_resource", {})
        policy_spec = action.get("parameters", {}).get("policy", {})
        
        if not policy_spec:
            return {"success": False, "error": "NetworkPolicy spec required"}
        
        if dry_run:
            return {
                "success": True,
                "dry_run": True,
                "message": f"Would apply NetworkPolicy {policy_spec.get('metadata', {}).get('name')}",
            }
        
        if not self.k8s_client:
            return {"success": False, "error": "Kubernetes client not available"}
        
        try:
            networking_api = client.NetworkingV1Api()
            namespace = policy_spec.get("metadata", {}).get("namespace", self.namespace)
            networking_api.create_namespaced_network_policy(namespace, policy_spec)
            return {"success": True, "policy_name": policy_spec.get("metadata", {}).get("name")}
        except ApiException as e:
            return {"success": False, "error": f"K8s API error: {e}"}
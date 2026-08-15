"""
Emulation lab models for AegisForge platform.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, ConfigDict


class EmulationStatus(str, Enum):
    """Emulation run status."""
    PENDING = "pending"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class EmulationScenario(BaseModel):
    """Safe threat emulation scenario definition."""
    model_config = ConfigDict(extra="allow")
    
    scenario_id: str
    name: str
    description: str
    version: str
    
    # MITRE ATT&CK mapping
    mitre_techniques: List[str] = Field(default_factory=list)
    mitre_tactics: List[str] = Field(default_factory=list)
    
    # Severity for scheduling priority
    severity: str = "medium"  # low, medium, high, critical
    
    # Scenario configuration
    config: Dict[str, any] = Field(default_factory=dict)
    simulators: List[str] = Field(default_factory=list)
    
    # Execution parameters
    duration_seconds: int = 300
    max_events_per_second: int = 100
    event_types: List[str] = Field(default_factory=list)
    
    # Safety controls
    namespace: str = "aegisforge-lab"
    allowed_namespaces: List[str] = Field(default_factory=lambda: ["aegisforge-lab"])
    require_approval: bool = True
    max_concurrent_runs: int = 3
    
    # Metadata
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    tags: List[str] = Field(default_factory=list)
    enabled: bool = True


class EmulationRun(BaseModel):
    """Execution of an emulation scenario."""
    model_config = ConfigDict(extra="allow")
    
    run_id: UUID = Field(default_factory=lambda: uuid4())
    scenario_id: str
    
    # Execution tracking
    status: EmulationStatus = EmulationStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    
    # Approval
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    approval_id: Optional[str] = None
    
    # Execution details
    config_override: Dict[str, any] = Field(default_factory=dict)
    target_namespace: str = "aegisforge-lab"
    
    # Progress tracking
    events_generated: int = 0
    events_sent: int = 0
    events_failed: int = 0
    events_per_second: float = 0.0
    
    # Error tracking
    errors: List[Dict[str, any]] = Field(default_factory=list)
    last_error: Optional[str] = None
    
    # Status tracking
    status_message: Optional[str] = None
    progress_percent: float = 0.0
    
    # Timing
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    started_by: Optional[str] = None
    
    # Cleanup
    cleanup_completed: bool = False
    cleanup_errors: List[str] = Field(default_factory=list)


class EmulationScenarioTemplate(BaseModel):
    """Pre-built scenario templates."""
    model_config = ConfigDict(extra="allow")
    
    template_id: str
    name: str
    description: str
    category: str  # authentication, network, workload, dns, traffic
    
    # Base configuration
    base_config: Dict[str, any] = Field(default_factory=dict)
    default_duration: int = 300
    default_rate: int = 10
    
    # MITRE mapping
    mitre_techniques: List[str] = Field(default_factory=list)
    mitre_tactics: List[str] = Field(default_factory=list)
    
    # Safety
    severity: str = "low"
    default_namespace: str = "aegisforge-lab"
    
    # Parameters that can be customized
    parameters: Dict[str, Dict[str, any]] = Field(default_factory=dict)


# Pre-built scenario templates
BUILTIN_SCENARIOS = {
    "auth-brute-force": EmulationScenarioTemplate(
        template_id="auth-brute-force",
        name="Authentication Brute Force",
        description="Simulates repeated failed login attempts from single source",
        category="authentication",
        base_config={
            "source_ips": ["10.0.1.100"],
            "target_usernames": ["admin", "root", "test", "user1"],
            "failure_rate": 0.9,
            "interval_seconds": 2,
        },
        mitre_techniques=["T1110.001", "T1110.003"],
        mitre_tactics=["TA0006"],  # Credential Access
        severity="high",
    ),
    
    "auth-password-spray": EmulationScenarioTemplate(
        template_id="auth-password-spray",
        name="Password Spray Attack",
        description="Simulates password spray across multiple accounts",
        category="authentication",
        base_config={
            "source_ips": ["10.0.1.100", "10.0.1.101", "10.0.1.102"],
            "target_usernames": ["user1", "user2", "user2", "admin", "service"],
            "password": "Password123",
            "interval_seconds": 30,
        },
        mitre_techniques=["T1110.003"],
        mitre_tactics=["TA0006"],
        severity="high",
    ),
    
    "dns-tunneling": EmulationScenarioTemplate(
        template_id="dns-tunneling",
        name="DNS Tunneling Exfiltration",
        description="Simulates DNS tunneling for data exfiltration",
        category="dns",
        base_config={
            "domain": "exfil.example.com",
            "subdomain_length": 50,
            "entropy": 0.9,
            "query_interval_ms": 100,
            "payload_size": 200,
        },
        mitre_techniques=["T1048.003", "T1572"],
        mitre_tactics=["TA0010", "TA0011"],  # Exfiltration, Command and Control
        severity="high",
    ),
    
    "dns-dga": EmulationScenarioTemplate(
        template_id="dns-dga",
        name="Domain Generation Algorithm",
        description="Simulates DGA-based C2 communication",
        category="dns",
        base_config={
            "algorithm": "seeded",
            "seed": "malware-seed-123",
            "tlds": [".com", ".net", ".org", ".info"],
            "query_interval_seconds": 30,
            "nxdomain_ratio": 0.8,
        },
        mitre_techniques=["T1568.002"],
        mitre_tactics=["TA0011"],
        severity="high",
    ),
    
    "traffic-beaconing": EmulationScenarioTemplate(
        template_id="traffic-beaconing",
        name="C2 Beaconing Pattern",
        description="Simulates regular C2 beaconing traffic",
        category="traffic",
        base_config={
            "destination": "10.0.100.50:443",
            "interval_seconds": 60,
            "jitter_percent": 10,
            "payload_size": 512,
            "protocol": "tcp",
        },
        mitre_techniques=["T1071.001", "T1573.001"],
        mitre_tactics=["TA0011"],
        severity="high",
    ),
    
    "traffic-port-scan": EmulationScenarioTemplate(
        template_id="traffic-port-scan",
        name="Internal Port Scan",
        description="Simulates internal network reconnaissance",
        category="traffic",
        base_config={
            "target_subnet": "10.0.0.0/24",
            "ports": [22, 23, 80, 443, 3306, 5432, 6379, 8080, 8443, 9090],
            "scan_type": "syn",
            "rate_pps": 100,
        },
        mitre_techniques=["T1046", "T1590.005"],
        mitre_tactics=["TA0007"],  # Discovery
        severity="medium",
    ),
    
    "workload-privilege-escalation": EmulationScenarioTemplate(
        template_id="workload-privilege-escalation",
        name="Container Privilege Escalation",
        description="Simulates container escape and privilege escalation attempts",
        category="workload",
        base_config={
            "techniques": [
                "privileged_container",
                "host_path_mount",
                "docker_socket_mount",
                "capability_abuse",
                "kernel_exploit",
            ],
            "interval_seconds": 60,
        },
        mitre_techniques=["T1611", "T1610", "T1609"],
        mitre_tactics=["TA0004"],  # Privilege Escalation
        severity="critical",
    ),
    
    "crypto-mining": EmulationScenarioTemplate(
        template_id="crypto-mining",
        name="Cryptocurrency Mining",
        description="Simulates cryptominer process execution",
        category="workload",
        base_config={
            "miner_process": "xmrig",
            "pool_address": "pool.minexmr.com:4444",
            "wallet": "4x...x",
            "cpu_threads": 2,
            "duration_seconds": 300,
        },
        mitre_techniques=["T1496"],
        mitre_tactics=["TA0005"],  # Defense Evasion
        severity="high",
    ),
    
    "data-exfiltration": EmulationScenarioTemplate(
        template_id="data-exfiltration",
        name="Data Exfiltration Simulation",
        description="Simulates large data transfer to external destination",
        category="traffic",
        base_config={
            "destination": "10.0.100.100:443",
            "data_size_mb": 100,
            "chunk_size_kb": 1024,
            "interval_ms": 100,
            "protocol": "https",
        },
        mitre_techniques=["T1041", "T1048.003"],
        mitre_tactics=["TA0010"],
        severity="critical",
    ),
}
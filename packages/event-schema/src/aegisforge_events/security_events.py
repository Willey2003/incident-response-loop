"""
Security event models for AegisForge platform.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, ConfigDict

from .base import BaseEvent, EventMetadata, EventSeverity


class AuthEventType(str, Enum):
    """Authentication event types."""
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILED = "login_failed"
    LOGOUT = "logout"
    SESSION_CREATED = "session_created"
    SESSION_DESTROYED = "session_destroyed"
    PASSWORD_CHANGE = "password_change"
    MFA_CHALLENGE = "mfa_challenge"
    MFA_SUCCESS = "mfa_success"
    MFA_FAILED = "mfa_failed"
    ACCOUNT_LOCKED = "account_locked"
    ACCOUNT_UNLOCKED = "account_unlocked"
    TOKEN_ISSUED = "token_issued"
    TOKEN_REFRESHED = "token_refreshed"
    TOKEN_REVOKED = "token_revoked"
    PERMISSION_DENIED = "permission_denied"
    PRIVILEGE_ESCALATION = "privilege_escalation"


class AuthEvent(BaseEvent):
    """Authentication and authorization events."""
    event_type: AuthEventType
    user_id: Optional[str] = None
    username: Optional[str] = None
    source_ip: Optional[str] = None
    user_agent: Optional[str] = None
    target_resource: Optional[str] = None
    permissions: List[str] = Field(default_factory=list)
    roles: List[str] = Field(default_factory=list)
    success: bool = True
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    session_id: Optional[str] = None
    mfa_method: Optional[str] = None
    geolocation: Optional[Dict[str, Any]] = None


class NetworkEventType(str, Enum):
    """Network event types."""
    CONNECTION_ESTABLISHED = "connection_established"
    CONNECTION_CLOSED = "connection_closed"
    CONNECTION_FAILED = "connection_failed"
    DNS_QUERY = "dns_query"
    DNS_RESPONSE = "dns_response"
    HTTP_REQUEST = "http_request"
    HTTP_RESPONSE = "http_response"
    TLS_HANDSHAKE = "tls_handshake"
    PORT_SCAN = "port_scan"
    UNUSUAL_PORT = "unusual_port"
    LARGE_TRANSFER = "large_transfer"
    UNUSUAL_PROTOCOL = "unusual_protocol"
    SUSPICIOUS_PATTERN = "suspicious_pattern"
    BEACONING = "beaconing"
    DATA_EXFILTRATION = "data_exfiltration"
    LATERAL_MOVEMENT = "lateral_movement"
    C2_COMMUNICATION = "c2_communication"


class NetworkEvent(BaseEvent):
    """Network traffic and connection events."""
    event_type: NetworkEventType
    source_ip: str
    source_port: Optional[int] = None
    destination_ip: str
    destination_port: Optional[int] = None
    protocol: str = "tcp"
    bytes_sent: int = 0
    bytes_received: int = 0
    packets_sent: int = 0
    packets_received: int = 0
    duration_ms: Optional[int] = None
    flags: List[str] = Field(default_factory=list)
    tls_version: Optional[str] = None
    tls_cipher: Optional[str] = None
    sni: Optional[str] = None
    http_method: Optional[str] = None
    http_path: Optional[str] = None
    http_status: Optional[int] = None
    http_user_agent: Optional[str] = None
    dns_query: Optional[str] = None
    dns_answer: Optional[str] = None
    dns_query_type: Optional[str] = None
    process_id: Optional[int] = None
    process_name: Optional[str] = None
    container_id: Optional[str] = None
    pod_name: Optional[str] = None
    namespace: Optional[str] = None


class ProcessEventType(str, Enum):
    """Process execution event types."""
    PROCESS_START = "process_start"
    PROCESS_END = "process_end"
    PROCESS_FORK = "process_fork"
    PROCESS_EXEC = "process_exec"
    SHELL_SPAWN = "shell_spawn"
    SCRIPT_EXECUTION = "script_execution"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    SUID_EXECUTION = "suid_execution"
    SUDO_EXECUTION = "sudo_execution"
    CONTAINER_ESCAPE = "container_escape"
    KERNEL_MODULE_LOAD = "kernel_module_load"
    SYSCALL_ANOMALY = "syscall_anomaly"


class ProcessEvent(BaseEvent):
    """Process execution and lifecycle events."""
    event_type: ProcessEventType
    pid: int
    ppid: Optional[int] = None
    process_name: str
    command_line: str
    user: str
    group: str
    working_directory: Optional[str] = None
    environment_variables: Dict[str, str] = Field(default_factory=dict)
    executable_path: Optional[str] = None
    executable_hash: Optional[str] = None
    parent_process_name: Optional[str] = None
    parent_command_line: Optional[str] = None
    container_id: Optional[str] = None
    pod_name: Optional[str] = None
    namespace: Optional[str] = None
    capabilities: List[str] = Field(default_factory=list)
    seccomp_profile: Optional[str] = None
    exit_code: Optional[int] = None
    duration_ms: Optional[int] = None
    cpu_time_ms: Optional[int] = None
    memory_bytes: Optional[int] = None


class FileEventType(str, Enum):
    """File system event types."""
    FILE_CREATE = "file_create"
    FILE_MODIFY = "file_modify"
    FILE_DELETE = "file_delete"
    FILE_RENAME = "file_rename"
    FILE_PERMISSION_CHANGE = "file_permission_change"
    FILE_OWNERSHIP_CHANGE = "file_ownership_change"
    SENSITIVE_FILE_ACCESS = "sensitive_file_access"
    CONFIG_FILE_CHANGE = "config_file_change"
    BINARY_FILE_WRITE = "binary_file_write"
    SCRIPT_FILE_WRITE = "script_file_write"
    CRON_JOB_MODIFY = "cron_job_modify"
    SYSTEM_FILE_MODIFY = "system_file_modify"
    LOG_FILE_MODIFY = "log_file_modify"


class FileEvent(BaseEvent):
    """File system access and modification events."""
    event_type: FileEventType
    file_path: str
    file_name: str
    file_extension: Optional[str] = None
    file_size: Optional[int] = None
    file_hash: Optional[str] = None
    file_permissions: Optional[str] = None
    file_owner: Optional[str] = None
    file_group: Optional[str] = None
    operation: str
    process_id: Optional[int] = None
    process_name: Optional[str] = None
    user: Optional[str] = None
    container_id: Optional[str] = None
    pod_name: Optional[str] = None
    namespace: Optional[str] = None
    is_sensitive: bool = False
    sensitivity_reason: Optional[str] = None


class ContainerEventType(str, Enum):
    """Container lifecycle and security event types."""
    CONTAINER_CREATE = "container_create"
    CONTAINER_START = "container_start"
    CONTAINER_STOP = "container_stop"
    CONTAINER_RESTART = "container_restart"
    CONTAINER_DELETE = "container_delete"
    CONTAINER_PAUSE = "container_pause"
    CONTAINER_UNPAUSE = "container_unpause"
    IMAGE_PULL = "image_pull"
    IMAGE_PUSH = "image_push"
    IMAGE_BUILD = "image_build"
    IMAGE_SCAN = "image_scan"
    PRIVILEGED_CONTAINER = "privileged_container"
    HOST_NETWORK = "host_network"
    HOST_PID = "host_pid"
    HOST_IPC = "host_ipc"
    CAPABILITY_ADDED = "capability_added"
    CAPABILITY_DROPPED = "capability_dropped"
    MOUNT_SENSITIVE = "mount_sensitive"
    MOUNT_HOST_PATH = "mount_host_path"
    MOUNT_DOCKER_SOCKET = "mount_docker_socket"
    SECCOMP_VIOLATION = "seccomp_violation"
    APPARMOR_VIOLATION = "apparmor_violation"
    SELINUX_VIOLATION = "selinux_violation"


class ContainerEvent(BaseEvent):
    """Container lifecycle and security events."""
    event_type: ContainerEventType
    container_id: str
    container_name: str
    image_name: str
    image_tag: Optional[str] = None
    image_digest: Optional[str] = None
    image_registry: Optional[str] = None
    runtime: Optional[str] = None
    privileged: bool = False
    host_network: bool = False
    host_pid: bool = False
    host_ipc: bool = False
    capabilities_added: List[str] = Field(default_factory=list)
    capabilities_dropped: List[str] = Field(default_factory=list)
    volumes: List[Dict[str, Any]] = Field(default_factory=list)
    ports: List[Dict[str, Any]] = Field(default_factory=list)
    environment_variables: Dict[str, str] = Field(default_factory=dict)
    labels: Dict[str, str] = Field(default_factory=dict)
    annotations: Dict[str, str] = Field(default_factory=dict)
    pod_name: Optional[str] = None
    namespace: Optional[str] = None
    node_name: Optional[str] = None
    service_account: Optional[str] = None
    image_scan_result: Optional[Dict[str, Any]] = None


class KubernetesEventType(str, Enum):
    """Kubernetes resource event types."""
    RESOURCE_CREATE = "resource_create"
    RESOURCE_UPDATE = "resource_update"
    RESOURCE_DELETE = "resource_delete"
    RESOURCE_PATCH = "resource_patch"
    POD_SCHEDULE = "pod_schedule"
    POD_EVICT = "pod_evict"
    POD_FAILED = "pod_failed"
    POD_OOM_KILLED = "pod_oom_killed"
    DEPLOYMENT_ROLLOUT = "deployment_rollout"
    DEPLOYMENT_SCALE = "deployment_scale"
    SERVICE_ACCOUNT_CREATE = "service_account_create"
    SERVICE_ACCOUNT_TOKEN_CREATE = "service_account_token_create"
    ROLE_BINDING_CREATE = "role_binding_create"
    ROLE_BINDING_DELETE = "role_binding_delete"
    NETWORK_POLICY_CREATE = "network_policy_create"
    NETWORK_POLICY_DELETE = "network_policy_delete"
    RESOURCE_QUOTA_EXCEEDED = "resource_quota_exceeded"
    LIMIT_RANGE_EXCEEDED = "limit_range_exceeded"
    ADMISSION_DENIED = "admission_denied"
    RBAC_ESCALATION = "rbac_escalation"


class KubernetesEvent(BaseEvent):
    """Kubernetes resource lifecycle and security events."""
    event_type: KubernetesEventType
    resource_type: str
    resource_name: str
    namespace: Optional[str] = None
    resource_uid: Optional[str] = None
    api_version: Optional[str] = None
    operation: str
    user: Optional[str] = None
    user_groups: List[str] = Field(default_factory=list)
    source_ip: Optional[str] = None
    user_agent: Optional[str] = None
    object_ref: Optional[Dict[str, Any]] = None
    old_object: Optional[Dict[str, Any]] = None
    new_object: Optional[Dict[str, Any]] = None
    admission_controller: Optional[str] = None
    admission_decision: Optional[str] = None
    labels: Dict[str, str] = Field(default_factory=dict)
    annotations: Dict[str, str] = Field(default_factory=dict)


class DNSEventType(str, Enum):
    """DNS event types."""
    DNS_QUERY = "dns_query"
    DNS_RESPONSE = "dns_response"
    DNS_TUNNELING = "dns_tunneling"
    DNS_EXFILTRATION = "dns_exfiltration"
    DNS_HIJACKING = "dns_hijacking"
    DNS_CACHE_POISONING = "dns_cache_poisoning"
    DGA_DETECTED = "dga_detected"
    FAST_FLUX = "fast_flux"
    DOMAIN_GENERATION = "domain_generation"
    SUSPICIOUS_TLD = "suspicious_tld"
    LONG_SUBDOMAIN = "long_subdomain"
    HIGH_ENTROPY_SUBDOMAIN = "high_entropy_subdomain"
    NXDOMAIN_FLOOD = "nxdomain_flood"
    DNS_AMP = "dns_amplification"


class DNSEvent(BaseEvent):
    """DNS query and anomaly events."""
    event_type: DNSEventType
    query_name: str
    query_type: str
    query_class: str = "IN"
    response_code: Optional[str] = None
    answers: List[Dict[str, Any]] = Field(default_factory=list)
    answer_count: int = 0
    authority_count: int = 0
    additional_count: int = 0
    query_time_ms: Optional[int] = None
    source_ip: str
    source_port: Optional[int] = None
    destination_ip: str
    destination_port: int = 53
    protocol: str = "udp"
    ttl: Optional[int] = None
    flags: List[str] = Field(default_factory=list)
    edns: bool = False
    dnssec: bool = False
    entropy_score: Optional[float] = None
    subdomain_count: Optional[int] = None
    max_subdomain_length: Optional[int] = None
    suspicious_patterns: List[str] = Field(default_factory=list)
    container_id: Optional[str] = None
    pod_name: Optional[str] = None
    namespace: Optional[str] = None


class TrafficEventType(str, Enum):
    """Network traffic pattern event types."""
    TRAFFIC_SPIKE = "traffic_spike"
    TRAFFIC_DROP = "traffic_drop"
    UNUSUAL_PROTOCOL = "unusual_protocol"
    UNUSUAL_PORT = "unusual_port"
    BEACONING_PATTERN = "beaconing_pattern"
    PORT_SCAN = "port_scan"
    NETWORK_SCAN = "network_scan"
    LATERAL_MOVEMENT = "lateral_movement"
    DATA_EXFILTRATION = "data_exfiltration"
    C2_PATTERN = "c2_pattern"
    ENCRYPTED_TRAFFIC_SPIKE = "encrypted_traffic_spike"
    TOR_TRAFFIC = "tor_traffic"
    VPN_TRAFFIC = "vpn_traffic"
    PROXY_TRAFFIC = "proxy_traffic"
    P2P_TRAFFIC = "p2p_traffic"
    CRYPTO_MINING = "crypto_mining"


class TrafficEvent(BaseEvent):
    """Network traffic pattern and anomaly events."""
    event_type: TrafficEventType
    source_ip: str
    destination_ip: str
    source_port: Optional[int] = None
    destination_port: Optional[int] = None
    protocol: str
    bytes_total: int
    packets_total: int
    connections_count: int
    unique_sources: int
    unique_destinations: int
    unique_ports: int
    time_window_seconds: int
    avg_packet_size: Optional[float] = None
    entropy_score: Optional[float] = None
    patterns_detected: List[str] = Field(default_factory=list)
    mitre_techniques: List[str] = Field(default_factory=list)
    confidence_score: Optional[float] = None
    namespace: Optional[str] = None
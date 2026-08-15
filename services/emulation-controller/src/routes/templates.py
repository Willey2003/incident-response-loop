"""
Emulation templates routes.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..auth import get_current_user, require_analyst
from ..config import settings

router = APIRouter()


@router.get("/templates", response_model=List[dict])
async def list_templates(
    current_user = Depends(require_analyst),
):
    """List built-in scenario templates."""
    return [
        {
            "template_id": "auth-brute-force",
            "name": "Authentication Brute Force",
            "description": "Simulates repeated failed login attempts from single source",
            "category": "authentication",
            "mitre_techniques": ["T1110.001", "T1110.003"],
            "mitre_tactics": ["TA0006"],
            "severity": "high",
        },
        {
            "template_id": "auth-password-spray",
            "name": "Password Spray Attack",
            "description": "Simulates password spray across multiple accounts",
            "category": "authentication",
            "mitre_techniques": ["T1110.003"],
            "mitre_tactics": ["TA0006"],
            "severity": "high",
        },
        {
            "template_id": "dns-tunneling",
            "name": "DNS Tunneling Exfiltration",
            "description": "Simulates DNS tunneling for data exfiltration",
            "category": "dns",
            "mitre_techniques": ["T1048.003", "T1572"],
            "mitre_tactics": ["TA0010", "TA0011"],
            "severity": "high",
        },
        {
            "template_id": "dns-dga",
            "name": "Domain Generation Algorithm",
            "description": "Simulates DGA-based C2 communication",
            "category": "dns",
            "mitre_techniques": ["T1568.002"],
            "mitre_tactics": ["TA0011"],
            "severity": "high",
        },
        {
            "template_id": "traffic-beaconing",
            "name": "C2 Beaconing Pattern",
            "description": "Simulates regular C2 beaconing traffic",
            "category": "traffic",
            "mitre_techniques": ["T1071.001", "T1573.001"],
            "mitre_tactics": ["TA0011"],
            "severity": "high",
        },
        {
            "template_id": "traffic-port-scan",
            "name": "Internal Port Scan",
            "description": "Simulates internal network reconnaissance",
            "category": "traffic",
            "mitre_techniques": ["T1046", "T1590.005"],
            "mitre_tactics": ["TA0007"],
            "severity": "medium",
        },
        {
            "template_id": "workload-privilege-escalation",
            "name": "Container Privilege Escalation",
            "description": "Simulates container escape and privilege escalation attempts",
            "category": "workload",
            "mitre_techniques": ["T1611", "T1610", "T1609"],
            "mitre_tactics": ["TA0004"],
            "severity": "critical",
        },
        {
            "template_id": "crypto-mining",
            "name": "Cryptocurrency Mining",
            "description": "Simulates cryptominer process execution",
            "category": "workload",
            "mitre_techniques": ["T1496"],
            "mitre_tactics": ["TA0005"],
            "severity": "high",
        },
        {
            "template_id": "data-exfiltration",
            "name": "Data Exfiltration Simulation",
            "description": "Simulates large data transfer to external destination",
            "category": "traffic",
            "mitre_techniques": ["T1041", "T1048.003"],
            "mitre_tactics": ["TA0010"],
            "severity": "critical",
        },
    ]
"""
Workload event generator for Workload Simulator.
Generates simulated process execution and policy violation events.
"""

import asyncio
import random
import time
from datetime import datetime
from typing import List, Dict, Any

from .config import settings
from .kafka import get_producer

import structlog

logger = structlog.get_logger()


class WorkloadEventGenerator:
    """Generates simulated process execution and policy violation events."""
    
    def __init__(self):
        self.producer = None
        self.running = False
        self.interval = settings.SIMULATOR_INTERVAL
        self.batch_size = settings.SIMULATOR_BATCH_SIZE
        
        # Event types
        self.process_events = [
            "process_start", "process_end", "process_fork", "process_exec",
            "shell_spawn", "script_execution", "privilege_escalation",
            "suid_execution", "sudo_execution", "container_escape",
        ]
        
        # Suspicious process names
        self.suspicious_processes = [
            "xmrig", "minergate", "cryptonight", "monero",
            "nmap", "masscan", "zmap", "sqlmap", "metasploit",
            "mimikatz", "sekurlsa", "lsass", "pwdump",
            "nc", "netcat", "socat", "bash", "sh", "powershell",
        ]
        
        # Legitimate processes
        self.legitimate_processes = [
            "nginx", "apache", "postgres", "mysql", "redis",
            "python", "node", "java", "go", "kubectl",
            "sshd", "systemd", "cron", "systemd-journald",
        ]
    
    async def initialize(self):
        """Initialize the generator."""
        from .kafka import get_producer
        self.producer = get_producer()
        logger.info("Workload event generator initialized")
    
    async def start(self):
        """Start the generator."""
        self.running = True
        logger.info("Workload event generator started")
    
    async def stop(self):
        """Stop the generator."""
        self.running = False
        logger.info("Workload event generator stopped")
    
    async def run(self):
        """Main generation loop."""
        await self.initialize()
        await self.start()
        
        logger.info("Starting workload event generation", interval=self.interval)
        
        while self.running:
            try:
                await self.generate_batch()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Error generating events", error=str(e))
            
            await asyncio.sleep(self.interval)
        
        logger.info("Workload event generator stopped")
    
    async def generate_batch(self):
        """Generate a batch of workload events."""
        if not self.running:
            return
        
        events = []
        
        for _ in range(self.batch_size):
            event = self.generate_workload_event()
            events.append(event)
        
        # Send to Kafka
        await self.send_events(events)
        
        logger.debug("Generated workload event batch", count=len(events))
    
    def generate_workload_event(self) -> Dict:
        """Generate a single workload event."""
        # Choose event type
        event_type = random.choice(self.process_events)
        
        # Determine if suspicious
        is_suspicious = random.random() < 0.3  # 30% suspicious
        
        if is_suspicious:
            process_name = random.choice(self.suspicious_processes)
            severity = random.choice(["medium", "high", "critical"])
        else:
            process_name = random.choice(self.legitimate_processes)
            severity = "info"
        
        # Generate event
        event = {
            "event_id": self._generate_event_id(),
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": "workload-simulator",
            "source_type": "simulator",
            "pid": random.randint(1, 65535),
            "ppid": random.randint(1, 65535),
            "process_name": process_name,
            "command_line": self._generate_command_line(process_name),
            "user": random.choice(["root", "www-data", "nginx", "postgres", "redis", "appuser"]),
            "group": "root",
            "working_directory": random.choice(["/tmp", "/home/user", "/var/www", "/opt/app", "/"]),
            "executable_path": f"/usr/bin/{process_name}",
            "executable_hash": self._generate_hash(),
            "container_id": self._generate_container_id(),
            "pod_name": f"pod-{random.randint(1000, 9999)}",
            "namespace": "aegisforge-lab",
            "capabilities": [],
            "severity": severity,
        }
        
        # Add suspicious-specific fields
        if "suspicious" in str(severity).lower() or severity in ["medium", "high", "critical"]:
            event["capabilities"] = random.sample(
                ["CAP_SYS_ADMIN", "CAP_NET_RAW", "CAP_SYS_PTRACE", "CAP_DAC_OVERRIDE", "CAP_SYS_MODULE"],
                random.randint(1, 3)
            )
            event["privileged"] = random.random() < 0.3
        
        return event
    
    def _generate_event_id(self) -> str:
        import time
        return f"evt-{int(time.time() * 1000000)}-{random.randint(1000, 9999)}"
    
    def _generate_hash(self) -> str:
        import hashlib
        return hashlib.sha256(str(random.random()).encode()).hexdigest()[:64]
    
    def _generate_container_id(self) -> str:
        return "".join(random.choices("0123456789abcdef", k=64))
    
    def _generate_command_line(self, process_name: str) -> str:
        args = {
            "nginx": ["nginx", "-g", "daemon off;"],
            "apache": ["apache2", "-D", "FOREGROUND"],
            "postgres": ["postgres", "-D", "/var/lib/postgresql/data"],
            "mysql": ["mysqld"],
            "redis": ["redis-server"],
            "python": ["python", "app.py"],
            "node": ["node", "server.js"],
            "java": ["java", "-jar", "app.jar"],
            "kubectl": ["kubectl", "get", "pods"],
            "xmrig": ["xmrig", "-o", "pool.minexmr.com:4444", "-u", "wallet"],
            "nmap": ["nmap", "-sS", "10.0.0.0/24"],
            "bash": ["bash", "-c", "whoami"],
            "sh": ["sh", "-c", "id"],
            "powershell": ["powershell", "-Command", "Get-Process"],
        }
        return " ".join(args.get(process_name, [process_name]))
    
    async def send_events(self, events: List[Dict]):
        """Send events to Kafka."""
        from .kafka import get_producer
        
        producer = get_producer()
        if not producer:
            return
        
        try:
            for event in events:
                await producer.send_and_wait(
                    "security-events",
                    value=event,
                    key=event.get("container_id", "").encode(),
                )
        except Exception as e:
            import structlog
            logger = structlog.get_logger()
            logger.error("Failed to send events to Kafka", error=str(e))
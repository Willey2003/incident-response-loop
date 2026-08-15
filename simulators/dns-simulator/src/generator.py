"""
DNS event generator for DNS Simulator.
Generates synthetic DNS anomaly events.
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


class DNSEventGenerator:
    """Generates synthetic DNS anomaly events."""
    
    def __init__(self):
        self.producer = None
        self.running = False
        self.interval = settings.SIMULATOR_INTERVAL
        self.batch_size = settings.SIMULATOR_BATCH_SIZE
        
        # DNS event types
        self.dns_events = [
            "dns_query", "dns_response", "dns_tunneling", "dns_exfiltration",
            "dns_hijacking", "dns_cache_poisoning", "dga_detected",
            "fast_flux", "domain_generation", "suspicious_tld",
            "long_subdomain", "high_entropy_subdomain", "nxdomain_flood",
            "dns_amplification",
        ]
        
        # Legitimate domains
        self.legitimate_domains = [
            "google.com", "github.com", "microsoft.com", "amazon.com",
            "kubernetes.io", "docker.io", "github.io", "cloudflare.com",
            "ubuntu.com", "debian.org", "redhat.com", "centos.org",
        ]
        
        # Suspicious domains for DGA/tunneling
        self.suspicious_tlds = [".tk", ".ml", ".ga", ".cf", ".gq", ".xyz", ".top", ".club", ".work", ".info"]
        self.dga_seeds = ["malware-seed-1", "malware-seed-2", "botnet-seed", "c2-seed"]
        
        # DNS record types
        self.record_types = ["A", "AAAA", "CNAME", "MX", "TXT", "NS", "SOA", "PTR"]
        
        # DNS response codes
        self.response_codes = ["NOERROR", "NXDOMAIN", "SERVFAIL", "REFUSED", "FORMERR"]
    
    async def initialize(self):
        """Initialize the generator."""
        from .kafka import get_producer
        self.producer = get_producer()
        logger.info("DNS event generator initialized")
    
    async def start(self):
        """Start the generator."""
        self.running = True
        logger.info("DNS event generator started")
    
    async def stop(self):
        """Stop the generator."""
        self.running = False
        logger.info("DNS event generator stopped")
    
    async def run(self):
        """Main generation loop."""
        from .kafka import get_producer
        self.producer = get_producer()
        self.running = True
        
        logger.info("Starting DNS event generation")
        
        while self.running:
            try:
                await self.generate_batch()
            except asyncio.CancelledError:
                break
            except Exception as e:
                import structlog
                logger = structlog.get_logger()
                logger.error("Error generating events", error=str(e))
            
            await asyncio.sleep(self.interval)
        
        logger.info("DNS event generator stopped")
    
    async def generate_batch(self):
        """Generate a batch of DNS events."""
        if not self.running:
            return
        
        events = []
        
        for _ in range(self.batch_size):
            event = self.generate_dns_event()
            events.append(event)
        
        # Send to Kafka
        await self.send_events(events)
        
        import structlog
        logger = structlog.get_logger()
        logger.debug("Generated DNS event batch", count=len(events))
    
    def generate_dns_event(self) -> Dict:
        """Generate a single DNS event."""
        # Choose event type
        event_type = random.choice(self.dns_events)
        
        # Determine if suspicious
        is_suspicious = event_type in [
            "dns_tunneling", "dns_exfiltration", "dns_hijacking", 
            "dns_cache_poisoning", "dga_detected", "fast_flux",
            "domain_generation", "suspicious_tld", "long_subdomain",
            "high_entropy_subdomain", "nxdomain_flood", "dns_amplification"
        ]
        
        # Generate event
        event = {
            "event_id": self._generate_event_id(),
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": "dns-simulator",
            "source_type": "simulator",
            "query_name": self._generate_query_name(event_type),
            "query_type": random.choice(self.record_types),
            "query_class": "IN",
            "response_code": random.choice(self.response_codes),
            "answers": [],
            "answer_count": 0,
            "authority_count": 0,
            "additional_count": 0,
            "query_time_ms": random.randint(1, 100),
            "source_ip": self._generate_source_ip(),
            "source_port": random.randint(1024, 65535),
            "destination_ip": "10.0.0.10",  # DNS server
            "destination_port": 53,
            "protocol": random.choice(["udp", "tcp"]),
            "ttl": random.randint(60, 86400),
            "flags": [],
            "edns": random.random() < 0.8,
            "dnssec": random.random() < 0.3,
        }
        
        # Add suspicious-specific fields
        if event_type in ["dns_tunneling", "dns_exfiltration"]:
            event["entropy_score"] = round(random.uniform(0.8, 1.0), 2)
            event["subdomain_count"] = random.randint(10, 50)
            event["max_subdomain_length"] = random.randint(50, 100)
            event["suspicious_patterns"] = ["high_entropy", "long_subdomain", "base64_encoded"]
        
        if event_type == "dga_detected":
            event["entropy_score"] = round(random.uniform(0.7, 0.95), 2)
            event["subdomain_count"] = random.randint(5, 20)
            event["max_subdomain_length"] = random.randint(20, 50)
            event["suspicious_patterns"] = ["dga_pattern", "algorithmic_domain"]
        
        if event_type == "nxdomain_flood":
            event["response_code"] = "NXDOMAIN"
            event["suspicious_patterns"] = ["nxdomain_flood", "reconnaissance"]
        
        return event
    
    def _generate_source_ip(self) -> str:
        # Mix of internal and external IPs
        if random.random() < 0.7:
            return f"10.0.{random.randint(1, 255)}.{random.randint(1, 255)}"
        else:
            return f"{random.randint(1, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"
    
    def _generate_query_name(self, event_type: str) -> str:
        if "tunneling" in event_type or "exfiltration" in event_type:
            # High entropy subdomain for tunneling
            import base64
            data = "x" * random.randint(50, 200)
            encoded = base64.b64encode(data.encode()).decode().rstrip('=')
            return f"{encoded}.tunnel.example.com"
        elif event_type == "dga_detected":
            # Algorithmic domain
            seed = random.choice(self.dga_seeds)
            domain = f"{seed}-{random.randint(1000,9999)}"
            tld = random.choice([".com", ".net", ".org", ".info", ".biz"])
            return f"{domain}{tld}"
        elif "suspicious_tld" in event_type or "tld" in event_type:
            domain = f"malicious-{random.randint(1000,9999)}"
            tld = random.choice(self.suspicious_tlds)
            return f"{domain}{tld}"
        elif "long_subdomain" in event_type:
            sub = "x" * random.randint(50, 100)
            return f"{sub}.example.com"
        elif "high_entropy" in event_type:
            import base64
            data = "x" * random.randint(60, 80)
            encoded = base64.b64encode(data.encode()).decode().rstrip('=')
            return f"{encoded}.evil.com"
        else:
            # Legitimate domain
            return random.choice(self.legitimate_domains)
    
    def _generate_event_id(self) -> str:
        return f"evt-{int(time.time() * 1000000)}-{random.randint(1000, 9999)}"
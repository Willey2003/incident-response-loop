"""
Traffic event generator for Traffic Simulator.
Generates namespace-local HTTP traffic pattern events.
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


class TrafficEventGenerator:
    """Generates namespace-local HTTP traffic pattern events."""
    
    def __init__(self):
        self.producer = None
        self.running = False
        self.interval = settings.SIMULATOR_INTERVAL
        self.batch_size = settings.SIMULATOR_BATCH_SIZE
        
        # Traffic event types
        self.traffic_events = [
            "traffic_spike", "traffic_drop", "unusual_protocol", "unusual_port",
            "beaconing_pattern", "port_scan", "network_scan", "lateral_movement",
            "data_exfiltration", "c2_pattern", "encrypted_traffic_spike",
            "tor_traffic", "vpn_traffic", "proxy_traffic", "p2p_traffic", "crypto_mining",
        ]
        
        # HTTP methods
        self.http_methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
        
        # HTTP status codes
        self.status_codes = [200, 201, 204, 301, 302, 304, 400, 401, 403, 404, 500, 502, 503]
        
        # User agents
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101",
            "curl/7.68.0",
            "python-requests/2.28.1",
            "go-resty/2.7.0",
            "axios/1.4.0",
            "k8s-client/1.28.0",
        ]
        
        # Paths
        self.paths = [
            "/api/v1/users", "/api/v1/health", "/api/v1/metrics", "/api/v1/login",
            "/api/v1/data", "/api/v1/config", "/api/v1/users/123", "/api/v1/orders",
            "/health", "/ready", "/metrics", "/actuator/health", "/actuator/info",
            "/.well-known/acme-challenge", "/.git/config", "/.env", "/admin",
            "/wp-admin", "/phpmyadmin", "/wp-login.php", "/api/v1/admin",
        ]
    
    async def initialize(self):
        """Initialize the generator."""
        from .kafka import get_producer
        self.producer = get_producer()
        logger.info("Traffic event generator initialized")
    
    async def start(self):
        """Start the generator."""
        self.running = True
        logger.info("Traffic event generator started")
    
    async def stop(self):
        """Stop the generator."""
        self.running = False
        logger.info("Traffic event generator stopped")
    
    async def run(self):
        """Main generation loop."""
        from .kafka import get_producer
        self.producer = get_producer()
        self.running = True
        
        logger.info("Starting traffic event generation")
        
        while self.running:
            try:
                await self.generate_batch()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Error generating events", error=str(e))
            
            await asyncio.sleep(self.interval)
        
        logger.info("Traffic event generator stopped")
    
    async def generate_batch(self):
        """Generate a batch of traffic events."""
        if not self.running:
            return
        
        events = []
        
        for _ in range(self.batch_size):
            event = self.generate_traffic_event()
            events.append(event)
        
        # Send to Kafka
        await self.send_events(events)
        
        logger.debug("Generated traffic event batch", count=len(events))
    
    def generate_traffic_event(self) -> Dict:
        """Generate a single traffic event."""
        # Choose event type
        event_type = random.choice(self.traffic_events)
        
        # Determine if suspicious
        is_suspicious = event_type in [
            "traffic_spike", "unusual_protocol", "unusual_port", "beaconing_pattern",
            "port_scan", "network_scan", "lateral_movement", "data_exfiltration",
            "c2_pattern", "encrypted_traffic_spike", "tor_traffic", "vpn_traffic",
            "proxy_traffic", "p2p_traffic", "crypto_mining",
        ]
        
        # Generate event
        event = {
            "event_id": self._generate_event_id(),
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": "traffic-simulator",
            "source_type": "simulator",
            "source_ip": self._generate_source_ip(),
            "destination_ip": self._generate_destination_ip(),
            "source_port": random.randint(1024, 65535),
            "destination_port": random.choice([80, 443, 8080, 8443, 3000, 5000, 8000, 9090, 22, 3389, 445]),
            "protocol": random.choice(["tcp", "udp", "http", "https", "grpc"]),
            "bytes_total": random.randint(100, 10000000),
            "packets_total": random.randint(1, 10000),
            "connections_count": random.randint(1, 100),
            "unique_sources": random.randint(1, 10),
            "unique_destinations": random.randint(1, 10),
            "unique_ports": random.randint(1, 20),
            "time_window_seconds": random.randint(60, 3600),
            "avg_packet_size": random.uniform(64, 1500),
            "entropy_score": round(random.uniform(0.1, 0.9), 2),
            "patterns_detected": [],
            "mitre_techniques": [],
            "confidence_score": round(random.uniform(0.5, 0.95), 2),
            "namespace": "aegisforge-lab",
        }
        
        # Add HTTP-specific fields
        if random.random() < 0.7:
            event["http_method"] = random.choice(self.http_methods)
            event["http_path"] = random.choice(self.paths)
            event["http_status"] = random.choice(self.status_codes)
            event["user_agent"] = random.choice(self.user_agents)
        
        # Add suspicious-specific fields
        if event_type in ["beaconing_pattern", "c2_pattern"]:
            event["mitre_techniques"] = ["T1071.001", "T1573.001"]
            event["patterns_detected"] = ["regular_interval", "fixed_payload_size", "single_destination"]
            event["entropy_score"] = round(random.uniform(0.1, 0.3), 2)  # Low entropy for beaconing
        
        if event_type in ["port_scan", "network_scan"]:
            event["mitre_techniques"] = ["T1046", "T1590.005"]
            event["patterns_detected"] = ["multiple_ports", "single_source", "rapid_connections"]
            event["entropy_score"] = round(random.uniform(0.5, 0.8), 2)
        
        if event_type in ["data_exfiltration"]:
            event["mitre_techniques"] = ["T1041", "T1048.003"]
            event["patterns_detected"] = ["large_transfer", "unusual_destination", "off_hours"]
            event["bytes_total"] = random.randint(10000000, 1000000000)
            event["entropy_score"] = round(random.uniform(0.7, 0.95), 2)
        
        if event_type in ["lateral_movement"]:
            event["mitre_techniques"] = ["T1021.001", "T1021.002", "T1021.004"]
            event["patterns_detected"] = ["smb_traffic", "admin_shares", "credential_reuse"]
            event["entropy_score"] = round(random.uniform(0.3, 0.6), 2)
        
        if event_type in ["tor_traffic", "vpn_traffic", "proxy_traffic"]:
            event["mitre_techniques"] = ["T1090.001", "T1090.002"]
            event["patterns_detected"] = ["known_exit_node", "encrypted_tunnel", "unusual_geo"]
            event["entropy_score"] = round(random.uniform(0.8, 1.0), 2)
        
        if event_type == "crypto_mining":
            event["mitre_techniques"] = ["T1496"]
            event["patterns_detected"] = ["stratum_protocol", "mining_pool", "high_cpu"]
            event["destination_port"] = random.choice([3333, 4444, 5555, 7777, 9999])
            event["entropy_score"] = round(random.uniform(0.4, 0.7), 2)
        
        return event
    
    def _generate_event_id(self) -> str:
        import time
        return f"evt-{int(time.time() * 1000000)}-{random.randint(1000, 9999)}"
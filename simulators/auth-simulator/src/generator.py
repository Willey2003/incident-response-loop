"""
Auth event generator for Auth Simulator.
Generates controlled authentication events for testing.
"""

import asyncio
import random
import time
from datetime import datetime
from typing import List, Dict, Any
from faker import Faker

from .config import settings
from .kafka import get_producer

import structlog

logger = structlog.get_logger()


class AuthEventGenerator:
    """Generates controlled authentication events."""
    
    def __init__(self):
        self.fake = Faker()
        self.producer = None
        self.running = False
        self.interval = settings.SIMULATOR_INTERVAL
        self.batch_size = settings.SIMULATOR_BATCH_SIZE
        self.mode = settings.SIMULATION_MODE
        
        # Target configuration
        self.target_ips = settings.TARGET_IPS
        self.target_usernames = settings.TARGET_USERNAMES
        self.failure_rate = settings.FAILURE_RATE
        self.interval_seconds = settings.INTERVAL_SECONDS
        
        # Event templates
        self.event_types = {
            "login_success": {
                "event_type": "login_success",
                "severity": "info",
            },
            "login_failed": {
                "event_type": "login_failed",
                "severity": "medium",
            },
            "logout": {
                "event_type": "logout",
                "severity": "info",
            },
            "password_change": {
                "event_type": "password_change",
                "severity": "medium",
            },
            "mfa_challenge": {
                "event_type": "mfa_challenge",
                "severity": "medium",
            },
        }
        
        # Pre-defined passwords for simulation
        self.common_passwords = [
            "password", "password123", "admin123", "root123", "test123",
            "welcome", "qwerty", "letmein", "monkey", "dragon",
            "password1", "admin", "root", "user", "guest",
        ]
    
    async def initialize(self):
        """Initialize the generator."""
        from .kafka import get_producer
        self.producer = get_producer()
        logger.info("Auth event generator initialized")
    
    async def start(self):
        """Start the generator."""
        self.running = True
        logger.info("Auth event generator started")
    
    async def stop(self):
        """Stop the generator."""
        self.running = False
        logger.info("Auth event generator stopped")
    
    async def run(self):
        """Main generation loop."""
        await self.initialize()
        await self.start()
        
        logger.info("Starting auth event generation", mode=self.mode, interval=self.interval)
        
        while self.running:
            try:
                await self.generate_batch()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Error generating events", error=str(e))
            
            await asyncio.sleep(self.interval)
        
        logger.info("Auth event generator stopped")
    
    async def generate_batch(self):
        """Generate a batch of authentication events."""
        if not self.running:
            return
        
        events = []
        
        for _ in range(self.batch_size):
            event = self.generate_auth_event()
            events.append(event)
        
        # Send to Kafka
        await self.send_events(events)
        
        logger.debug("Generated event batch", count=len(events))
    
    def generate_auth_event(self) -> Dict:
        """Generate a single authentication event."""
        # Choose event type based on mode
        if self.mode == "brute_force":
            event_type = "login_failed"
        elif self.mode == "password_spray":
            event_type = random.choice(["login_failed", "login_success"])
        else:  # mixed
            if random.random() < self.failure_rate:
                event_type = "login_failed"
            else:
                event_type = "login_success"
        
        # Generate event
        event_template = self.event_types.get(event_type, self.event_types["login_failed"])
        
        source_ip = random.choice(self.target_ips)
        username = random.choice(self.target_usernames)
        
        event = {
            "event_id": self._generate_event_id(),
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": "auth-simulator",
            "source_type": "simulator",
            "user_id": self._generate_user_id(),
            "username": username,
            "source_ip": source_ip,
            "user_agent": self._generate_user_agent(),
            "target_resource": "auth-service",
            "success": event_type == "login_success",
            "error_code": None if event_type == "login_success" else "AUTH_FAILED",
            "error_message": None if event_type == "login_success" else "Invalid credentials",
            "session_id": self._generate_session_id(),
            "mfa_method": random.choice(["totp", "sms", "push", None]),
            "geolocation": self._generate_geolocation(source_ip),
        }
        
        # Add failure-specific fields
        if event_type == "login_failed":
            event["password_used"] = random.choice(self.common_passwords)
            event["attempt_number"] = random.randint(1, 10)
        
        return event
    
    def _generate_event_id(self) -> str:
        """Generate unique event ID."""
        return f"evt-{int(time.time() * 1000000)}-{random.randint(1000, 9999)}"
    
    def _generate_user_id(self) -> str:
        """Generate user ID."""
        return f"user-{random.randint(1000, 9999)}"
    
    def _generate_session_id(self) -> str:
        """Generate session ID."""
        return f"sess-{int(time.time())}-{random.randint(10000, 99999)}"
    
    def _generate_user_agent(self) -> str:
        """Generate realistic user agent."""
        browsers = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101",
            "curl/7.68.0",
            "python-requests/2.28.1",
        ]
        return random.choice(browsers)
    
    def _generate_geolocation(self, ip: str) -> Dict:
        """Generate geolocation data for IP."""
        # Simplified - in reality would use GeoIP database
        countries = ["US", "CN", "RU", "BR", "IN", "DE", "FR", "GB", "JP", "CA"]
        cities = ["New York", "Beijing", "Moscow", "São Paulo", "Mumbai", "Berlin", "Paris", "London", "Tokyo", "Toronto"]
        
        return {
            "country": random.choice(countries),
            "city": random.choice(cities),
            "latitude": round(random.uniform(-90, 90), 6),
            "longitude": round(random.uniform(-180, 180), 6),
        }
    
    async def send_events(self, events: List[Dict]):
        """Send events to Kafka."""
        from .kafka import get_producer
        
        producer = get_producer()
        if not producer:
            logger.warning("Kafka producer not available")
            return
        
        try:
            for event in events:
                await self._send_event(event)
        except Exception as e:
            logger.error("Failed to send events to Kafka", error=str(e))
    
    async def _send_event(self, event: Dict):
        """Send a single event to Kafka."""
        from .kafka import get_producer
        
        producer = get_producer()
        if not producer:
            return
        
        try:
            await producer.send_and_wait(
                "security-events",
                value=event,
                key=event.get("source_ip", "").encode(),
            )
        except Exception as e:
            logger.error("Failed to send event to Kafka", error=str(e))
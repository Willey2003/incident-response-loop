"""
Redaction pipeline for AI Copilot.
Removes sensitive information before sending to LLM.
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

import structlog

logger = structlog.get_logger()


@dataclass
class Redaction:
    type: str
    start: int
    end: int
    original: str
    replacement: str


class RedactionPipeline:
    """Redacts sensitive information from text before LLM processing."""
    
    def __init__(self):
        self.patterns = {
            # API keys and secrets
            'api_key': re.compile(r'(?i)(api[_-]?key|secret[_-]?key|access[_-]?token)["\s:=]+([a-zA-Z0-9_\-]{20,})'),
            'aws_key': re.compile(r'(?i)(aws[_-]?access[_-]?key|aws[_-]?secret[_-]?key)["\s:=]+([A-Z0-9]{20})'),
            'github_token': re.compile(r'(?i)gh[pousr]_[a-zA-Z0-9]{36}'),
            'gitlab_token': re.compile(r'(?i)glpat-[a-zA-Z0-9_\-]{20,}'),
            
            # JWT tokens
            'jwt': re.compile(r'eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+'),
            
            # IP addresses
            'ipv4': re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b'),
            'ipv6': re.compile(r'(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}'),
            'cidr': re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}/\d{1,2}\b'),
            
            # Email addresses
            'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            
            # Passwords
            'password': re.compile(r'(?i)(password|passwd|pwd)["\s:=]+([^\s]+)'),
            
            # SSH keys
            'ssh_private_key': re.compile(r'-----BEGIN (RSA|OPENSSH|DSA|EC|OPENSSH) PRIVATE KEY-----'),
            'ssh_public_key': re.compile(r'ssh-(rsa|dsa|ecdsa|ed25519) [A-Za-z0-9+/]+[=]{0,2}'),
            
            # Database URLs
            'database_url': re.compile(r'(?i)(postgresql|mysql|mongodb|redis)://[^\s]+'),
            
            # Credit cards
            'credit_card': re.compile(r'\b(?:\d{4}[-\s]?){3}\d{4}\b'),
            
            # AWS ARNs
            'aws_arn': re.compile(r'arn:aws:[a-z]+:[a-z0-9-]+:\d{12}:[a-zA-Z0-9:/_-]+'),
            
            # Kubernetes secrets
            'k8s_secret': re.compile(r'(?i)secret["\s:=]+([a-zA-Z0-9+/=]{20,})'),
        }
    
    def redact(self, text: str, 
               redact_secrets: bool = True,
               redact_pii: bool = True,
               redact_ips: bool = True,
               redact_tokens: bool = True,
               custom_patterns: Optional[Dict[str, str]] = None) -> Tuple[str, List[Dict]]:
        """Redact sensitive information from text."""
        if not text:
            return text, []
        
        redactions = []
        redacted_text = text
        
        # Built-in patterns
        patterns_to_check = {}
        
        if redact_secrets:
            patterns_to_check.update({
                k: v for k, v in self.patterns.items() 
                if k in ['api_key', 'aws_key', 'github_token', 'gitlab_token', 'password', 'database_url', 'credit_card', 'aws_arn', 'k8s_secret']
            })
        
        if redact_tokens:
            patterns_to_check.update({
                k: v for k, v in self.patterns.items() 
                if k in ['api_key', 'github_token', 'gitlab_token', 'jwt', 'ssh_private_key', 'ssh_public_key', 'k8s_secret']
            })
        
        if redact_ips:
            patterns_to_check.update({
                k: v for k, v in self.patterns.items() 
                if k in ['ipv4', 'ipv6', 'cidr']
            })
        
        if redact_pii:
            patterns_to_check.update({
                k: v for k, v in self.patterns.items() 
                if k in ['email']
            })
        
        # Custom patterns
        if custom_patterns:
            for name, pattern in custom_patterns.items():
                try:
                    patterns_to_check[name] = re.compile(pattern)
                except re.error as e:
                    logger.warning("Invalid custom regex pattern", pattern=pattern, error=str(e))
        
        # Apply redactions
        for name, pattern in patterns_to_check.items():
            for match in pattern.finditer(redacted_text):
                start, end = match.span()
                original = match.group()
                replacement = f"[REDACTED {name.upper()}]"
                
                redactions.append({
                    "type": name,
                    "start": start,
                    "end": end,
                    "original": original,
                    "replacement": replacement,
                })
                
                # Replace in text
                redacted_text = redacted_text[:start] + replacement + redacted_text[end:]
                
                # Adjust positions for subsequent matches (simplified - in reality need to track offsets)
        
        # Sort redactions by position
        redactions.sort(key=lambda x: x["start"])
        
        return redacted_text, redactions
    
    def redact_for_llm(self, text: str) -> Tuple[str, List[Dict]]:
        """Redact text for LLM processing with all safety filters enabled."""
        return self.redact(
            text,
            redact_secrets=True,
            redact_pii=True,
            redact_ips=True,
            redact_tokens=True,
        )
    
    def redact_for_logging(self, text: str) -> str:
        """Redact text for logging purposes."""
        redacted, _ = self.redact(
            text,
            redact_secrets=True,
            redact_pii=True,
            redact_ips=True,
            redact_tokens=True,
        )
        return redacted
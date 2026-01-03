"""
OSINT Compliance and Ethics Module

Handles ethical compliance for OSINT operations.
"""

import asyncio
import re
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from urllib.robotparser import RobotFileParser

import httpx
from loguru import logger


class OSINTCompliance:
    """
    Ethics and compliance checker for OSINT operations.

    Handles:
    - robots.txt enforcement
    - Rate limiting
    - User agent rotation
    - Honeypot detection
    - Data sensitivity validation
    - Audit logging
    - Jurisdiction compliance
    """

    def __init__(self):
        self.robots_cache: Dict[str, Dict[str, Any]] = {}
        self.rate_limit_cache: Dict[str, Dict[str, Any]] = {}
        self.blocked_domains: List[str] = [
            # Government/military domains
            ".gov",
            ".mil",
            # Sensitive domains (example - customize based on use case)
            ".bank",
            ".insurance",
        ]

        # Default rate limits (requests per second)
        self.default_rate_limits = {
            "per_domain": 0.5,  # 1 request every 2 seconds
            "per_target": 1.0,  # 1 request per second
            "global": 10.0,  # 10 requests per second globally
        }

        # Realistic user agents
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
        ]

        self.current_ua_index = 0

    async def check_robots_txt(self, domain: str, user_agent: str = "*", path: str = "/") -> bool:
        """
        Check robots.txt and respect rules.

        Args:
            domain: Domain to check
            user_agent: User agent string (default: *)
            path: Path to check (default: /)

        Returns:
            True if allowed, False if disallowed
        """
        try:
            # Check cache first
            cache_key = f"{domain}_{user_agent}"
            if cache_key in self.robots_cache:
                cache_entry = self.robots_cache[cache_key]
                # Cache expires after 1 hour
                if datetime.utcnow() - cache_entry["cached_at"] < timedelta(hours=1):
                    rp = cache_entry["parser"]
                else:
                    del self.robots_cache[cache_key]
                    rp = None
            else:
                rp = None

            if rp is None:
                # Fetch robots.txt
                robots_url = f"https://{domain}/robots.txt"

                try:
                    async with httpx.AsyncClient(timeout=10) as client:
                        response = await client.get(robots_url)
                        if response.status_code == 200:
                            rp = RobotFileParser()
                            rp.parse(response.text.splitlines())

                            # Cache it
                            self.robots_cache[cache_key] = {
                                "parser": rp,
                                "cached_at": datetime.utcnow(),
                            }
                            logger.info(f"Loaded robots.txt for {domain}")
                        else:
                            logger.info(f"No robots.txt at {domain}, allowing access")
                            return True

                except Exception as e:
                    logger.warning(f"Failed to fetch robots.txt for {domain}: {e}")
                    return True

            if rp:
                allowed = rp.can_fetch(user_agent, path)
                if not allowed:
                    logger.warning(f"robots.txt disallows {path} for {user_agent} on {domain}")

                return allowed

            return True

        except Exception as e:
            logger.error(f"Error checking robots.txt: {e}")
            return True

    async def respect_rate_limits(
        self,
        domain: str,
        target: Optional[str] = None,
        rate_limits: Optional[Dict[str, float]] = None,
    ) -> float:
        """
        Respect rate limits with delays.

        Args:
            domain: Domain being accessed
            target: Specific target being accessed
            rate_limits: Custom rate limits

        Returns:
            Delay time in seconds
        """
        limits = rate_limits or self.default_rate_limits
        now = time.time()

        delay = 0.0

        # Check per-domain rate limit
        cache_key = f"domain_{domain}"
        if cache_key in self.rate_limit_cache:
            last_access = self.rate_limit_cache[cache_key]["last_access"]
            time_since = now - last_access
            min_interval = 1.0 / limits.get("per_domain", 1.0)

            if time_since < min_interval:
                delay = max(delay, min_interval - time_since)

        # Check per-target rate limit
        if target:
            target_key = f"target_{target}"
            if target_key in self.rate_limit_cache:
                last_access = self.rate_limit_cache[target_key]["last_access"]
                time_since = now - last_access
                min_interval = 1.0 / limits.get("per_target", 1.0)

                if time_since < min_interval:
                    delay = max(delay, min_interval - time_since)

        # Apply delay if needed
        if delay > 0:
            logger.debug(f"Rate limiting: delaying {delay:.2f}s for {domain}")

            # If delay is significant, consider it a minor violation or log it
            if delay > 5.0:
                asyncio.create_task(
                    self.report_violation(
                        violation_type="rate_limit",
                        severity="low",
                        message=f"Significant rate limit delay ({delay:.2f}s) for {domain}",
                        source="rate_limiter",
                        metadata={"domain": domain, "delay": delay},
                    )
                )

            await asyncio.sleep(delay)

        # Update cache
        for key in [cache_key] + ([target_key] if target else []):
            self.rate_limit_cache[key] = {"last_access": time.time()}

        return delay

    def rotate_user_agents(self) -> str:
        """
        Rotate to next user agent.

        Returns:
            User agent string
        """
        ua = self.user_agents[self.current_ua_index]
        self.current_ua_index = (self.current_ua_index + 1) % len(self.user_agents)
        return ua

    def get_random_user_agent(self) -> str:
        """Get a random user agent"""
        import random

        return random.choice(self.user_agents)

    async def detect_honeypots(self, domain: str) -> bool:
        """
        Identify potential honeypot domains.

        Args:
            domain: Domain to check

        Returns:
            True if likely a honeypot, False otherwise
        """
        # Note: Real honeypot detection is complex
        # This is a basic heuristic-based implementation

        indicators = 0

        try:
            # Check for suspicious patterns
            suspicious_patterns = [r"honeypot", r"trap", r"canary", r"decoy"]

            for pattern in suspicious_patterns:
                if re.search(pattern, domain, re.I):
                    indicators += 1

            # Check for unusual TLD
            uncommon_tlds = [".tk", ".ml", ".ga", ".cf"]
            if any(domain.endswith(tld) for tld in uncommon_tlds):
                indicators += 1

            # Check for excessive subdomains
            subdomain_count = domain.count(".")
            if subdomain_count > 5:
                indicators += 1

            # Check for very short or very long domains
            domain_name = domain.split(".")[0]
            if len(domain_name) < 3 or len(domain_name) > 63:
                indicators += 1

            # If multiple indicators, flag as potential honeypot
            if indicators >= 2:
                logger.warning(f"Potential honeypot detected: {domain} ({indicators} indicators)")
                return True

        except Exception as e:
            logger.error(f"Error detecting honeypots: {e}")

        return False

    def validate_data_sensitivity(self, data: Any, collection_type: str) -> Dict[str, Any]:
        """
        Check for PII and sensitive data collection.

        Args:
            data: Collected data
            collection_type: Type of collection operation

        Returns:
            Validation result with any issues found
        """
        result = {"allowed": True, "issues": [], "sensitive_data_detected": False}

        try:
            # Convert data to string for analysis
            data_str = str(data).lower()

            # PII patterns (basic detection)
            pii_patterns = {
                "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
                "credit_card": r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13})\b",
                "phone": r"\b\d{3}-\d{3}-\d{4}\b",
            }

            for pii_type, pattern in pii_patterns.items():
                matches = re.findall(pattern, data_str)
                if matches:
                    result["issues"].append({"type": pii_type, "count": len(matches), "severity": "HIGH"})
                    result["sensitive_data_detected"] = True

            # Check for passwords
            if "password" in data_str and ":" in data_str:
                result["issues"].append({"type": "potential_password", "count": 1, "severity": "CRITICAL"})
                result["sensitive_data_detected"] = True

            # Check for API keys (basic pattern)
            api_key_patterns = [
                r"api[_-]?key\s*[:=]\s*['\"][a-zA-Z0-9]{20,}['\"]",
                r"apikey\s*[:=]\s*['\"][a-zA-Z0-9]{20,}['\"]",
            ]

            for pattern in api_key_patterns:
                matches = re.findall(pattern, data_str)
                if matches:
                    result["issues"].append(
                        {
                            "type": "potential_api_key",
                            "count": len(matches),
                            "severity": "HIGH",
                        }
                    )
                    result["sensitive_data_detected"] = True

            # Determine if collection should be blocked
            if result["sensitive_data_detected"]:
                critical_issues = [i for i in result["issues"] if i.get("severity") == "CRITICAL"]

                # Report violation for any sensitive data detected
                for issue in result["issues"]:
                    asyncio.create_task(
                        self.report_violation(
                            violation_type="data_sensitivity",
                            severity=issue["severity"].lower(),
                            message=f"Sensitive data detected ({issue['type']}): {issue['count']} matches",
                            source=collection_type,
                            metadata={"issue": issue},
                        )
                    )

                if critical_issues:
                    result["allowed"] = False
                    logger.warning("Sensitive data detected - collection blocked")

        except Exception as e:
            logger.error(f"Error validating data sensitivity: {e}")

        return result

    def log_collection_activity(self, target: str, data: Any, collection_type: str, status: str = "success"):
        """
        Log collection activity for audit trail.

        Args:
            target: Target being collected
            data: Collected data summary
            collection_type: Type of collection
            status: Collection status
        """
        import json
        import uuid

        from app.database import get_db
        from app.models.intelligence import ComplianceAuditTrail

        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "target": target,
            "collection_type": collection_type,
            "status": status,
            "data_summary": str(len(str(data))) if data else 0,
        }

        logger.info(f"Collection activity: {log_entry}")

        # Store in DB for audit trail
        try:
            db = next(get_db())
            try:
                audit_id = str(uuid.uuid4())
                db_audit = ComplianceAuditTrail(
                    id=audit_id,
                    action="collected",
                    actor="system",
                    source=collection_type,
                    status=status,
                    details=json.dumps(log_entry),
                    timestamp=datetime.utcnow(),
                )
                db.add(db_audit)
                db.commit()
            except Exception as e:
                db.rollback()
                logger.error(f"Failed to log audit activity: {e}")
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Failed to get DB session for audit: {e}")

    async def report_violation(
        self,
        violation_type: str,
        severity: str,
        message: str,
        source: str,
        collection_id: Optional[str] = None,
        entity_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Record a compliance violation and broadcast it.
        """
        import json
        import uuid

        from app.api.websockets import broadcast_compliance_violation
        from app.database import get_db
        from app.models.intelligence import ComplianceViolation

        violation_id = str(uuid.uuid4())

        # Store in DB
        try:
            db = next(get_db())
            try:
                db_violation = ComplianceViolation(
                    id=violation_id,
                    collection_id=collection_id,
                    entity_id=entity_id,
                    violation_type=violation_type,
                    severity=severity,
                    message=message,
                    source=source,
                    metadata=json.dumps(metadata) if metadata else None,
                    created_at=datetime.utcnow(),
                )
                db.add(db_violation)
                db.commit()

                # Broadcast via WebSocket
                await broadcast_compliance_violation(
                    {
                        "id": violation_id,
                        "type": violation_type,
                        "severity": severity,
                        "message": message,
                        "source": source,
                        "collection_id": collection_id,
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                )

                logger.warning(f"Compliance violation recorded: {violation_type} ({severity}) - {message}")
            except Exception as e:
                db.rollback()
                logger.error(f"Failed to record compliance violation in DB: {e}")
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Failed to get DB session for violation: {e}")

    async def get_ethical_verdict(self, target: str, collection_type: str) -> Dict[str, Any]:
        """
        Get ethical verdict for collection operation.

        Args:
            target: Target to check
            collection_type: Type of collection

        Returns:
            Verdict with allow/deny decision and reason
        """
        verdict = {"allowed": True, "reason": "", "conditions": []}

        try:
            # Check if target is a blocked domain
            if any(target.endswith(domain) for domain in self.blocked_domains):
                verdict["allowed"] = False
                verdict["reason"] = "Target is in blocked domain list"
                logger.warning(f"Collection blocked: {target} (blocked domain)")
                await self.report_violation(
                    violation_type="policy",
                    severity="high",
                    message=f"Attempted collection from blocked domain: {target}",
                    source=collection_type,
                    metadata={"target": target, "rule": "blocked_domains"},
                )
                return verdict

            # Check for honeypots
            if await self.detect_honeypots(target):
                verdict["allowed"] = False
                verdict["reason"] = "Potential honeypot detected"
                logger.warning(f"Collection blocked: {target} (honeypot)")
                await self.report_violation(
                    violation_type="policy",
                    severity="medium",
                    message=f"Potential honeypot detected: {target}",
                    source=collection_type,
                    metadata={"target": target, "rule": "honeypot_detection"},
                )
                return verdict

            # Check robots.txt for domains
            try:
                if "." in target and not target.startswith(("http://", "https://")):
                    # It's likely a domain
                    domain = target
                    if not await self.check_robots_txt(domain, path="/"):
                        verdict["allowed"] = False
                        verdict["reason"] = "robots.txt disallows access"
                        logger.warning(f"Collection blocked: {target} (robots.txt)")
                        await self.report_violation(
                            violation_type="robots_txt",
                            severity="medium",
                            message=f"robots.txt restriction for {domain}",
                            source=collection_type,
                            metadata={"target": target, "domain": domain},
                        )
                        return verdict
            except Exception as e:
                logger.debug(f"Could not check robots.txt: {e}")

            # All checks passed
            verdict["reason"] = "All ethical checks passed"
            verdict["conditions"] = [
                "Respect rate limits (1 request per 2 seconds)",
                "Use realistic user agents",
                "Respect robots.txt rules",
                "Do not collect sensitive PII",
                "Implement retry with exponential backoff",
            ]

        except Exception as e:
            logger.error(f"Error getting ethical verdict: {e}")
            verdict["allowed"] = False
            verdict["reason"] = f"Error during ethical check: {e}"

        return verdict

    async def apply_delay_with_retry_after(self, headers: Dict[str, str]) -> bool:
        """
        Check for Retry-After header and apply appropriate delay.

        Args:
            headers: HTTP response headers

        Returns:
            True if delay was applied, False otherwise
        """
        try:
            retry_after = headers.get("Retry-After")

            if retry_after:
                # Try to parse as integer (seconds)
                try:
                    delay = int(retry_after)
                    logger.info(f"Retry-After header detected, waiting {delay}s")
                    await asyncio.sleep(delay)
                    return True
                except ValueError:
                    # Try to parse as HTTP date
                    from email.utils import parsedate_to_datetime

                    try:
                        retry_date = parsedate_to_datetime(retry_after)
                        delay = (retry_date - datetime.utcnow(retry_date.tzinfo)).total_seconds()
                        if delay > 0:
                            logger.info(f"Retry-After date detected, waiting {delay}s")
                            await asyncio.sleep(delay)
                            return True
                    except Exception:
                        pass

        except Exception as e:
            logger.error(f"Error handling Retry-After header: {e}")

        return False

    def check_jurisdiction_compliance(self, target: str, collection_type: str) -> Dict[str, Any]:
        """
        Check compliance with jurisdiction-specific regulations.

        Args:
            target: Target being collected
            collection_type: Type of collection

        Returns:
            Compliance information
        """
        result = {
            "compliant": True,
            "jurisdiction": "unknown",
            "regulations": [],
            "notes": [],
        }

        try:
            # Simple TLD-based jurisdiction detection
            tld_to_jurisdiction = {
                ".eu": "EU (GDPR)",
                ".uk": "UK (UK GDPR)",
                ".ca": "Canada (PIPEDA)",
                ".au": "Australia (Privacy Act)",
            }

            domain = target.replace("http://", "").replace("https://", "").split("/")[0]

            for tld, jurisdiction in tld_to_jurisdiction.items():
                if domain.endswith(tld):
                    result["jurisdiction"] = jurisdiction
                    result["regulations"].append(jurisdiction)
                    result["notes"].append(f"Ensure compliance with {jurisdiction} regulations")
                    break

        except Exception as e:
            logger.error(f"Error checking jurisdiction compliance: {e}")

        return result

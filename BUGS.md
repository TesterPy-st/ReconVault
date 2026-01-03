# Bug Tracking and Management

## Overview

This document tracks known bugs, their status, and resolution progress for the ReconVault project.

## Bug Status Legend

- 🔴 **OPEN** - Bug identified, not yet assigned
- 🟡 **IN PROGRESS** - Actively being worked on
- 🟢 **RESOLVED** - Fix implemented and tested
- ⚫ **CLOSED** - Verified fixed in production
- 🔵 **WONTFIX** - Not fixing (by design or out of scope)

## Priority Levels

- **P0 - CRITICAL** - System crash, data loss, security vulnerability
- **P1 - HIGH** - Major feature broken, significant impact
- **P2 - MEDIUM** - Feature partially broken, workaround exists
- **P3 - LOW** - Minor issue, cosmetic, edge case

---

## Active Bugs

### Backend Issues

#### BUG-001: Rate Limiter Memory Leak
- **Status:** 🟡 IN PROGRESS
- **Priority:** P1 - HIGH
- **Severity:** High
- **Component:** `app/ethics/compliance.py`
- **Reported:** 2024-01-03
- **Assigned:** Backend Team
- **Description:** Rate limiter accumulates entries indefinitely, causing memory growth over time.
- **Reproduction:**
  1. Start backend server
  2. Make 1000+ requests from different hosts
  3. Monitor memory usage - grows continuously
- **Expected:** Rate limiter should clean up old entries
- **Actual:** Memory usage grows without limit
- **Workaround:** Restart service periodically
- **Fix Status:** Implementing TTL-based cleanup mechanism
- **Test Case:** `tests/bugs/test_bug_001_rate_limiter.py`

#### BUG-002: Neo4j Connection Pool Exhaustion
- **Status:** 🔴 OPEN
- **Priority:** P2 - MEDIUM
- **Severity:** Medium
- **Component:** `app/intelligence_graph/neo4j_client.py`
- **Reported:** 2024-01-03
- **Assigned:** Unassigned
- **Description:** Neo4j connections not properly released under high load
- **Reproduction:**
  1. Run load test with 100+ concurrent users
  2. Perform graph operations
  3. Connection pool exhausts after ~5 minutes
- **Expected:** Connections released after use
- **Actual:** Connection pool saturates
- **Workaround:** Increase pool size, restart service
- **Fix Status:** Needs investigation
- **Test Case:** `tests/bugs/test_bug_002_neo4j_pool.py`

#### BUG-003: Collector Timeout Not Respected
- **Status:** 🟢 RESOLVED
- **Priority:** P2 - MEDIUM
- **Severity:** Medium
- **Component:** `app/collectors/base_collector.py`
- **Reported:** 2024-01-02
- **Assigned:** Backend Team
- **Resolved:** 2024-01-03
- **Description:** HTTP requests don't timeout when specified timeout exceeded
- **Reproduction:**
  1. Set collector timeout to 5 seconds
  2. Request very slow endpoint
  3. Collector hangs indefinitely
- **Expected:** Request canceled after 5 seconds
- **Actual:** Request never times out
- **Fix:** Added proper timeout handling with asyncio.timeout
- **Fixed In:** Commit `abc123`
- **Test Case:** `tests/unit/test_collectors.py::test_web_collector_timeout`

### Frontend Issues

#### BUG-004: Graph Canvas Performance Degradation
- **Status:** 🟡 IN PROGRESS
- **Priority:** P1 - HIGH
- **Severity:** High
- **Component:** `frontend/src/components/GraphCanvas.jsx`
- **Reported:** 2024-01-03
- **Assigned:** Frontend Team
- **Description:** Graph rendering becomes very slow with 1000+ nodes
- **Reproduction:**
  1. Load target with 1000+ entities
  2. Attempt to zoom/pan graph
  3. UI becomes unresponsive
- **Expected:** Smooth rendering even with large graphs
- **Actual:** UI freezes, rendering takes 5+ seconds
- **Workaround:** Use filtering to reduce visible nodes
- **Fix Status:** Implementing virtualization and WebGL rendering
- **Test Case:** `frontend/src/__tests__/performance/graph-performance.test.js`

#### BUG-005: WebSocket Reconnection Fails
- **Status:** 🔴 OPEN
- **Priority:** P2 - MEDIUM
- **Severity:** Medium
- **Component:** `frontend/src/services/websocketService.js`
- **Reported:** 2024-01-03
- **Assigned:** Unassigned
- **Description:** WebSocket doesn't reconnect after connection loss
- **Reproduction:**
  1. Establish WebSocket connection
  2. Kill backend server
  3. Restart backend
  4. WebSocket remains disconnected
- **Expected:** Automatic reconnection after backend available
- **Actual:** Manual page refresh required
- **Workaround:** Refresh page
- **Fix Status:** Needs implementation
- **Test Case:** `frontend/src/__tests__/websocket-reconnect.test.js`

### Integration Issues

#### BUG-006: Race Condition in Collection Pipeline
- **Status:** 🟡 IN PROGRESS
- **Priority:** P1 - HIGH
- **Severity:** High
- **Component:** Multiple (collectors, normalization, database)
- **Reported:** 2024-01-03
- **Assigned:** Backend Team
- **Description:** Concurrent collections on same target cause duplicate entities
- **Reproduction:**
  1. Start two collections for same target simultaneously
  2. Wait for completion
  3. Database contains duplicate entities
- **Expected:** Entities deduplicated regardless of collection order
- **Actual:** Duplicate entries created
- **Workaround:** Don't run concurrent collections on same target
- **Fix Status:** Implementing database-level uniqueness constraints
- **Test Case:** `tests/integration/test_bug_006_race_condition.py`

---

## Resolved Bugs (Recent)

### BUG-007: Email Validation Regex Too Strict
- **Status:** ⚫ CLOSED
- **Priority:** P3 - LOW
- **Resolved:** 2024-01-02
- **Description:** Email validator rejected valid international domains
- **Fix:** Updated regex to support internationalized domains
- **Verified In:** v0.2.0

### BUG-008: Compliance Score Calculation Error
- **Status:** ⚫ CLOSED
- **Priority:** P2 - MEDIUM
- **Resolved:** 2024-01-02
- **Description:** Compliance score could exceed 100
- **Fix:** Added bounds checking to ensure 0-100 range
- **Verified In:** v0.2.0

---

## Known Limitations

### LIMIT-001: Dark Web Collection Requires Tor
- **Status:** 🔵 WONTFIX (By Design)
- **Description:** Dark web collection requires Tor installation
- **Reason:** Necessary for .onion address access
- **Documentation:** Added to README and setup docs

### LIMIT-002: ML Models Not Included in Repository
- **Status:** 🔵 WONTFIX (By Design)
- **Description:** Trained ML models not included in git repository
- **Reason:** Large file sizes (>100MB)
- **Workaround:** Download from release artifacts or train locally
- **Documentation:** Added to deployment docs

---

## Bug Report Template

When reporting a new bug, please include:

```markdown
### BUG-XXX: [Short Description]
- **Status:** 🔴 OPEN
- **Priority:** P? - [CRITICAL/HIGH/MEDIUM/LOW]
- **Severity:** [High/Medium/Low]
- **Component:** `path/to/file.py`
- **Reported:** YYYY-MM-DD
- **Assigned:** [Team/Person/Unassigned]
- **Description:** Clear description of the bug
- **Reproduction:**
  1. Step 1
  2. Step 2
  3. Step 3
- **Expected:** What should happen
- **Actual:** What actually happens
- **Workaround:** Temporary solution if available
- **Fix Status:** Current status of fix
- **Test Case:** Path to test that reproduces bug
```

---

## Bug Workflow

1. **Report** - Bug identified and documented
2. **Triage** - Priority and severity assigned
3. **Assign** - Assigned to team member
4. **Investigate** - Root cause identified
5. **Fix** - Code changes implemented
6. **Test** - Regression test created and passing
7. **Review** - Code review completed
8. **Deploy** - Fix deployed to environment
9. **Verify** - Bug verified fixed
10. **Close** - Bug marked as closed

---

## Testing for Bugs

All bugs should have corresponding test cases:

```python
# tests/bugs/test_bug_001_rate_limiter.py
def test_bug_001_rate_limiter_memory_leak():
    """
    Test that rate limiter doesn't leak memory.
    
    Bug: BUG-001
    Status: IN PROGRESS
    """
    rate_limiter = RateLimiter(max_requests=10, time_window=60)
    
    # Make many requests
    for i in range(10000):
        rate_limiter.check_rate_limit(f"host{i}.com")
    
    # Check that old entries are cleaned up
    assert len(rate_limiter._requests) < 1000  # Should have cleaned up old entries
```

---

## Metrics

### Bug Statistics

- **Total Open Bugs:** 3
- **Total In Progress:** 3
- **Total Resolved (This Month):** 2
- **Average Time to Resolution:** 2.5 days
- **Critical Bugs Open:** 0
- **High Priority Bugs Open:** 2

### Bug Trends

- **Week 1:** 5 bugs reported, 2 resolved
- **Week 2:** 3 bugs reported, 3 resolved
- **Week 3:** 2 bugs reported, 1 resolved
- **Week 4:** 1 bug reported, 2 resolved

---

## Contact

To report a bug:
1. Check if already reported in this document
2. Create detailed bug report using template
3. Submit PR updating this document
4. Notify team in Slack #bugs channel

For urgent/critical bugs, contact on-call engineer immediately.

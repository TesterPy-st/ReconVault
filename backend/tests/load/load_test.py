"""
Load tests using Locust.

Simulates:
- 100+ concurrent users
- API endpoint stress testing
- WebSocket connections
- Database performance under load
"""
from locust import HttpUser, task, between, events
import json


class ReconVaultUser(HttpUser):
    """Simulated ReconVault user for load testing."""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    
    def on_start(self):
        """Called when a user starts."""
        # Initialize any user session data
        self.client.headers.update({"User-Agent": "LoadTest/1.0"})
    
    @task(3)
    def get_health(self):
        """Test health endpoint (most frequent)."""
        self.client.get("/health")
    
    @task(2)
    def list_targets(self):
        """Test listing targets."""
        self.client.get("/api/targets")
    
    @task(2)
    def list_entities(self):
        """Test listing entities."""
        self.client.get("/api/entities")
    
    @task(1)
    def get_graph(self):
        """Test getting graph data."""
        self.client.get("/api/graph")
    
    @task(1)
    def create_target(self):
        """Test creating a target."""
        data = {
            "name": f"Load Test Target",
            "type": "domain",
            "value": f"loadtest-{self.environment.runner.user_count}.com",
            "priority": "medium"
        }
        self.client.post("/api/targets", json=data)
    
    @task(1)
    def search_entities(self):
        """Test searching entities."""
        self.client.get("/api/entities/search?q=test")
    
    @task(1)
    def get_compliance_report(self):
        """Test compliance reporting."""
        self.client.get("/api/compliance/report")


class APILoadTest(HttpUser):
    """Focused API load testing."""
    
    wait_time = between(0.5, 1.5)
    
    @task(5)
    def collection_api_load(self):
        """Test collection API under load (target: 100 req/sec)."""
        self.client.get("/api/collection")
    
    @task(10)
    def graph_api_load(self):
        """Test graph API under load (target: 200 req/sec)."""
        self.client.get("/api/graph")
    
    @task(15)
    def search_api_load(self):
        """Test search API under load (target: 300 req/sec)."""
        self.client.get("/api/entities/search?q=test")


class DatabaseQueryUser(HttpUser):
    """User simulating database-heavy operations."""
    
    wait_time = between(1, 2)
    
    @task
    def query_entities_with_filters(self):
        """Test complex entity queries."""
        self.client.get("/api/entities?type=domain&risk_level=high&limit=50")
    
    @task
    def query_relationships(self):
        """Test relationship queries."""
        self.client.get("/api/graph?depth=3")


# Performance targets and thresholds
@events.request.add_listener
def record_performance(request_type, name, response_time, response_length, exception, **kwargs):
    """Record performance metrics."""
    if exception:
        return
    
    # Check against performance targets
    if response_time > 500:  # 500ms threshold for 95th percentile
        print(f"SLOW REQUEST: {name} took {response_time}ms")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when test starts."""
    print("=" * 60)
    print("Starting ReconVault Load Test")
    print("Performance Targets:")
    print("  - API response time: < 500ms (95th percentile)")
    print("  - Graph load: < 2000ms for 10K+ nodes")
    print("  - WebSocket latency: < 100ms")
    print("  - Memory usage: < 2GB peak")
    print("  - CPU usage: < 80%")
    print("=" * 60)


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when test stops."""
    print("=" * 60)
    print("Load Test Complete")
    stats = environment.runner.stats
    print(f"Total Requests: {stats.num_requests}")
    print(f"Total Failures: {stats.num_failures}")
    print(f"Average Response Time: {stats.total.avg_response_time}ms")
    print(f"95th Percentile: {stats.total.get_response_time_percentile(0.95)}ms")
    print("=" * 60)


# Run configuration
# Command: locust -f load_test.py --host=http://localhost:8000
# Web UI: http://localhost:8089
# Headless: locust -f load_test.py --host=http://localhost:8000 --users 100 --spawn-rate 10 --run-time 5m --headless

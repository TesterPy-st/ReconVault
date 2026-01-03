# ReconVault Testing Guide

## Overview

This document provides comprehensive information about the testing infrastructure for ReconVault, including how to run tests, write new tests, and understand coverage requirements.

## Table of Contents

- [Test Structure](#test-structure)
- [Running Tests](#running-tests)
- [Writing Tests](#writing-tests)
- [Coverage Requirements](#coverage-requirements)
- [CI/CD Process](#cicd-process)
- [Troubleshooting](#troubleshooting)

## Test Structure

### Backend Tests

```
backend/tests/
├── __init__.py
├── conftest.py                      # Shared fixtures and configuration
├── unit/                            # Unit tests (200+ tests)
│   ├── test_collectors.py          # Collector tests (40+ tests)
│   ├── test_normalization.py       # Normalization tests (20+ tests)
│   ├── test_intelligence_graph.py  # Graph tests (25+ tests)
│   ├── test_risk_engine.py         # Risk engine tests (25+ tests)
│   ├── test_ai_engine.py           # AI/ML tests (20+ tests)
│   ├── test_compliance.py          # Compliance tests (20+ tests)
│   ├── test_api_routes.py          # API tests (35+ tests)
│   └── test_database.py            # Database tests (15+ tests)
├── integration/                     # Integration tests (40+ tests)
│   ├── test_collection_pipeline.py # Pipeline tests (10+ tests)
│   ├── test_graph_integration.py   # Graph integration (8+ tests)
│   ├── test_api_database_integration.py
│   └── test_websocket_integration.py
├── load/                            # Load tests
│   └── load_test.py                # Locust load tests
└── fixtures/                        # Test data and fixtures
```

### Frontend Tests

```
frontend/src/__tests__/
├── components.test.js               # Component tests (25+ tests)
├── hooks.test.js                    # React hooks tests (12+ tests)
├── services.test.js                 # Service tests (20+ tests)
├── utils.test.js                    # Utility tests (15+ tests)
└── fixtures/                        # Test data
```

### E2E Tests

```
frontend/e2e/
├── user-workflows.spec.js           # User workflow tests
└── api-integration.spec.js          # API integration tests
```

## Running Tests

### Backend Tests

#### Run All Backend Tests

```bash
cd backend
pytest
```

#### Run Unit Tests Only

```bash
pytest tests/unit/ -v
```

#### Run Integration Tests

```bash
pytest tests/integration/ -v
```

#### Run with Coverage

```bash
pytest --cov=app --cov-report=html --cov-report=term-missing
```

#### Run Specific Test File

```bash
pytest tests/unit/test_collectors.py -v
```

#### Run Specific Test

```bash
pytest tests/unit/test_collectors.py::TestWebCollector::test_web_collector_parsing_success -v
```

#### Run Tests by Marker

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"
```

### Frontend Tests

#### Run All Frontend Tests

```bash
cd frontend
npm test
```

#### Run with Coverage

```bash
npm test -- --coverage
```

#### Run in Watch Mode

```bash
npm test -- --watch
```

#### Run E2E Tests

```bash
npm run test:e2e
```

### Load Tests

#### Run Load Tests with Locust

```bash
cd backend/tests/load

# Run with web UI
locust -f load_test.py --host=http://localhost:8000

# Run headless
locust -f load_test.py --host=http://localhost:8000 --users 100 --spawn-rate 10 --run-time 5m --headless
```

## Writing Tests

### Backend Test Guidelines

#### 1. Use Fixtures

```python
@pytest.fixture
def sample_entity():
    return {
        "entity_type": "domain",
        "value": "example.com",
        "confidence": 0.95
    }

def test_entity_creation(sample_entity):
    assert sample_entity["entity_type"] == "domain"
```

#### 2. Test Success and Failure Paths

```python
def test_successful_collection(web_collector):
    """Test successful data collection."""
    result = await web_collector.collect()
    assert result.success is True

def test_failed_collection_timeout(web_collector):
    """Test collection failure due to timeout."""
    with patch('httpx.get', side_effect=asyncio.TimeoutError()):
        result = await web_collector.collect()
        assert result.success is False
```

#### 3. Use Descriptive Test Names

```python
# Good
def test_domain_collector_handles_nxdomain_error():
    pass

# Bad
def test_domain():
    pass
```

#### 4. Test Async Code Properly

```python
@pytest.mark.asyncio
async def test_async_collection():
    result = await collector.collect()
    assert result is not None
```

#### 5. Mock External Dependencies

```python
@patch('httpx.AsyncClient.get')
async def test_web_collector_with_mock(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_get.return_value = mock_response
    
    result = await collector.collect()
    assert result.success is True
```

### Frontend Test Guidelines

#### 1. Component Testing

```javascript
test('renders component with props', () => {
  render(<Component data={mockData} />);
  expect(screen.getByText('Expected Text')).toBeInTheDocument();
});
```

#### 2. User Interaction Testing

```javascript
test('handles button click', () => {
  const handleClick = jest.fn();
  render(<Button onClick={handleClick} />);
  
  fireEvent.click(screen.getByRole('button'));
  expect(handleClick).toHaveBeenCalled();
});
```

#### 3. Async Testing

```javascript
test('loads data asynchronously', async () => {
  render(<Component />);
  
  await waitFor(() => {
    expect(screen.getByText('Loaded Data')).toBeInTheDocument();
  });
});
```

## Coverage Requirements

### Backend Coverage

- **Minimum: 70%** overall coverage
- **Unit tests:** All critical paths covered
- **Integration tests:** Major workflows tested

#### Check Coverage

```bash
cd backend
pytest --cov=app --cov-report=term-missing

# View HTML report
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

### Frontend Coverage

- **Minimum: 60%** overall coverage
- **Components:** Major components tested
- **Services:** Critical services covered

#### Check Coverage

```bash
cd frontend
npm test -- --coverage
```

### Coverage Thresholds

```python
# backend/pytest.ini
[pytest]
addopts = --cov=app --cov-report=html --cov-fail-under=70
```

## CI/CD Process

### Pipeline Stages

1. **Lint & Format Check** (5 min)
   - Backend: pylint, black, isort, mypy
   - Frontend: eslint, prettier
   - Fails on critical issues

2. **Build** (10 min)
   - Backend: Docker build
   - Frontend: npm build
   - Verifies compilation

3. **Unit Tests** (15 min)
   - Backend: pytest with PostgreSQL
   - Frontend: jest
   - Coverage reports generated

4. **Integration Tests** (20 min)
   - Full stack testing
   - PostgreSQL, Neo4j, Redis services
   - API integration tests

5. **Security Scan** (10 min)
   - Dependency checking
   - Container scanning
   - Vulnerability reports

6. **Deploy Preview** (5 min)
   - Docker image build & push
   - Tagged with commit SHA
   - Available for deployment

### Running CI Locally

#### Using Act (GitHub Actions locally)

```bash
# Install act
brew install act  # macOS
# or
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Run CI workflow
act -j lint-backend
act -j test-backend-unit
```

#### Manual CI Simulation

```bash
# Run linting
cd backend && black --check app/ tests/
cd backend && flake8 app/ tests/

# Run tests
cd backend && pytest tests/unit/ --cov=app
cd frontend && npm test -- --coverage

# Run integration tests
docker-compose up -d postgres neo4j redis
cd backend && pytest tests/integration/
```

## Troubleshooting

### Common Issues

#### 1. Import Errors

```bash
# Add project root to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/backend"
```

#### 2. Database Connection Errors

```bash
# Ensure test database is running
docker-compose up -d postgres

# Or use in-memory SQLite
export DATABASE_URL="sqlite:///:memory:"
```

#### 3. Test Failures in CI

```bash
# Run tests with same environment as CI
docker run -it python:3.11 bash
pip install -r requirements.txt -r requirements-test.txt
pytest tests/
```

#### 4. Slow Tests

```bash
# Run tests in parallel
pytest -n auto

# Skip slow tests
pytest -m "not slow"
```

#### 5. Frontend Test Timeouts

```javascript
// Increase timeout
test('slow operation', async () => {
  // ...
}, 10000); // 10 second timeout
```

### Debug Mode

#### Backend

```bash
# Run single test with debug output
pytest tests/unit/test_collectors.py::test_name -vv -s

# Drop into debugger on failure
pytest --pdb
```

#### Frontend

```bash
# Run tests in debug mode
node --inspect-brk node_modules/.bin/jest --runInBand
```

## Best Practices

1. **Write tests first** (TDD) when adding new features
2. **Mock external services** to avoid flaky tests
3. **Use fixtures** for reusable test data
4. **Test edge cases** and error conditions
5. **Keep tests fast** - use mocks and in-memory databases
6. **Isolate tests** - no cross-test dependencies
7. **Clean up** after tests (teardown)
8. **Use descriptive names** for tests
9. **Group related tests** in classes
10. **Document complex tests** with comments

## Test Metrics

### Performance Targets

- **Unit tests:** < 1 second per test
- **Integration tests:** < 5 seconds per test
- **Total test suite:** < 60 minutes
- **Coverage generation:** < 2 minutes

### Quality Metrics

- **Test count:** 340+ tests
- **Backend coverage:** ≥ 70%
- **Frontend coverage:** ≥ 60%
- **Critical path coverage:** 100%

## Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [Jest Documentation](https://jestjs.io/)
- [React Testing Library](https://testing-library.com/react)
- [Locust Documentation](https://docs.locust.io/)

## Contact

For questions about testing, please contact the development team or open an issue on GitHub.

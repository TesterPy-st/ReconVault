# Contributors Guide

Thank you for your interest in contributing to ReconVault! This guide will help you get started.

## 🤝 How to Contribute

### Ways to Contribute

- **Report Bugs**: Open an issue with detailed reproduction steps
- **Suggest Features**: Propose new features via GitHub issues
- **Submit Code**: Fix bugs, add features, improve documentation
- **Improve Documentation**: Help make our docs clearer
- **Test**: Report issues, verify fixes, test new features

### Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Create a branch** for your changes
4. **Make your changes** following our guidelines
5. **Test your changes** thoroughly
6. **Submit a pull request** with clear description

## 📋 Development Setup

See the [Development Guide](../DEVELOPMENT.md) for complete setup instructions.

### Quick Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/reconvault.git
cd reconvault

# Create a feature branch
git checkout -b feature/your-feature-name

# Start development environment
docker-compose up -d
```

## 💻 Code Guidelines

### General Principles

- **Follow existing patterns** in the codebase
- **Write clear, self-documenting code**
- **Add comments only for complex logic**
- **Test your changes thoroughly**
- **Keep commits focused and atomic**

### Backend (Python)

**Style**:
- Follow PEP 8 conventions
- Use type hints for all functions
- Maximum line length: 88 characters (Black formatter)
- Docstrings in Google style

**Example**:
```python
def fetch_entity(entity_id: str, db: Session) -> Optional[Entity]:
    """
    Fetch an entity by ID from the database.
    
    Args:
        entity_id: Unique entity identifier
        db: Database session
        
    Returns:
        Entity object if found, None otherwise
    """
    try:
        return db.query(Entity).filter(Entity.id == entity_id).first()
    except Exception as e:
        logger.error(f"Failed to fetch entity {entity_id}: {e}")
        raise
```

**Testing**:
```bash
cd backend
pytest tests/ -v
pytest --cov=app tests/
```

### Frontend (React/JavaScript)

**Style**:
- Use functional components with hooks
- PropTypes for all component props
- ESLint + Prettier for formatting
- Use meaningful variable names

**Example**:
```jsx
import React from 'react';
import PropTypes from 'prop-types';

const EntityCard = ({ entity, onSelect }) => {
  const handleClick = () => {
    onSelect(entity.id);
  };

  return (
    <div onClick={handleClick} className="entity-card">
      <h3>{entity.name}</h3>
      <p>{entity.type}</p>
    </div>
  );
};

EntityCard.propTypes = {
  entity: PropTypes.shape({
    id: PropTypes.string.isRequired,
    name: PropTypes.string.isRequired,
    type: PropTypes.string.isRequired,
  }).isRequired,
  onSelect: PropTypes.func.isRequired,
};

export default EntityCard;
```

**Testing**:
```bash
cd frontend
npm test
npm run test:coverage
```

## 🔀 Git Workflow

### Branch Naming

Use descriptive branch names with prefixes:
- `feature/` - New features
- `bugfix/` - Bug fixes
- `hotfix/` - Urgent production fixes
- `refactor/` - Code refactoring
- `docs/` - Documentation changes

**Examples**:
- `feature/add-export-panel`
- `bugfix/fix-websocket-reconnect`
- `docs/update-api-reference`

### Commit Messages

Follow conventional commit format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples**:
```
feat(collectors): add dark web collector module

Implement Tor-based dark web collector with rate limiting
and ethical compliance checks.

Closes #123
```

```
fix(frontend): resolve 404 error on initial load

Create missing index.html entry point for Vite
```

### Pull Request Process

1. **Update your branch** with latest main
```bash
git fetch upstream
git rebase upstream/main
```

2. **Run tests** and ensure they pass
```bash
# Backend
cd backend && pytest

# Frontend  
cd frontend && npm test
```

3. **Push to your fork**
```bash
git push origin feature/your-feature-name
```

4. **Create pull request** on GitHub with:
   - Clear title and description
   - Reference related issues
   - Screenshots (for UI changes)
   - Test results

5. **Address review feedback**
   - Make requested changes
   - Push updates to same branch
   - Respond to comments

## 🧪 Testing Requirements

### Backend Tests

- Write unit tests for all new services
- Integration tests for API endpoints
- Maintain minimum 80% coverage

### Frontend Tests

- Component unit tests
- Integration tests for API calls
- E2E tests for critical workflows
- Maintain minimum 70% coverage

### Test Before Submitting

```bash
# Full test suite
docker-compose up -d
cd backend && pytest --cov=app
cd frontend && npm run test:coverage
```

## 📝 Documentation

### When to Update Docs

- New features → Update relevant docs
- API changes → Update API.md
- Bug fixes → Update TROUBLESHOOTING.md if relevant
- Breaking changes → Update DEVELOPMENT.md

### Documentation Style

- **Clear and concise** language
- **Code examples** for complex features
- **Screenshots** for UI features
- **Links** to related documentation

## 🎯 Code Review

### As a Contributor

- **Respond promptly** to review feedback
- **Be open** to suggestions
- **Ask questions** if unclear
- **Test thoroughly** before requesting review

### As a Reviewer

- **Be respectful** and constructive
- **Explain reasoning** for requested changes
- **Test the changes** when possible
- **Approve quickly** for good PRs

## 🐛 Reporting Issues

### Good Bug Reports Include

- **Clear title** describing the issue
- **Steps to reproduce** the problem
- **Expected behavior** vs actual behavior
- **Environment details** (OS, Docker version, etc.)
- **Logs** and error messages
- **Screenshots** if relevant

### Example Issue

```markdown
## Bug: Frontend 404 Error on Startup

**Description**: Frontend shows 404 error when accessing http://localhost:5173

**Steps to Reproduce**:
1. Run `docker-compose up -d`
2. Navigate to http://localhost:5173
3. See 404 error

**Expected**: ReconVault UI loads

**Actual**: 404 Not Found

**Environment**:
- Docker: 24.0.7
- OS: Ubuntu 22.04
- Branch: main

**Logs**:
```
vite v4.5.0 dev server running at:
> Local: http://localhost:5173/
GET / 404 Not Found
```

**Fix**: Missing index.html entry point
```

## 🏆 Recognition

Contributors will be:
- Listed in project README
- Credited in release notes
- Acknowledged in commit history

## 📞 Getting Help

- **Questions**: Open a discussion on GitHub
- **Issues**: Check existing issues first
- **Chat**: Join our community (link TBD)
- **Email**: contact@reconvault.com

## 📜 Code of Conduct

### Our Standards

- **Be respectful** and inclusive
- **Be collaborative** and helpful
- **Accept constructive criticism** gracefully
- **Focus on what's best** for the project

### Unacceptable Behavior

- Harassment or discrimination
- Trolling or insulting comments
- Publishing others' private information
- Other unprofessional conduct

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to ReconVault!** 🙌

Questions? Open an issue or contact the maintainers.

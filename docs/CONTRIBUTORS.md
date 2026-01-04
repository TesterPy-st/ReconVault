# Contributors

## Team

### Core Team

**Simanchala Bisoyi**
- Role: Lead Architect & Backend Developer
- Responsibilities: System architecture, backend development, database design
- GitHub: @simanchala

**Subham Mohanty**
- Role: Frontend Specialist & UI/UX Designer
- Responsibilities: Frontend development, UI design, user experience
- GitHub: @subham

**Abhinav Kumar**
- Role: DevOps & Infrastructure Engineer
- Responsibilities: Docker setup, CI/CD, deployment, monitoring
- GitHub: @abhinav

## Contribution Guidelines

### How to Contribute

We welcome contributions from the community! Here's how you can help:

1. **Report Bugs** - Found a bug? Create an issue with details
2. **Suggest Features** - Have an idea? Open a feature request
3. **Submit Code** - Fixed something? Submit a pull request
4. **Improve Docs** - Spotted an error? Help us improve documentation
5. **Answer Questions** - Help others in GitHub Discussions

### Getting Started

1. **Fork the Repository**
   ```bash
   # Click "Fork" on GitHub
   git clone https://github.com/YOUR_USERNAME/reconvault.git
   cd reconvault
   ```

2. **Create a Branch**
   ```bash
   git checkout -b feature/amazing-feature
   # or
   git checkout -b fix/bug-description
   ```

3. **Make Your Changes**
   - Follow the code standards (see DEVELOPMENT.md)
   - Write tests for new features
   - Update documentation

4. **Test Your Changes**
   ```bash
   # Backend
   cd backend
   pytest
   black app/
   flake8 app/

   # Frontend
   cd frontend
   npm test
   npm run lint
   ```

5. **Commit and Push**
   ```bash
   git add .
   git commit -m "feat(module): description of changes"
   git push origin feature/amazing-feature
   ```

6. **Create Pull Request**
   - Go to GitHub and create a PR
   - Describe your changes clearly
   - Reference related issues

### Code Standards

**Backend (Python):**
- Follow PEP 8 style guide
- Use type hints for all functions
- Write docstrings in Google style
- Maximum line length: 88 characters
- Use async/await for I/O operations

**Frontend (React):**
- Use functional components with hooks
- Add PropTypes for all components
- Follow ESLint + Prettier rules
- Use useCallback for event handlers
- Use useMemo for expensive calculations

**Git Commits:**
- Use conventional commit format: `type(scope): description`
- Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`
- Examples:
  - `feat(targets): add bulk import functionality`
  - `fix(collector): resolve race condition in web scraper`
  - `docs(readme): update installation instructions`

### Pull Request Guidelines

**Before Submitting:**
- [ ] Code follows project style guidelines
- [ ] Tests pass locally
- [ ] New features include tests
- [ ] Documentation is updated
- [ ] Commit messages are clear

**PR Description Template:**
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe how you tested this change

## Checklist
- [ ] Tests pass
- [ ] Code follows style guide
- [ ] Documentation updated
- [ ] No new warnings
```

## Reporting Issues

### Bug Reports

When reporting bugs, include:

1. **Title** - Clear, descriptive title
2. **Description** - What happened and what you expected
3. **Steps to Reproduce** - Minimal reproduction steps
4. **Environment** - OS, versions, configuration
5. **Logs** - Relevant error messages or logs
6. **Screenshots** - If applicable

**Example:**
```markdown
## Bug: Collection fails when target contains special characters

### Description
Collection fails when target name contains underscores or hyphens

### Steps to Reproduce
1. Create target: "my_test-domain.com"
2. Start web collection
3. Collection fails with error

### Environment
- OS: Ubuntu 22.04
- Version: 1.0.0-beta
- Docker: 24.0

### Error
```
ValueError: Invalid target name
```
```

### Feature Requests

When requesting features:

1. **Problem** - What problem does this solve?
2. **Proposed Solution** - How should it work?
3. **Alternatives** - Other solutions considered
4. **Additional Context** - Screenshots, examples, use cases

**Example:**
```markdown
## Feature: Add scheduled collections

### Problem
Currently, collections must be started manually. We need automated runs.

### Proposed Solution
- Add scheduler in backend
- UI to configure collection schedule
- Send notifications on completion

### Alternatives
- Use external cron jobs
- Integrate with existing task queue

### Additional Context
Would be useful for daily monitoring of targets
```

## Code of Conduct

### Our Pledge

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Accept feedback gracefully

### Unacceptable Behavior

- Harassment or discrimination
- Personal attacks or insults
- Sharing private information
- Spam or off-topic discussions

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project documentation

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

- Check [Documentation](INDEX.md)
- Join [GitHub Discussions](../../discussions)
- Open an [Issue](../../issues)

---

Thank you for contributing to ReconVault! 🚀

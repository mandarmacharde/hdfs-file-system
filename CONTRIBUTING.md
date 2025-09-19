# Contributing to HDFS File System

Thank you for your interest in contributing to the HDFS File System project! This document provides guidelines and information for contributors.

## 🚀 Quick Start for Contributors

### Prerequisites
- Python 3.8+
- Node.js 16+
- Git
- Docker (optional, for containerized development)

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/mandarmacharde/hdfs-file-system.git
   cd hdfs-file-system
   ```

2. **Start Development Environment**
   ```bash
   ./scripts/start-dev.sh
   ```

3. **Run Tests**
   ```bash
   ./scripts/test.sh
   ```

## 📋 Development Guidelines

### Code Style

#### Python
- Follow PEP 8 style guidelines
- Use type hints where possible
- Write docstrings for all public functions and classes
- Maximum line length: 88 characters (Black formatter)

#### TypeScript/React
- Use ESLint configuration provided
- Follow React best practices
- Use functional components with hooks
- Write JSDoc comments for complex functions

### Commit Messages

Use conventional commit format:
```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(namenode): add file replication monitoring
fix(datanode): resolve heartbeat timeout issue
docs(readme): update installation instructions
```

### Pull Request Process

1. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Your Changes**
   - Write clean, well-documented code
   - Add tests for new functionality
   - Update documentation as needed

3. **Test Your Changes**
   ```bash
   ./scripts/test.sh
   ```

4. **Submit Pull Request**
   - Provide a clear description of changes
   - Reference any related issues
   - Include screenshots for UI changes

## 🧪 Testing

### Backend Testing
- Unit tests for individual components
- Integration tests for API endpoints
- System tests for end-to-end functionality

### Frontend Testing
- Component unit tests
- Integration tests for user workflows
- Visual regression tests for UI changes

### Running Tests
```bash
# All tests
./scripts/test.sh

# Backend only
source venv/bin/activate && python test_hdfs.py

# Frontend only
cd hdfs-frontend && npm test
```

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Environment Information**
   - OS and version
   - Python version
   - Node.js version
   - Browser (for frontend issues)

2. **Steps to Reproduce**
   - Clear, numbered steps
   - Expected vs actual behavior
   - Screenshots or error messages

3. **Additional Context**
   - Any relevant configuration
   - Related issues or discussions

## 💡 Feature Requests

For feature requests, please:

1. Check existing issues first
2. Provide a clear use case
3. Explain the expected behavior
4. Consider implementation complexity

## 📚 Documentation

### Code Documentation
- All public APIs should have docstrings
- Complex algorithms should include comments
- README files for each major component

### User Documentation
- Keep README.md updated
- Provide clear installation instructions
- Include usage examples

## 🔧 Development Tools

### Recommended VS Code Extensions
- Python
- TypeScript and JavaScript
- ESLint
- Prettier
- Docker

### Pre-commit Hooks
```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install
```

## 🏗️ Architecture Guidelines

### Backend
- Follow separation of concerns
- Use dependency injection where appropriate
- Implement proper error handling
- Add logging for debugging

### Frontend
- Use React hooks for state management
- Implement proper error boundaries
- Follow accessibility guidelines
- Optimize for performance

## 📦 Release Process

1. Update version numbers
2. Update CHANGELOG.md
3. Create release branch
4. Run full test suite
5. Create GitHub release
6. Update documentation

## 🤝 Community Guidelines

- Be respectful and inclusive
- Help others learn and grow
- Provide constructive feedback
- Follow the code of conduct

## 📞 Getting Help

- Create an issue for bugs or questions
- Join discussions in GitHub Discussions
- Check existing documentation first

## 🎯 Areas for Contribution

### High Priority
- Performance optimizations
- Security improvements
- Test coverage
- Documentation

### Medium Priority
- New features
- UI/UX improvements
- Error handling
- Monitoring and logging

### Low Priority
- Code refactoring
- Style improvements
- Additional examples

Thank you for contributing! 🎉

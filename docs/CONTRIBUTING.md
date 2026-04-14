# Contributing to RAG-Based Intelligent Document Assistant

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## Getting Started

### Prerequisites
- Python 3.8+
- Groq API key
- Git

### Setup
1. Fork the repository
2. Clone your fork locally
3. Follow the setup instructions in README.md

## Development Workflow

### 1. Create a Branch
```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes
- Follow the existing code style
- Add tests for new features
- Update documentation as needed

### 3. Test Your Changes
```bash
# Run tests
python test_client.py

# Test error handling
python test_errors.py

# Run linting (if configured)
flake8 .
black .
```

### 4. Commit Changes
```bash
git add .
git commit -m "feat: add your feature description"
```

### 5. Push and Create PR
```bash
git push origin feature/your-feature-name
```
Then create a Pull Request on GitHub.

## Code Style Guidelines

### Python
- Follow PEP 8
- Use descriptive variable names
- Add docstrings to functions and classes
- Keep functions small and focused

### JavaScript
- Use ES6+ features
- Follow existing naming conventions
- Add comments for complex logic
- Use async/await for asynchronous operations

### HTML/CSS
- Use semantic HTML5 tags
- Follow Tailwind CSS conventions
- Keep components modular
- Ensure responsive design

## Project Structure

```
RAG-Based-Intelligent-Document-Assistant/
|
|-- main.py              # FastAPI application
|-- models.py            # Pydantic models
|-- rag_service.py       # Core RAG logic
|-- index.html           # Frontend HTML
|-- script.js            # Frontend JavaScript
|-- styles.css           # Custom styles
|-- test_client.py        # API tests
|-- test_errors.py        # Error tests
|-- setup.py             # Setup script
|-- requirements.txt      # Dependencies
|-- .env.example         # Environment template
|-- README.md           # Documentation
|-- CONTRIBUTING.md      # This file
|-- LICENSE             # License
```

## Types of Contributions

### Bug Fixes
- Describe the bug clearly
- Include steps to reproduce
- Add tests to prevent regression

### Features
- Describe the feature purpose
- Consider backwards compatibility
- Add comprehensive tests

### Documentation
- Fix typos and grammar
- Improve clarity
- Add examples

### Performance Improvements
- Benchmark before and after
- Explain the optimization
- Consider trade-offs

## Testing

### Running Tests
```bash
# Test API endpoints
python test_client.py

# Test error scenarios
python test_errors.py
```

### Writing Tests
- Test both success and failure cases
- Use descriptive test names
- Mock external dependencies when needed
- Test edge cases and boundary conditions

## Submitting Pull Requests

### PR Description
Include in your PR:
- Clear description of changes
- Reason for the change
- Testing performed
- Any breaking changes

### Review Process
1. Automated checks must pass
2. Code review by maintainers
3. Feedback addressed
4. Approval and merge

## Release Process

Maintainers will:
1. Update version numbers
2. Update CHANGELOG.md
3. Create git tag
4. Create GitHub release

## Community Guidelines

### Code of Conduct
- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Assume good intentions

### Communication
- Use GitHub issues for bugs/features
- Ask questions in discussions
- Be patient with responses

## Getting Help

- Check existing issues
- Read documentation
- Ask in discussions
- Contact maintainers

## Recognition

Contributors will be:
- Listed in README.md
- Mentioned in release notes
- Invited to collaborate further

Thank you for contributing!

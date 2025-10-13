# Contributing to adCTF

First off, thank you for considering contributing to adCTF! 🎉 It's people like you that make adCTF such a great tool for the CTF community.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Submitting Changes](#submitting-changes)
- [Style Guidelines](#style-guidelines)
- [Community](#community)

## 🤝 Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

### Our Pledge

We are committed to making participation in this project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, education, socio-economic status, nationality, personal appearance, race, religion, or sexual identity and orientation.

## 🛠 How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When you are creating a bug report, please include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples to demonstrate the steps**
- **Describe the behavior you observed and what you expected**
- **Include screenshots if applicable**
- **Provide your environment details** (OS, Python version, Docker version)

#### Bug Report Template

```markdown
**Bug Description**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected Behavior**
A clear and concise description of what you expected to happen.

**Screenshots**
If applicable, add screenshots to help explain your problem.

**Environment:**
 - OS: [e.g. Ubuntu 20.04]
 - Python Version: [e.g. 3.9.2]
 - Docker Version: [e.g. 20.10.7]
 - Browser: [e.g. Chrome 91.0]

**Additional Context**
Add any other context about the problem here.
```

### Suggesting Enhancements

Enhancement suggestions are welcome! Please provide:

- **Use a clear and descriptive title**
- **Provide a step-by-step description of the suggested enhancement**
- **Provide specific examples to demonstrate the enhancement**
- **Describe the current behavior and explain the expected behavior**
- **Explain why this enhancement would be useful**

### Contributing Code

#### Types of Contributions We're Looking For

- **Bug fixes**
- **New features** (please discuss in an issue first)
- **Performance improvements**
- **Documentation improvements**
- **Test coverage improvements**
- **Challenge templates and examples**
- **UI/UX improvements**

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Docker and Docker Compose
- Git
- A GitHub account

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/rayhanhanaputra/adCTF.git
   cd adCTF
   ```

3. Add the original repository as upstream:
   ```bash
   git remote add upstream https://github.com/rayhanhanaputra/adCTF.git
   ```

## 💻 Development Setup

### 1. Set Up Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Set Up Development Database

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your development settings
# Start development database
docker-compose -f docker-compose.db-only.yaml up -d

# Initialize database
python init_db.py
```

### 3. Run Development Server

```bash
# Start the development server
python run.py
```

The application will be available at http://localhost:5000

### 4. Set Up Pre-commit Hooks (Optional but Recommended)

```bash
pip install pre-commit
pre-commit install
```

## 🔄 Submitting Changes

### Pull Request Process

1. **Create a new branch** from the main branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the style guidelines

3. **Add tests** for new functionality

4. **Run the test suite**:
   ```bash
   python -m pytest tests/
   ```

5. **Update documentation** if necessary

6. **Commit your changes** with clear, descriptive messages:
   ```bash
   git add .
   git commit -m "Add feature: description of what you added"
   ```

7. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

8. **Create a Pull Request** on GitHub

### Pull Request Guidelines

- **Fill out the PR template completely**
- **Reference related issues** using keywords like "Fixes #123"
- **Include screenshots** for UI changes
- **Ensure all tests pass**
- **Keep PRs focused** - one feature or bug fix per PR
- **Write clear commit messages**
- **Update documentation** as needed

#### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] I have tested this manually

## Checklist
- [ ] My code follows the style guidelines of this project
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings

## Screenshots (if applicable)
Add screenshots to help explain your changes.

## Additional Notes
Any additional information that reviewers should know.
```

## 📝 Style Guidelines

### Python Code Style

We follow **PEP 8** with some modifications:

- **Line length**: 88 characters (Black formatter default)
- **Indentation**: 4 spaces
- **Quotes**: Double quotes for strings
- **Imports**: Use absolute imports, group imports logically

#### Code Formatting

We use **Black** for code formatting:

```bash
# Install Black
pip install black

# Format your code
black .

# Check formatting
black --check .
```

#### Linting

We use **flake8** for linting:

```bash
# Install flake8
pip install flake8

# Run linting
flake8 .
```

### JavaScript/HTML/CSS

- **Indentation**: 2 spaces
- **Semicolons**: Always use semicolons
- **Quotes**: Single quotes for JavaScript, double quotes for HTML attributes

### Commit Message Guidelines

Format: `<type>(<scope>): <description>`

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(challenges): add new challenge template system
fix(scoreboard): resolve real-time update issue
docs(readme): update installation instructions
```

### Documentation Style

- Use clear, concise language
- Include code examples where helpful
- Update relevant sections when making changes
- Use proper Markdown formatting

## 🧪 Testing

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=app

# Run specific test file
python -m pytest tests/test_models.py

# Run with verbose output
python -m pytest -v
```

### Writing Tests

- Place tests in the `tests/` directory
- Follow the naming convention `test_*.py`
- Write descriptive test names
- Use fixtures for common test setup
- Mock external dependencies

Example test structure:
```python
import pytest
from app import create_app, db
from app.models import User

class TestUserModel:
    def test_user_creation(self):
        """Test that a user can be created successfully."""
        user = User(username="testuser", email="test@example.com")
        assert user.username == "testuser"
        assert user.email == "test@example.com"
```

## 📚 Documentation

### Types of Documentation

1. **Code Comments**: For complex logic
2. **Docstrings**: For functions, classes, and modules
3. **README**: Project overview and setup
4. **API Documentation**: Endpoint documentation
5. **User Guide**: How to use the platform

### Docstring Format

Use Google-style docstrings:

```python
def calculate_score(attack_points, defense_points, sla_penalty):
    """Calculate the total score for a team.
    
    Args:
        attack_points (int): Points earned from attacks
        defense_points (int): Points earned from defense
        sla_penalty (int): Points deducted for SLA violations
        
    Returns:
        int: The total calculated score
        
    Raises:
        ValueError: If any points are negative
    """
    if any(x < 0 for x in [attack_points, defense_points, sla_penalty]):
        raise ValueError("Points cannot be negative")
    
    return attack_points + defense_points - sla_penalty
```

## 🏗️ Project Structure

Understanding the codebase structure:

```
adCTF/
├── app/                    # Main application code
│   ├── __init__.py        # App factory
│   ├── models.py          # Database models
│   ├── views.py           # Route handlers
│   └── controllers/       # Business logic
├── templates/             # Jinja2 templates
├── static/               # CSS, JavaScript, images
├── tests/                # Test files
├── participant-node/     # Participant node code
├── docker-compose.yaml   # Docker configuration
├── requirements.txt      # Python dependencies
└── run.py               # Application entry point
```

## 🌐 Community

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and ideas
- **Email**: For sensitive security issues

### Getting Help

If you need help:

1. Check the documentation first
2. Search existing issues
3. Ask in GitHub Discussions
4. Create a new issue with the question label

### Recognition

Contributors are recognized in:
- The project README
- Release notes
- Annual contributor acknowledgments

## 🎯 Development Priorities

Current focus areas:

1. **Performance improvements**
2. **Better test coverage**
3. **Enhanced documentation**
4. **New challenge types**
5. **UI/UX improvements**
6. **Security enhancements**

## 📈 Release Process

1. Features are developed in feature branches
2. PRs are reviewed and merged to main
3. Releases are tagged with semantic versioning
4. Release notes are generated
5. Docker images are built and published

## 🙏 Thank You

Thank you for contributing to adCTF! Your efforts help make Attack Defense CTFs more accessible to everyone in the security community.

---

*This contributing guide is adapted from open source best practices and may be updated as the project evolves.*
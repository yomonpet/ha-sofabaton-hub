# Contributing to Sofabaton Hub Integration

Thank you for your interest in contributing to the Sofabaton Hub integration for Home Assistant! 🎉

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Coding Guidelines](#coding-guidelines)
- [Submitting Changes](#submitting-changes)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Enhancements](#suggesting-enhancements)

---

## 📜 Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to uphold this code. Please be respectful and constructive in all interactions.

---

## 🤝 How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce** the issue
- **Expected behavior** vs **actual behavior**
- **Home Assistant version**
- **Integration version**
- **Relevant logs** (enable debug logging)
- **Configuration** (remove sensitive data)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Clear title and description**
- **Use case** - why is this enhancement useful?
- **Proposed solution** (if you have one)
- **Alternative solutions** you've considered
- **Additional context** (screenshots, examples, etc.)

### Pull Requests

We actively welcome your pull requests:

1. Fork the repository
2. Create a new branch from `main`
3. Make your changes
4. Test thoroughly
5. Update documentation
6. Submit a pull request

---

## 🛠️ Development Setup

### Prerequisites

- Python 3.11 or higher
- Home Assistant development environment
- MQTT broker (Mosquitto recommended)
- Sofabaton Hub device (for testing)

### Setup Steps

1. **Clone the repository**:
```bash
git clone https://github.com/YOUR_USERNAME/ha-sofabaton-hub.git
cd ha-sofabaton-hub
```

2. **Create a virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install homeassistant
```

4. **Link to Home Assistant**:
```bash
# Create symlink to your HA config directory
ln -s $(pwd)/custom_components/sofabaton_hub ~/.homeassistant/custom_components/sofabaton_hub
```

5. **Enable debug logging** in `configuration.yaml`:
```yaml
logger:
  default: info
  logs:
    custom_components.sofabaton_hub: debug
```

6. **Restart Home Assistant**

---

## 📝 Coding Guidelines

### Python Code Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use [Black](https://github.com/psf/black) for code formatting
- Use type hints where possible
- Write docstrings for all functions and classes
- Keep functions small and focused

### Example:

```python
async def async_example_function(
    hass: HomeAssistant,
    entity_id: str,
) -> dict[str, Any]:
    """
    Example function with proper typing and docstring.
    
    Args:
        hass: Home Assistant instance
        entity_id: Entity ID to process
        
    Returns:
        Dictionary with processed data
        
    Raises:
        ValueError: If entity_id is invalid
    """
    # Implementation here
    pass
```

### JavaScript Code Style

- Use ES6+ features
- Use `const` and `let`, avoid `var`
- Use arrow functions where appropriate
- Add comments for complex logic
- Follow Lit element best practices

### Commit Messages

- Use clear, descriptive commit messages
- Start with a verb in present tense (Add, Fix, Update, etc.)
- Reference issue numbers when applicable

Examples:
```
Add support for custom key layouts
Fix WebSocket connection timeout issue
Update documentation for MQTT configuration
Refactor coordinator data handling (#123)
```

---

## 🧪 Testing

### Manual Testing

Before submitting a PR, test:

1. **Fresh installation** - Remove and reinstall the integration
2. **Configuration flow** - Test both auto-discovery and manual setup
3. **All features** - Test activity switching, key control, etc.
4. **Error handling** - Test with MQTT offline, hub offline, etc.
5. **Frontend** - Test both cards in different browsers
6. **Upgrade path** - Test upgrading from previous version

### Debug Logging

Enable debug logging to help identify issues:

```yaml
logger:
  default: info
  logs:
    custom_components.sofabaton_hub: debug
```

Check logs in: **Settings** → **System** → **Logs**

---

## 📤 Submitting Changes

### Pull Request Process

1. **Update documentation** - Update README.md, CHANGELOG.md, etc.
2. **Test thoroughly** - Ensure all features work as expected
3. **Follow code style** - Run linters and formatters
4. **Write clear description** - Explain what and why
5. **Link related issues** - Reference issue numbers

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tested on Home Assistant version: X.X.X
- [ ] Tested fresh installation
- [ ] Tested upgrade path
- [ ] Tested all affected features

## Checklist
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] No breaking changes (or documented)
- [ ] All tests pass
```

---

## 🐛 Reporting Bugs

### Before Submitting

1. **Check existing issues** - Your bug might already be reported
2. **Update to latest version** - Bug might be fixed
3. **Enable debug logging** - Gather relevant logs
4. **Test in safe mode** - Disable other custom components

### Bug Report Template

```markdown
## Description
Clear description of the bug

## Steps to Reproduce
1. Go to '...'
2. Click on '...'
3. See error

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- Home Assistant version: X.X.X
- Integration version: X.X.X
- MQTT broker: Mosquitto X.X
- Browser: Chrome/Firefox/Safari

## Logs
```
Paste relevant logs here (enable debug logging)
```

## Additional Context
Screenshots, configuration, etc.
```

---

## 💡 Suggesting Enhancements

### Enhancement Template

```markdown
## Feature Description
Clear description of the proposed feature

## Use Case
Why is this feature useful?

## Proposed Solution
How should this feature work?

## Alternatives Considered
Other approaches you've thought about

## Additional Context
Mockups, examples, etc.
```

---

## 📚 Resources

- [Home Assistant Developer Docs](https://developers.home-assistant.io/)
- [Home Assistant Architecture](https://developers.home-assistant.io/docs/architecture_index)
- [Integration Quality Scale](https://www.home-assistant.io/docs/quality_scale/)
- [HACS Documentation](https://hacs.xyz/docs/publish/start)

---

## 🙏 Thank You!

Your contributions make this project better for everyone. We appreciate your time and effort!

---

## 📞 Contact

- **Issues**: https://github.com/YOUR_USERNAME/ha-sofabaton-hub/issues
- **Discussions**: https://github.com/YOUR_USERNAME/ha-sofabaton-hub/discussions
- **Email**: your.email@example.com (optional)

---

**Happy Contributing! 🚀**


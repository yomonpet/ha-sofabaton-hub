# 🧪 Sofabaton Hub Testing Guide

This guide explains how to run tests for the Sofabaton Hub integration.

---

## 📋 Prerequisites

### 1. Install Test Dependencies

```bash
pip install pytest pytest-homeassistant-custom-component pytest-cov
```

Or if you have a `requirements_test.txt`:

```bash
pip install -r requirements_test.txt
```

---

## 🚀 Running Tests

### Run All Tests

```bash
pytest tests/
```

### Run Specific Test File

```bash
pytest tests/test_config_flow.py
```

### Run Specific Test Function

```bash
pytest tests/test_config_flow.py::test_user_flow_success
```

### Run with Verbose Output

```bash
pytest tests/ -v
```

### Run with Coverage Report

```bash
pytest tests/ --cov=custom_components.sofabaton_hub --cov-report=html
```

This will generate an HTML coverage report in `htmlcov/index.html`.

### Run with Coverage and Show Missing Lines

```bash
pytest tests/ --cov=custom_components.sofabaton_hub --cov-report=term-missing
```

---

## 📊 Test Structure

```
tests/
├── __init__.py                 # Test package initialization
├── conftest.py                 # Shared fixtures and configuration
├── test_init.py                # Integration setup/teardown tests
├── test_config_flow.py         # Configuration flow tests
├── test_coordinator.py         # Data coordinator tests
├── test_remote.py              # Remote entity tests
└── test_diagnostics.py         # Diagnostics tests
```

---

## 🎯 Test Coverage Goals

For Home Assistant Core submission, we need:

- **Minimum 90% code coverage**
- All critical paths tested
- Error handling tested
- Edge cases covered

### Current Test Coverage

Run this command to check current coverage:

```bash
pytest tests/ --cov=custom_components.sofabaton_hub --cov-report=term
```

---

## 📝 Writing New Tests

### Test File Template

```python
"""Test the Sofabaton Hub [component name]."""
from __future__ import annotations

import pytest
from homeassistant.core import HomeAssistant


async def test_something(hass: HomeAssistant, setup_integration) -> None:
    """Test something specific."""
    # Arrange
    # ... setup test data
    
    # Act
    # ... perform action
    
    # Assert
    # ... verify results
    assert True
```

### Using Fixtures

Common fixtures available in `conftest.py`:

- `hass` - Home Assistant instance
- `mock_config_entry` - Mock configuration entry
- `mock_mqtt_client` - Mock MQTT client
- `mock_api_client` - Mock API client
- `mock_coordinator` - Mock coordinator
- `setup_integration` - Fully set up integration
- `mock_activity_list_payload` - Sample activity list data
- `mock_activity_status_payload` - Sample activity status data
- `mock_assigned_keys_payload` - Sample assigned keys data
- `mock_macro_keys_payload` - Sample macro keys data
- `mock_favorite_keys_payload` - Sample favorite keys data

Example:

```python
async def test_with_fixtures(
    hass: HomeAssistant,
    setup_integration,
    mock_api_client,
) -> None:
    """Test using fixtures."""
    # Integration is already set up
    # mock_api_client is available for assertions
    
    mock_api_client.async_publish_message.assert_called()
```

---

## 🐛 Debugging Tests

### Run Tests with Print Statements

```bash
pytest tests/ -s
```

The `-s` flag allows print statements to show in output.

### Run Tests with PDB Debugger

```bash
pytest tests/ --pdb
```

This will drop into the debugger on test failures.

### Run Only Failed Tests

```bash
pytest tests/ --lf
```

---

## ✅ Pre-Commit Checklist

Before committing code, run:

```bash
# 1. Run all tests
pytest tests/

# 2. Check coverage
pytest tests/ --cov=custom_components.sofabaton_hub --cov-report=term-missing

# 3. Ensure coverage is above 90%
# If not, add more tests!
```

---

## 📚 Additional Resources

- [Home Assistant Testing Documentation](https://developers.home-assistant.io/docs/development_testing)
- [pytest Documentation](https://docs.pytest.org/)
- [pytest-homeassistant-custom-component](https://github.com/MatthewFlamm/pytest-homeassistant-custom-component)

---

## 🎯 Next Steps

1. **Run existing tests** to ensure they pass
2. **Add more tests** to increase coverage
3. **Test edge cases** and error conditions
4. **Achieve 90%+ coverage** for HA Core submission

---

## 💡 Tips

- Write tests as you write code (TDD approach)
- Test both success and failure cases
- Mock external dependencies (MQTT, network calls)
- Keep tests simple and focused
- Use descriptive test names
- Add docstrings to explain what each test does

---

**Happy Testing!** 🚀


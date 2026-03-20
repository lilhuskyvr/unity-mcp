---
name: 'Testing Conventions'
description: 'How to write and run tests for the Python MCP server'
applyTo: 'Server/tests/**'
---
# Testing Conventions

## Running Tests

```bash
# All tests
cd Server && uv run pytest tests/ -v

# Single file
cd Server && uv run pytest tests/test_manage_material.py -v

# Single test by name
cd Server && uv run pytest tests/ -k "test_create_material" -v
```

## Test Structure

Tests live in `Server/tests/`. Each tool gets its own test file: `test_manage_<domain>.py`.

## Shared Fixtures

`Server/tests/conftest.py` contains shared pytest fixtures. Use them instead of duplicating setup logic.

## Test Requirements

- Every new tool needs tests.
- Every new feature needs tests.
- Run tests before submitting PRs.

## Unity Tests

Unity-side tests live in `TestProjects/UnityMCPTests/Assets/Tests/`. Open the project in Unity and use the Test Runner window.

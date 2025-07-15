# MCP Agents

A Python project for MCP (Model Context Protocol) agents.

## Requirements

- Python 3.13+

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
- On Windows:
  ```bash
  venv\Scripts\activate
  ```
- On macOS/Linux:
  ```bash
  source venv/bin/activate
  ```

3. Install the package in development mode:
```bash
pip install -e .
```

4. Install development dependencies:
```bash
pip install -e ".[dev]"
```

## Development

### Code Formatting
```bash
black src tests
isort src tests
```

### Linting
```bash
flake8 src tests
mypy src
```

### Testing
```bash
pytest
```

### Running Tests with Coverage
```bash
pytest --cov=src --cov-report=html
```

## Project Structure

```
mcp-agents/
├── src/
│   └── mcp_agents/
│       └── __init__.py
├── tests/
│   └── __init__.py
├── pyproject.toml
├── README.md
└── .gitignore
```

## License

MIT License

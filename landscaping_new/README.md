# Landscaping Management System

A comprehensive landscaping business management system with integrated AI assistant capabilities.

## Overview

This system provides a complete solution for managing a landscaping business, including:
- Customer management
- Job scheduling and tracking
- Staff management
- Invoicing and payments
- Time tracking
- AI-powered assistance

## Architecture

The system follows a modular architecture with clear separation of concerns:

- **app/**: Streamlit-based web application
- **brain/**: AI assistant and tool system
- **database/**: Database layer with query modules
- **components/**: Reusable UI components
- **services/**: Business logic services
- **docs/**: Documentation

## Key Features

### AI Assistant
- Natural language interface to system functions
- Tool-based architecture for safe operations
- Risk-tier classification for operations
- Audit logging for all actions

### Database Layer
- Facade pattern for clean separation
- Modular query modules
- Connection pooling
- Audit trails

### Authentication & Authorization
- Role-based access control
- Secure password handling
- Session management
- Permission system

## Quick Setup

**1. Install dependencies:**
```bash
pip install -r requirements.txt
```

**2. Initialize the database:**
```bash
python3 init_db_script.py
python3 force_admin_reset.py
```

**3. Run the system:**
```bash
python3 run_system.py
```

**4. Open http://localhost:8501 in your browser.**

---

## Main Entry Points

| Entry Point | Description |
|-------------|-------------|
| `run_system.py` | Main admin interface |
| `app/pages/` | Streamlit UI pages |
| `brain/tools/` | LLM tools |
| `database/queries/` | Database queries |

---

## Navigation Tips

| Area | Location |
|------|----------|
| UI pages | `app/pages/` |
| Business logic | `services/` and `database/queries/` |
| LLM brains and tools | `brain/` |

---

## LLM Integration

The system is designed for safe, modular code editing via LLMs.

- Use the **Brain pipeline** for multi-step code generation and review
- **Audit logs** and **risk-tier gating** ensure safe changes

---

## Useful Links

| Document | Description |
|----------|-------------|
| [README.md](../README.md) | Main project documentation |
| [FEATURE_MAP.md](../FEATURE_MAP.md) | Feature-to-file mapping |

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Errors | Enable debug mode |
| Change history | Check audit logs |
| Can't login | Run `python3 force_admin_reset.py` |

## Architecture Rules

This system follows strict architectural rules:

1. **Facade Pattern**: `db.py` acts as a switchboard, delegating to specific query modules without running SQL directly
2. **No Circular Imports**: Query modules must never import from `db.py`
3. **Modular Design**: Each module has a single responsibility
4. **Security First**: All user inputs are validated, SQL queries are parameterized
5. **Audit Everything**: All significant operations are logged

## AI Brain System

The AI brain system implements a 6-step linear pipeline:
1. Deliberation: Think about the problem
2. Architect: Design the solution structure
3. Scaffold: Add error handling and flow control
4. Logic: Implement business logic
5. Integration: Wire components together
6. Review: Audit for quality and security

Each step is validated before proceeding to the next, ensuring safe AI-assisted operations.

## Contributing

When adding new features:
1. Follow the existing architectural patterns
2. Add to the appropriate module (not misc.py)
3. Include proper error handling
4. Add audit logging where appropriate
5. Write tests for new functionality
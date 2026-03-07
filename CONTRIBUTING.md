# 🤝 Contributing to Veryfyn Tracking System

Thank you for your interest in contributing to Veryfyn! This document provides guidelines and workflows for contributors.

---

## 🚨 MANDATORY RULES FOR ALL CONTRIBUTORS

**These rules apply to ALL contributors (LLMs and humans):**

### 1. Read ALL Referenced Documentation
- Whenever documentation references another file, you MUST open and read that file.
- Do not skip any referenced documentation before proceeding.

### 2. Follow Project Conventions
- Use only documented directories and file structures.
- Never invent new paths without explicit instruction.
- **Python-First (LANG_001):** All new features in Python/Streamlit only.

### 3. Check Before You Change
- Confirm correct location and naming before making changes.
- Search the workspace if unsure about existing structures.

### 4. Single-Page Modification Rule (MOD_001)
- Only modify the specific file you're working on.
- Never modify multiple pages in a single task unless required.

### 5. Document Your Steps
- Update relevant documentation as part of your workflow.
- Add entries to `decisions.log` for architectural choices.

---

## 🚦 Getting Started

### Prerequisites
- Python 3.10+
- SQLite3
- Git

### Initial Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd tracking-system
   ```

2. **Create virtual environment (MANDATORY):**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\Activate.ps1
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Read required documentation:**
   - [`AI_START_HERE.md`](AI_START_HERE.md) - Entry point and rules
   - [`CONTEXT.md`](CONTEXT.md) - Master reference
   - [`PROJECT_RULES.md`](PROJECT_RULES.md) - Coding standards
   - [`GETTING_STARTED.md`](GETTING_STARTED.md) - Onboarding guide

---

## 📐 Development Workflow

### Before Starting Any Task

1. **Load context:**
   ```
   Read: AI_START_HERE.md → CONTEXT.md → session.json
   ```

2. **Check current state:**
   - Review `session.json` for project phase status
   - Check `decisions.log` for recent choices

3. **Follow 4-Phase Workflow:**
   - **Phase 1:** Interrogation - Analyze for ambiguity
   - **Phase 2:** Translation - Create "Serious Prompt"
   - **Phase 3:** Roadmap Verification - Check dependencies
   - **Phase 4:** Execution - Implement and update memory

### Making Changes

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make targeted changes:**
   - Follow Single-Page Modification Rule
   - Use existing patterns from `patterns/` directory
   - Write docstrings for all functions

3. **Test your changes:**
   ```bash
   # Run the application
   streamlit run tracking_app/app.py
   
   # Run relevant tests
   python -m pytest brain/immune/tests/
   ```

4. **Update documentation:**
   - Update `FEATURE_MAP.md` if adding new features
   - Add entry to `decisions.log` for architectural choices
   - Update page-specific `WHAT_I_CAN_DO.md` if modifying pages

---

## 📝 Code Style Guidelines

### Python (PRIMARY)

1. **Follow PEP 8:**
   ```python
   # ✅ Good - snake_case
   def calculate_streak(habit_id: str) -> int:
       pass
   
   # ❌ Bad - camelCase
   def calculateStreak(habitId):
       pass
   ```

2. **Use type hints:**
   ```python
   def get_habit(habit_id: str) -> Optional[Habit]:
       """Retrieve a habit by ID."""
       return habits.get(habit_id)
   ```

3. **Use dataclasses for models:**
   ```python
   @dataclass
   class Habit:
       id: str
       name: str
       icon: str = "🎯"
   ```

4. **Use docstrings:**
   ```python
   def calculate_streak(habit_id: str) -> int:
       """
       Calculate the current streak for a habit.
       
       Args:
           habit_id: The unique identifier of the habit.
           
       Returns:
           The number of consecutive days completed.
       """
       pass
   ```

5. **Use f-strings:**
   ```python
   message = f"Habit '{habit.name}' completed! +{xp} XP"
   ```

### Streamlit-Specific

1. **Use st.session_state for state:**
   ```python
   if 'habits' not in st.session_state:
       st.session_state.habits = load_habits()
   ```

2. **Use st.columns for layout:**
   ```python
   col1, col2, col3 = st.columns([1, 2, 1])
   ```

3. **Use st.form for data entry:**
   ```python
   with st.form("add_habit"):
       name = st.text_input("Habit Name")
       submitted = st.form_submit_button("Add")
   ```

---

## 🧪 Testing

### Running Tests
```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest brain/immune/tests/test_fingerprinter.py

# Run with verbose output
python -m pytest -v
```

### Writing Tests
- Place tests in `tests/` directory or module-specific `tests/` folders
- Follow existing test patterns
- Use descriptive test names

---

## 📋 Pull Request Process

1. **Ensure all tests pass**
2. **Update documentation** as needed
3. **Add entry to decisions.log** for significant changes
4. **Request review** from maintainers

### PR Checklist
- [ ] Code follows PEP 8 style
- [ ] Type hints added to all functions
- [ ] Docstrings added to all functions
- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] decisions.log updated (if applicable)
- [ ] Single-page modification rule followed

---

## 🔗 Quick Reference

| Want to... | Go to... |
|------------|----------|
| **Understand project** | [`AI_START_HERE.md`](AI_START_HERE.md) |
| **See coding standards** | [`PROJECT_RULES.md`](PROJECT_RULES.md) |
| **Find a feature** | [`FEATURE_MAP.md`](FEATURE_MAP.md) |
| **See patterns** | [`patterns/`](patterns/) |
| **Check current state** | [`session.json`](session.json) |
| **Review decisions** | [`decisions.log`](decisions.log) |

---

## ❓ Questions?

If you have questions about contributing:
1. Check the documentation listed above
2. Review existing code patterns
3. Check `decisions.log` for architectural context

---

**Last Updated:** March 7, 2026
**Version:** 1.0.0
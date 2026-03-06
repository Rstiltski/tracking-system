# 📋 Pattern Library - Engram Storage

**Reusable code patterns and templates for the Veryfyn Tracking System.**

---

## 🎯 Purpose

This directory stores reusable code patterns (engrams) that have been extracted from successful implementations. Patterns are like "muscle memory" - reusable structures that ensure consistency.

---

## 📁 Pattern Index

| Pattern | File | Purpose | Usage |
|---------|------|---------|-------|
| **Prompt Template** | [prompt_template.md](./prompt_template.md) | Five-Component prompt framework | Structuring AI requests |
| **Page Module** | [page_module.md](./page_module.md) | Streamlit page structure | Creating new pages |
| **Neural Hub** | [neural_hub.md](./neural_hub.md) | Central navigation | Creating neural hubs |
| **Tool Pattern** | [tool_pattern.md](./tool_pattern.md) | Brain tool structure | Creating new tools |

---

## 🧠 What is a Pattern?

A pattern is a reusable solution to a recurring problem. Each pattern includes:

1. **Context** - When to use this pattern
2. **Structure** - The code/template structure
3. **Implementation** - How to implement
4. **Examples** - Real implementations

---

## 📋 Pattern Categories

### Page Patterns
Patterns for Streamlit UI pages in `tracking_app/pages/`

| Pattern | Description |
|---------|-------------|
| Page Module | Standard page structure with session state |
| Form Page | Page with data entry forms |
| Dashboard Page | Page with metrics and charts |
| List Page | Page with CRUD operations |

### Component Patterns
Patterns for reusable UI components in `tracking_app/components/`

| Pattern | Description |
|---------|-------------|
| Card Component | Reusable card display |
| Form Component | Reusable form elements |
| Chart Component | Reusable chart displays |

### Brain Patterns
Patterns for Brain system components in `brain/`

| Pattern | Description |
|---------|-------------|
| Tool Pattern | Standard tool implementation |
| Policy Pattern | Standard policy implementation |
| State Machine | Standard state machine |

### Prompt Patterns
Patterns for AI communication (Vibe Coding)

| Pattern | Description |
|---------|-------------|
| Prompt Template | Five-Component Framework for AI requests |
| Quality Phrases | Standard phrases for quality expectations |
| Edge Case Handling | Patterns for specifying error behavior |

### Documentation Patterns
Patterns for documentation files

| Pattern | Description |
|---------|-------------|
| README Pattern | Standard README structure |
| Roadmap Pattern | Standard roadmap structure |

---

## 🔄 Creating New Patterns

When you create reusable code that:

1. Solves a common problem
2. Has been used more than once
3. Has a clear template form

**Create a pattern file:**

```markdown
# Pattern Name

## Context
When to use this pattern.

## Structure
```python
# Template code here
```

## Implementation
Step-by-step implementation guide.

## Examples
Real implementations in the project.
```

---

## 📁 Pattern Template

```markdown
# [Pattern Name]

## Context
[When to use this pattern]

## Structure
```python
# Template code
```

## Required Imports
```python
from typing import ...
from dataclasses import ...
```

## Implementation Steps
1. Step 1
2. Step 2
3. Step 3

## Example Usage
[Real example from project]

## Related Patterns
- [Pattern A](./pattern_a.md)
- [Pattern B](./pattern_b.md)

## Rules Enforced
- RULE_ID_1: Description
- RULE_ID_2: Description
```

---

## 🔗 Related Files

| File | Purpose |
|------|---------|
| [brain/CORE_RULES.md](../brain/CORE_RULES.md) | Master rule registry |
| [brain/NEURAL_HUB.md](../brain/NEURAL_HUB.md) | Central cortex |
| [brain/AI_RULES.md](../brain/AI_RULES.md) | AI thinking protocol |
| [.context.md](../.context.md) | Synapse registry |

---

**Last Updated:** March 2026  
**Maintained By:** Neural System Architect  
**Version:** 1.0.0
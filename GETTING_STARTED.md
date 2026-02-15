# 🚀 Getting Started - Personal Tracking System

## 📋 Overview

This guide will help you understand, set up, and work with the Personal Tracking System (TrackLife). Whether you're a developer, contributor, or AI assistant, follow this guide to get started.

---

## 🎯 What is TrackLife?

TrackLife is a comprehensive personal tracking system that helps you monitor and improve various aspects of your life:

- **Habits** - Build and maintain good habits with streak tracking
- **Tasks** - Manage todos with priority levels
- **Finances** - Track income, expenses, and budgets
- **Health** - Monitor weight, sleep, mood, and other metrics
- **Time** - Track how you spend your time
- **Goals** - Set and achieve personal goals
- **Achievements** - Gamified rewards for consistency

---

## 🧭 Quick Navigation

| Want to... | Go to... |
|------------|----------|
| **Get started** | [GETTING_STARTED.md](GETTING_STARTED.md) |
| **Understand rules** | [PROJECT_RULES.md](PROJECT_RULES.md) |
| **Find a feature** | [FEATURE_MAP.md](FEATURE_MAP.md) |
| **See roadmap** | [ROADMAP.md](ROADMAP.md) |
| **Check tasks** | [TODO.md](TODO.md) |
| **Read research** | [docs/research/](docs/research/) |
| **Understand Brain** | [brain/README.md](brain/README.md) |

---

## 🛠️ Setup Instructions

### Prerequisites

- **Web Browser** - Chrome, Firefox, Safari, or Edge (modern versions)
- **Code Editor** - VS Code recommended
- **Local Server** (optional) - For development

### Quick Start

1. **Open the application**
   ```bash
   # Simply open index.html in your browser
   open index.html
   
   # Or use a local server for development
   npx serve .
   # or
   python -m http.server 8000
   ```

2. **Start tracking**
   - Click on any section in the sidebar
   - Add habits, tasks, or log data
   - Watch your progress grow!

### Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd tracking-system
   ```

2. **Open in VS Code**
   ```bash
   code .
   ```

3. **Install recommended extensions**
   - Live Server (for hot reload)
   - ESLint (for code quality)
   - Prettier (for formatting)

---

## 📁 Project Structure

```
tracking-system/
├── index.html              # Main entry point
├── css/
│   └── styles.css          # All styles
├── js/                     # JavaScript modules
│   ├── app.js              # Main controller
│   ├── storage.js          # Data layer
│   ├── habits.js           # Habits module
│   ├── tasks.js            # Tasks module
│   ├── finances.js         # Finances module
│   ├── health.js           # Health module
│   ├── time.js             # Time tracking
│   ├── goals.js            # Goals module
│   ├── achievements.js     # Gamification
│   └── charts.js           # Visualizations
├── brain/                  # Python AI module
│   ├── core/               # Core components
│   ├── brains/             # Specialized brains
│   ├── tools/              # Tool definitions
│   └── design/             # Design documents
├── docs/                   # Documentation
│   ├── research/           # Research docs
│   ├── specs/              # Feature specs
│   ├── schemas/            # Data schemas
│   └── guides/             # Implementation guides
├── phases/                 # Phase docs
└── assets/                 # Static assets
```

---

## 🔄 Workflow Guide

### For New Features

1. **Check the roadmap** - See `ROADMAP.md` for current phase
2. **Read the rules** - Review `PROJECT_RULES.md`
3. **Find related code** - Use `FEATURE_MAP.md`
4. **Implement** - Follow module pattern
5. **Test** - Use the testing checklist
6. **Document** - Update relevant `.md` files

### For Bug Fixes

1. **Identify the module** - Use `FEATURE_MAP.md`
2. **Read the code** - Understand the implementation
3. **Fix the issue** - Make minimal changes
4. **Test thoroughly** - Check all affected areas
5. **Update docs** - If behavior changes

### For AI Assistants

When working on this project:

1. **Start here** - Read this file first
2. **Gather context** - Read relevant documentation
3. **Understand the user's goal** - Ask clarifying questions
4. **Plan before coding** - Break down tasks
5. **Implement carefully** - Follow PROJECT_RULES.md
6. **Explain changes** - In plain language for non-coders
7. **Suggest expansions** - Linear and non-linear ideas

---

## 📚 Documentation Guide

### Core Documents

| Document | When to Read |
|----------|--------------|
| `README.md` | First time setup |
| `PROJECT_RULES.md` | Before any coding |
| `FEATURE_MAP.md` | Finding feature locations |
| `ROADMAP.md` | Planning new features |
| `TODO.md` | Checking current tasks |

### Research Documents

Located in `docs/research/`:

| Document | Content |
|----------|---------|
| `RESEARCH_SUMMARY.md` | Overview of all research |
| `BEHAVIORAL_SCIENCE.md` | Habit formation science |
| `TECHNICAL_ARCHITECTURES.md` | System architectures |
| `OPEN_SOURCE_PROJECTS.md` | Analysis of similar projects |
| `AI_AND_PREDICTION.md` | AI and prediction features |

### Specification Documents

Located in `docs/specs/`:

| Document | Content |
|----------|---------|
| `HABIT_SCORE_SPEC.md` | Habit scoring algorithm |

### Schema Documents

Located in `docs/schemas/`:

| Document | Content |
|----------|---------|
| `EVENT_SCHEMA.md` | Event sourcing schema |

### Guide Documents

Located in `docs/guides/`:

| Document | Content |
|----------|---------|
| `INDEXEDDB_MIGRATION.md` | Storage migration guide |

---

## 🧪 Testing

### Manual Testing Checklist

Before considering any feature complete:

#### Functionality
- [ ] All CRUD operations work
- [ ] Data persists after refresh
- [ ] Navigation works correctly
- [ ] Modals open/close properly
- [ ] Forms validate input

#### UI/UX
- [ ] Responsive on all devices
- [ ] Dark mode works
- [ ] Animations are smooth
- [ ] No console errors
- [ ] Accessibility works

#### Data
- [ ] Storage operations succeed
- [ ] Migration handles old data
- [ ] Export/import works
- [ ] Reset clears all data

### Running Tests

```bash
# Run JavaScript tests
open js/tests/test-runner.html

# Run Python tests (for brain module)
cd brain
python -m pytest
```

---

## 🔧 Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Data not saving | Check localStorage quota, clear old data |
| Charts not showing | Verify Chart.js loaded, check console |
| Dark mode broken | Check `data-theme` on `<html>` element |
| App not loading | Check script order in index.html |

### Debug Mode

Open browser console and run:
```javascript
// Enable debug logging
localStorage.setItem('debug', 'true');

// View all stored data
console.log(Storage.getUserData());
console.log(Storage.getHabits());
console.log(Storage.getTasks());
```

### Reset Application

```javascript
// Clear all data (WARNING: destructive)
Storage.clearAll();
location.reload();
```

---

## 🚀 Feature Development

### Adding a New Module

1. **Create the file** - `js/newmodule.js`
2. **Follow the pattern** - See PROJECT_RULES.md
3. **Add to index.html** - Include script tag
4. **Add navigation** - Update sidebar
5. **Update FEATURE_MAP.md** - Document location
6. **Create spec** - If complex, add to docs/specs/

### Example Module Structure

```javascript
/**
 * NewModule - Description
 * Detailed description of purpose
 */

const NewModule = {
    config: {},
    items: [],
    
    init() {
        this.loadData();
        this.render();
        this.bindEvents();
    },
    
    loadData() {
        this.items = Storage.load('newmodule_items', []);
    },
    
    saveData() {
        Storage.save('newmodule_items', this.items);
    },
    
    render() {
        // Render UI
    },
    
    bindEvents() {
        // Event listeners
    }
};

window.NewModule = NewModule;
```

---

## 📈 Roadmap Summary

| Phase | Focus | Status |
|-------|-------|--------|
| 1 | Foundation | ✅ Complete |
| 2 | Core Features | ✅ Complete |
| 3 | Views & Navigation | ✅ Complete |
| 4 | Statistics | ✅ Complete |
| 5 | Gamification | ✅ Complete |
| 6 | Notifications | ✅ Complete |
| 7 | Polish | 🔄 In Progress |

See `ROADMAP.md` for detailed phase information.

---

## 🤝 Contributing

### Before Contributing

1. Read `PROJECT_RULES.md` thoroughly
2. Check `TODO.md` for current priorities
3. Review existing code style
4. Test your changes extensively

### Commit Message Format

```
type: brief description

Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation
- style: Formatting
- refactor: Code restructuring
- test: Adding tests
- chore: Maintenance
```

---

## 📞 Getting Help

### Documentation First

Before asking for help:
1. Check this guide
2. Read `PROJECT_RULES.md`
3. Search `FEATURE_MAP.md`
4. Review relevant code

### Asking Questions

When asking for help, include:
- What you're trying to achieve
- What you've already tried
- Any error messages
- Relevant code snippets

---

## 🎯 Quick Reference

### Key Files to Know

| File | Purpose |
|------|---------|
| `js/app.js` | Main application controller |
| `js/storage.js` | All data operations |
| `css/styles.css` | All styling |
| `index.html` | Main HTML structure |

### Common Operations

```javascript
// Get all habits
Storage.getHabits();

// Add a habit
Storage.addHabit({ name: 'Exercise', icon: '🏃', color: '#6366f1' });

// Log habit completion
Storage.logHabitCompletion(habitId);

// Get streak
Storage.getHabitStreak(habitId);

// Add XP
Storage.addXP(10);

// Show toast
App.showToast('Message', 'success');
```

---

*Last updated: February 2026*
*Version: 1.0.0*
# Module Management Roadmap

This roadmap outlines the steps to implement a robust, safe, and user-friendly module enable/disable system for TrackLife.

---

## Phase 1: Design & Planning ✅ COMPLETE
- [x] Define what constitutes a "module" (tracking feature, tool, etc.)
- [x] List all modules and their dependencies
- [x] Decide on config file format for enabled/disabled state

### Current Modules

| Module | Location | Status | Dependencies |
|--------|----------|--------|--------------|
| Habits | `js/habits.js` | ✅ Active | storage.js |
| Tasks | `js/tasks.js` | ✅ Active | storage.js |
| Finances | `js/finances.js` | ✅ Active | storage.js, charts.js |
| Health | `js/health.js` | ✅ Active | storage.js, charts.js |
| Time | `js/time.js` | ✅ Active | storage.js |
| Goals | `js/goals.js` | ✅ Active | storage.js |
| Achievements | `js/achievements.js` | ✅ Active | storage.js, all modules |
| Charts | `js/charts.js` | ✅ Active | Chart.js |
| Notifications | `js/notifications.js` | ✅ Active | None |
| Data Export | `js/dataExport.js` | ✅ Active | storage.js |

### Brain Modules

| Module | Location | Status | Dependencies |
|--------|----------|--------|--------------|
| Core Brain | `brain/core/` | ✅ Active | None |
| Router | `brain/core/router.py` | ✅ Active | brain.py |
| Policies | `brain/policies/` | ✅ Active | core |
| State Machines | `brain/state/` | ✅ Active | core |
| Tools | `brain/tools/` | ✅ Active | core |
| Audit | `brain/audit/` | ✅ Active | core |
| Security | `brain/security/` | ✅ Active | core |
| Invariants | `brain/invariants/` | ✅ Active | core |
| Immune System | `brain/immune/` | ✅ Active | core |
| Privacy | `brain/privacy/` | ✅ Active | core |
| Fork Engine | `brain/fork/` | ✅ Active | core |

---

## Phase 2: Backend Implementation 📋 UPCOMING
- [ ] Create `modules_config.json` for module state management
- [ ] Implement logic to load module config at startup
- [ ] Only initialize/load enabled modules
- [ ] Add dependency checks: prevent disabling a module if others depend on it
- [ ] Expose module state to the UI and brain system

### Proposed Config Structure
```json
{
  "modules": {
    "habits": {
      "enabled": true,
      "required": false,
      "dependencies": ["storage"]
    },
    "tasks": {
      "enabled": true,
      "required": false,
      "dependencies": ["storage"]
    },
    "finances": {
      "enabled": true,
      "required": false,
      "dependencies": ["storage", "charts"]
    },
    "health": {
      "enabled": true,
      "required": false,
      "dependencies": ["storage", "charts"]
    },
    "time": {
      "enabled": true,
      "required": false,
      "dependencies": ["storage"]
    },
    "goals": {
      "enabled": true,
      "required": false,
      "dependencies": ["storage"]
    },
    "achievements": {
      "enabled": true,
      "required": true,
      "dependencies": ["storage", "habits", "tasks", "finances", "health", "time", "goals"]
    }
  },
  "brain_modules": {
    "core": { "enabled": true, "required": true },
    "policies": { "enabled": true, "required": true },
    "tools": { "enabled": true, "required": true },
    "audit": { "enabled": true, "required": false },
    "security": { "enabled": true, "required": false },
    "invariants": { "enabled": true, "required": false },
    "immune": { "enabled": true, "required": false },
    "privacy": { "enabled": true, "required": false },
    "fork": { "enabled": true, "required": false }
  }
}
```

---

## Phase 3: UI Implementation 📋 FUTURE
- [ ] Add a "Module Management" section in Settings
- [ ] List all modules with enable/disable toggles
- [ ] Allow single or group selection
- [ ] Show warnings if disabling a module would break dependencies
- [ ] Save changes to module configuration

### UI Design Considerations
- Use toggle switches for enable/disable
- Color-code required modules (cannot be disabled)
- Show dependency tree on hover/click
- Provide "Reset to Defaults" button
- Include confirmation dialog for breaking changes

---

## Phase 4: Brain/Tool Integration 📋 FUTURE
- [ ] Update the Brain to only expose tools from enabled modules
- [ ] Add checks so LLMs cannot use or reference disabled modules
- [ ] Implement dynamic tool registration based on module state
- [ ] Add module state to brain context

### Tool Registration
```python
# Dynamic tool registration based on module state
def register_tools(modules_config):
    for module, config in modules_config.items():
        if config['enabled']:
            register_module_tools(module)
```

---

## Phase 5: Testing 📋 FUTURE
- [ ] Unit tests for module loading
- [ ] Integration tests for dependency checks
- [ ] UI tests for module management interface
- [ ] Test disabling/enabling modules in all combinations
- [ ] Test edge cases (circular dependencies, all off, etc.)

### Test Scenarios
1. Disable single module with no dependents
2. Attempt to disable module with dependents (should warn)
3. Disable all optional modules
4. Re-enable modules after disable
5. Reset to defaults
6. Invalid config handling

---

## Phase 6: Documentation 📋 FUTURE
- [ ] Update README.md to explain module management
- [ ] Document how to add new modules
- [ ] Document how to set dependencies
- [ ] Create user guide for module management UI

---

## Module Categories

### Core Modules (Required)
These modules are essential and cannot be disabled:
- Storage (`js/storage.js`)
- App Core (`js/app.js`)
- Achievements (`js/achievements.js`)

### Tracking Modules (Optional)
These can be enabled/disabled based on user preference:
- Habits
- Tasks
- Finances
- Health
- Time
- Goals

### Support Modules (Conditional)
These are enabled based on other module requirements:
- Charts (required by Finances, Health)
- Notifications (optional for all)
- Data Export (optional for all)

---

## Dependency Graph

```
storage.js (Required)
    ├── habits.js
    ├── tasks.js
    ├── finances.js ─── charts.js
    ├── health.js ───── charts.js
    ├── time.js
    ├── goals.js
    └── achievements.js (requires all tracking modules)

app.js (Required)
    └── All modules
```

---

## Implementation Priority

### High Priority
1. Create module configuration system
2. Implement dependency checking
3. Add UI for module management

### Medium Priority
1. Brain/tool integration
2. Dynamic loading based on config
3. Performance optimization

### Low Priority
1. Advanced dependency visualization
2. Module marketplace/gallery
3. Custom module creation UI

---

## Success Criteria

### Phase 2 Success
- [ ] Module config loads correctly
- [ ] Dependencies validated
- [ ] State exposed to application

### Phase 3 Success
- [ ] UI shows all modules
- [ ] Toggles work correctly
- [ ] Warnings display for dependencies

### Phase 4 Success
- [ ] Brain respects module state
- [ ] Tools filtered by module
- [ ] LLM cannot access disabled modules

### Phase 5 Success
- [ ] All tests pass
- [ ] Edge cases handled
- [ ] No regressions

---

## Risk Assessment

### High Risk
- Disabling critical modules accidentally
- Circular dependency issues
- Data loss when disabling modules

### Medium Risk
- Performance impact of dynamic loading
- UI complexity for non-technical users
- Configuration corruption

### Low Risk
- Module compatibility issues
- Documentation gaps
- Testing coverage

---

## Cross-References

| Document | Description |
|----------|-------------|
| [ROADMAP.md](ROADMAP.md) | Main project roadmap |
| [README.md](README.md) | Full documentation |
| [PROJECT_RULES.md](PROJECT_RULES.md) | Development guidelines |
| [FEATURE_MAP.md](FEATURE_MAP.md) | Feature-to-file mapping |

---

**Goal:** A flexible, safe module management system that allows users to customize their TrackLife experience while preventing configuration errors.

---

*Last updated: February 2026*
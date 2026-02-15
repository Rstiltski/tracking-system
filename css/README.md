# 🎨 CSS Styles - Styling & Theming

**Stylesheet organization and theming system.**

---

## Overview

The `css/` directory contains all styles for the tracking system. The stylesheet is organized by sections and supports both light and dark themes.

---

## File Structure

```
css/
└── styles.css    # All styles (organized by sections)
```

---

## Style Organization

The stylesheet is organized into sections:

```css
/* ========================================
   CSS VARIABLES (Custom Properties)
   ======================================== */
:root {
    --primary-color: #6366f1;
    --success-color: #10b981;
    --danger-color: #ef4444;
    /* ... */
}

/* ========================================
   BASE STYLES
   ======================================== */
* { box-sizing: border-box; }
body { font-family: 'Inter', sans-serif; }

/* ========================================
   LAYOUT
   ======================================== */
.sidebar { }
.main-content { }

/* ========================================
   NAVIGATION
   ======================================== */
.nav-item { }
.nav-item.active { }

/* ========================================
   DASHBOARD
   ======================================== */
.dashboard-stats { }
.stat-card { }

/* ========================================
   HABITS SECTION
   ======================================== */
.habits-container { }
.habit-item { }

/* ========================================
   TASKS SECTION
   ======================================== */
.tasks-container { }
.task-item { }

/* ========================================
   FINANCES SECTION
   ======================================== */
.finances-container { }
.transaction-item { }

/* ========================================
   HEALTH SECTION
   ======================================== */
.health-container { }
.health-entry { }

/* ========================================
   GOALS SECTION
   ======================================== */
.goals-container { }
.goal-progress { }

/* ========================================
   ACHIEVEMENTS SECTION
   ======================================== */
.achievements-container { }
.achievement-badge { }

/* ========================================
   COMPONENTS
   ======================================== */
.button { }
.modal { }
.toast { }

/* ========================================
   ANIMATIONS
   ======================================== */
@keyframes fadeIn { }
@keyframes slideIn { }

/* ========================================
   RESPONSIVE
   ======================================== */
@media (max-width: 768px) { }
@media (max-width: 480px) { }
```

---

## Theming

### Light Theme (Default)
```css
:root {
    --bg-primary: #f8fafc;
    --bg-secondary: #ffffff;
    --text-primary: #1e293b;
    --text-secondary: #64748b;
    --border-color: #e2e8f0;
}
```

### Dark Theme
```css
[data-theme="dark"] {
    --bg-primary: #0f172a;
    --bg-secondary: #1e293b;
    --text-primary: #f1f5f9;
    --text-secondary: #94a3b8;
    --border-color: #334155;
}
```

---

## Color Palette

| Purpose | Light Mode | Dark Mode |
|---------|------------|-----------|
| Primary | #6366f1 | #818cf8 |
| Success | #10b981 | #34d399 |
| Warning | #f59e0b | #fbbf24 |
| Danger | #ef4444 | #f87171 |
| Background | #f8fafc | #0f172a |
| Text | #1e293b | #f1f5f9 |

---

## Naming Convention

Use BEM-like naming:

```css
/* Block */
.habit-card { }

/* Element */
.habit-card__title { }
.habit-card__streak { }

/* Modifier */
.habit-card--completed { }
.habit-card--active { }
```

---

## Responsive Breakpoints

| Breakpoint | Device |
|------------|--------|
| < 768px | Mobile |
| 768px - 1024px | Tablet |
| > 1024px | Desktop |

---

## Animations

Keep animations under 300ms:

```css
.fade-in {
    animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}
```

Respect reduced motion:

```css
@media (prefers-reduced-motion: reduce) {
    * {
        animation-duration: 0.01ms !important;
        transition-duration: 0.01ms !important;
    }
}
```

---

## Cross-References

| Topic | File |
|-------|------|
| JavaScript modules | `js/README.md` |
| Project rules | `PROJECT_RULES.md` |
| Main README | `README.md` |

---

**Last Updated:** February 2026
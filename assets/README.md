# 📦 Assets - Static Resources

**Icons, sounds, and other static assets.**

---

## Overview

The `assets/` directory contains static resources used by the tracking system.

---

## Directory Structure

```
assets/
├── icons/     # Icon assets
└── sounds/    # Sound effects
```

---

## Icons (`icons/`)

Icon assets for the application:

| Icon | Purpose |
|------|---------|
| Various | Habit icons, achievement badges, UI icons |

### Usage

Icons are typically emoji or SVG-based for scalability:

```html
<!-- Emoji icons (recommended) -->
<span class="icon">🎯</span>
<span class="icon">💪</span>

<!-- SVG icons -->
<img src="assets/icons/habit.svg" alt="Habit">
```

---

## Sounds (`sounds/`)

Sound effects for gamification:

| Sound | Purpose |
|-------|---------|
| Achievement unlock | Played when earning achievements |
| Level up | Played when leveling up |
| Task complete | Played when completing tasks |
| Celebration | Played for special events |

### Usage

```javascript
// Play sound effect
const audio = new Audio('assets/sounds/achievement.mp3');
audio.play();
```

---

## Adding New Assets

1. **Icons**: Add to `assets/icons/`
   - Prefer SVG format for scalability
   - Keep file sizes small
   - Use descriptive names

2. **Sounds**: Add to `assets/sounds/`
   - Use MP3 or WAV format
   - Keep durations short (< 2 seconds)
   - Optimize file sizes

---

## Best Practices

1. **Optimize all assets** before adding
2. **Use descriptive filenames**
3. **Keep file sizes minimal**
4. **Prefer vector formats (SVG) for icons**
5. **Compress audio files**

---

## Cross-References

| Topic | File |
|-------|------|
| JavaScript modules | `js/README.md` |
| CSS styles | `css/README.md` |
| Main README | `README.md` |

---

**Last Updated:** February 2026
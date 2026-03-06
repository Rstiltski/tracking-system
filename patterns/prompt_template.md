# Prompt Template Pattern

**The Perfect Prompt Template for AI Coding Assistants**

---

## Context

Use this template structure for all prompts to AI coding assistants. Fill in each section with as much detail as possible. Not every section applies to every project, but addressing each relevant section significantly improves results.

---

## The Perfect Prompt Template

```markdown
## PURPOSE
[What problem does this solve? Who benefits? What defines success?]

## USERS
[Who will use this? What are their characteristics? What devices/contexts?]

## FEATURES
[What specifically should users be able to do? List each feature with details]

## DESIGN PREFERENCES
[What should it look/feel like? Reference examples if helpful]

## CONSTRAINTS
[What limitations exist? What must it work with? What should it NOT do?]

## QUALITY STANDARDS
[How polished should it be? What level of completeness?]

## EDGE CASES
[What could go wrong? How should errors be handled?]
```

---

## Example: Portfolio Website

```markdown
## PURPOSE
Create a portfolio website for a freelance graphic designer targeting small business clients. 
The site should showcase work and convert visitors into clients.

## USERS
- Small business owners looking for design services
- Primarily accessing on desktop during work hours
- Not highly technical, need clear navigation
- Want to quickly assess the designer's style and capabilities

## FEATURES
- About Me section (professional background, design approach, experience)
- Portfolio gallery (10-15 projects with images and descriptions)
- Filter by project type (logo, branding, web design, print)
- Services page with clear pricing tiers
- Testimonials from past clients
- Contact form (name, email, project type, message)
- Social media links

## DESIGN PREFERENCES
- Creative and modern but professional
- Deep blue and white primary colors
- Accent colors from portfolio pieces
- Plenty of white space
- Clean typography
- Smooth hover effects on portfolio items

## CONSTRAINTS
- Must be mobile-responsive
- Must load quickly (optimize images)
- No JavaScript frameworks (keep it simple)
- SEO-friendly structure
- Easy to update portfolio items

## QUALITY STANDARDS
- Should look professional and production-ready
- Must work on desktop, tablet, and mobile
- Provide clear feedback for form submission
- Handle image loading gracefully
- Accessible for screen readers

## EDGE CASES
- What if portfolio has no images yet? Show placeholder
- What if contact form fails? Show helpful error message
- What if user has slow internet? Lazy load images
- What if JavaScript disabled? Core content still accessible
```

---

## Example: Task Management App

```markdown
## PURPOSE
Build a personal task management application for a busy professional who needs to track 
work tasks, personal errands, and family commitments in one place.

## USERS
- Busy professional (30-50 years old)
- Uses both desktop at work and mobile on-the-go
- Needs quick entry and retrieval
- Easily overwhelmed by complexity
- Values simplicity over advanced features

## FEATURES
- Create tasks with due dates and priorities
- Organize tasks into custom categories (work, personal, family)
- Set recurring tasks for regular responsibilities
- Receive reminder notifications
- Mark tasks complete with satisfying visual confirmation
- Quick task entry
- Task search functionality
- Daily focus view (today's priorities only)

## DESIGN PREFERENCES
- Clean and minimalist interface
- Calming color scheme (soft blues and grays)
- Reduce cognitive load
- Satisfying completion animation
- Easy to scan quickly

## CONSTRAINTS
- Data must persist between sessions
- Must work on both desktop and mobile browsers
- No login required (single-user, local storage)
- Must work offline

## QUALITY STANDARDS
- Should feel intuitive without tutorial
- Provide clear feedback for all actions
- Should handle errors gracefully
- Load quickly even with many tasks

## EDGE CASES
- What if storage is full? Alert user, offer export
- What if due date passes? Show overdue clearly
- What if too many tasks? Enable filtering/hiding
- What if browser closes unexpectedly? Auto-save continuously
```

---

## Quick Reference: Quality Phrases

Include these phrases to communicate quality expectations:

| Quality Aspect | Required Phrase |
|----------------|-----------------|
| Visual Polish | "Should look professional and production-ready, not like a prototype" |
| Responsiveness | "Must work well on desktop, tablet, and mobile devices" |
| Error Handling | "Should handle errors gracefully with helpful user-friendly messages" |
| User Feedback | "Provide clear visual feedback for all user actions (loading states, success confirmations, errors)" |
| Performance | "Should load quickly and feel responsive, even on slower connections" |
| Accessibility | "Should be usable by people using screen readers and other assistive technologies" |

---

## Common Mistakes to Avoid

### 1. The Simplicity Trap

| ❌ Don't Say | ✅ Do Say |
|--------------|-----------|
| "Simple website" | "Clean, professional website with essential features: home, about, contact" |
| "Basic feature" | "Core feature with essential functionality: X, Y, Z" |
| "Just a button" | "Interactive button with hover state, click feedback, and clear labeling" |

### 2. Describing Output Instead of Outcome

| ❌ Don't Say | ✅ Do Say |
|--------------|-----------|
| "Use React" | "Build an interactive dashboard that updates in real-time" |
| "Make a REST API" | "Enable data storage and retrieval for user preferences" |
| "Add a database" | "Store user data persistently so it survives page refreshes" |

### 3. Neglecting Edge Cases

Always add:
- "Should handle errors gracefully with helpful messages"
- "Should validate user input and explain what's wrong"
- "Should work even with slow internet connections"

---

## Rules Enforced

| Rule ID | Description |
|---------|-------------|
| AI_001 | Always use Five-Component Framework |
| AI_002 | Never use "simple" without definition |
| AI_003 | Always specify quality standards |
| AI_004 | Always include edge case handling |
| AI_005 | Focus on outcomes, not implementation |

---

## Related Patterns

- [Page Module Pattern](./page_module.md) - For creating new pages
- [Neural Hub Pattern](./neural_hub.md) - For navigation structure

---

**Last Updated:** March 2026  
**Version:** 1.0.0
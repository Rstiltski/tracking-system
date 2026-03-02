#!/usr/bin/env python3
"""Test script to verify all page modules can be imported."""

import sys

modules = [
    'tracking_app.pages.habits',
    'tracking_app.pages.dashboard',
    'tracking_app.pages.goals',
    'tracking_app.pages.tasks',
    'tracking_app.pages.time',
    'tracking_app.pages.finances',
    'tracking_app.pages.health',
    'tracking_app.pages.achievements',
    'tracking_app.pages.insights',
    'tracking_app.pages.challenges',
    'tracking_app.pages.backup_restore',
    'tracking_app.pages.data_export',
    'tracking_app.pages.data_import',
    'tracking_app.pages.data_lifecycle',
    'tracking_app.pages.emotional_health',
    'tracking_app.pages.friends',
    'tracking_app.pages.goal_alerts',
    'tracking_app.pages.habit_analytics',
    'tracking_app.pages.habit_experiments',
    'tracking_app.pages.habit_reminders',
    'tracking_app.pages.leaderboards',
    'tracking_app.pages.notification_settings',
    'tracking_app.pages.rewards',
    'tracking_app.pages.stacks',
    'tracking_app.pages.task_alerts',
    'tracking_app.pages.template_sharing',
    'tracking_app.pages.weekly_review',
]

errors = []
passed = 0

for mod in modules:
    try:
        __import__(mod)
        print(f'✓ {mod}')
        passed += 1
    except Exception as e:
        errors.append((mod, str(e)))
        print(f'✗ {mod}: {e}')

print(f'\n--- Summary ---')
print(f'Passed: {passed}/{len(modules)}')
if errors:
    print('Errors:')
    for mod, err in errors:
        print(f'  {mod}: {err}')
    sys.exit(1)
else:
    print('All imports successful!')
    sys.exit(0)
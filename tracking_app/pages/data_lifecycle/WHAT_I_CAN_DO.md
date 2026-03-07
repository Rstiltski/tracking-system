# 🎯 What I Can Do - Data Lifecycle Page

## Purpose
Manage the lifecycle of your data - set retention policies, archive old data, and manage storage.

---

## ✅ User Interactions

### Actions I Can Perform

| Action | How | Result |
|--------|-----|--------|
| **Set retention** | Configure policies | Auto-delete after period |
| **Archive data** | Click "Archive" | Move data to archive |
| **Delete data** | Select and delete | Permanently remove data |
| **View storage** | Check storage section | See data usage |

---

## 📊 Data Displayed

### Retention Policies
| Data Type | Retention Period | Action |
|-----------|------------------|--------|
| **Habit Entries** | Default: Forever | Archive or delete |
| **Task History** | Default: 1 year | Archive or delete |
| **Health Data** | Default: Forever | Archive or delete |
| **Financial Data** | Default: Forever | Archive or delete |

### Storage Usage
- **Total Size**: Overall data size
- **By Type**: Size per data category
- **Archive Size**: Archived data size
- **Available Space**: Remaining capacity

---

## 🔗 Navigation

### Where I Can Go From Here
- **Data Export** (`data_export.py`) - Export data
- **Backup & Restore** (`backup_restore.py`) - Backup data

---

## ⚡ Quick Tips

1. **Set Policies**: Configure retention for auto-cleanup
2. **Archive First**: Archive before deleting
3. **Check Storage**: Monitor storage usage
4. **Keep Important**: Don't auto-delete critical data

---

**Related Files:** `data_lifecycle.py`, `components.py`, `helpers.py`
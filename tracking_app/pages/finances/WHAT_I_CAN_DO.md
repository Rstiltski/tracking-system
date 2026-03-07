# 🎯 What I Can Do - Finances Page

## Purpose
Track your income and expenses, monitor your budget, and understand your spending patterns through category breakdowns.

---

## ✅ User Interactions

### Actions I Can Perform

| Action | How | Result |
|--------|-----|--------|
| **Add transaction** | Fill form, click "Add Transaction" | Transaction recorded |
| **Delete transaction** | Click 🗑️ button | Transaction permanently removed |
| **Filter by period** | Select time period dropdown | Shows transactions for that period |
| **Filter by type** | Select type dropdown | Shows only income or expenses |

### Forms I Can Fill

**Add Transaction Form:**
- **Description**: What the transaction is for (required)
- **Amount**: Transaction amount (required)
- **Type**: Income or Expense
- **Category**: Transaction category (changes based on type)
- **Date**: When the transaction occurred
- **Notes**: Optional additional details

### Buttons I Can Click

| Button | What It Does |
|--------|--------------|
| Add Transaction | Save the new transaction |
| 🗑️ (Delete) | Delete transaction immediately |

---

## 📊 Data Displayed

### Financial Summary
| Metric | Description |
|--------|-------------|
| **💰 Income** | Total income for selected period |
| **💸 Expenses** | Total expenses for selected period |
| **⚖️ Balance** | Income minus expenses |

### Category Breakdown
- **Expenses by Category**: Bar chart of expense categories
- **Income by Category**: Bar chart of income sources
- Category totals listed below each chart

### Transactions List
- **Icon**: Income (+) or Expense (-)
- **Description**: Transaction description
- **Category & Date**: Folder icon with category, calendar icon with date
- **Amount**: Positive (income) or negative (expense)

---

## 🔍 Filtering Options

| Filter | Options |
|--------|---------|
| **Time Period** | This Week, This Month, Last Month, This Year, All Time |
| **Transaction Type** | All, Income Only, Expenses Only |

---

## 🔗 Navigation

### Where I Can Go From Here
- **Dashboard** - Overview including financial summary
- **Data Export** (`data_export.py`) - Export financial data
- **Goals** (`goals.py`) - Set financial goals

---

## ⚡ Quick Tips

1. **Log Everything**: Track all transactions for accurate picture
2. **Use Categories**: Categorize for better insights
3. **Review Monthly**: Check category breakdown monthly
4. **Monitor Balance**: Keep an eye on income vs expenses
5. **Export Regularly**: Back up your financial data

---

## 📁 Transaction Categories

### Expense Categories
- Food & Dining
- Transportation
- Shopping
- Entertainment
- Bills & Utilities
- Healthcare
- Education
- Travel
- Other

### Income Categories
- Salary
- Freelance
- Investment
- Gift
- Other

---

## 📈 Transaction Types

| Type | Icon | Effect on Balance |
|------|------|-------------------|
| **Income** | 💰 | Increases balance |
| **Expense** | 💸 | Decreases balance |

---

## 💱 Currency Format

All amounts are displayed in your local currency format (e.g., $1,234.56).

---

**Related Files:** `finances.py`, `components.py`, `helpers.py`, `constants.py`, `session_state.py`
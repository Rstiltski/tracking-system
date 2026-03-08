"""
Reports Page - Advanced Reporting Dashboard

Phase 9 Task 1: Advanced Reporting Dashboard
Provides custom date range reports for habits, tasks, finances, and health.

Features:
- Custom date range picker
- Multi-category report types
- Visual charts and metrics
- Export to CSV/JSON

Usage:
    streamlit run tracking_app/pages/reports.py
"""

import streamlit as st
from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Optional
import json
import plotly.express as px
import pandas as pd

from brain.analysis.time_views import TimeViewsProcessor


def render_page():
    """Render the reports page."""
    st.title("📊 Reports Dashboard")
    st.markdown("Generate custom reports for any date range.")
    
    # Get storage from session state
    storage = st.session_state.get('storage', None)
    
    if storage is None:
        st.warning("⚠️ Storage not initialized. Please go to the Dashboard first.")
        return
    
    # Initialize processor
    processor = TimeViewsProcessor(storage=storage)
    
    # =========================================================================
    # DATE RANGE SELECTOR
    # =========================================================================
    st.subheader("📅 Select Date Range")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Quick presets
        preset = st.selectbox(
            "Quick Presets",
            ["Custom", "This Week", "Last Week", "This Month", "Last Month", "Last 7 Days", "Last 30 Days", "This Year"]
        )
    
    # Calculate dates based on preset
    today = date.today()
    
    if preset == "This Week":
        start_date = today - timedelta(days=today.weekday())
        end_date = today
    elif preset == "Last Week":
        start_date = today - timedelta(days=today.weekday() + 7)
        end_date = today - timedelta(days=today.weekday() + 1)
    elif preset == "This Month":
        start_date = date(today.year, today.month, 1)
        end_date = today
    elif preset == "Last Month":
        first_this_month = date(today.year, today.month, 1)
        last_month_end = first_this_month - timedelta(days=1)
        start_date = date(last_month_end.year, last_month_end.month, 1)
        end_date = last_month_end
    elif preset == "Last 7 Days":
        start_date = today - timedelta(days=6)
        end_date = today
    elif preset == "Last 30 Days":
        start_date = today - timedelta(days=29)
        end_date = today
    elif preset == "This Year":
        start_date = date(today.year, 1, 1)
        end_date = today
    else:
        # Custom
        start_date = today - timedelta(days=30)
        end_date = today
    
    with col2:
        start_date = st.date_input("Start Date", value=start_date, max_value=today)
    
    with col3:
        end_date = st.date_input("End Date", value=end_date, max_value=today)
    
    # Validate date range
    if start_date > end_date:
        st.error("❌ Start date must be before end date.")
        return
    
    # Calculate days in range
    days_in_range = (end_date - start_date).days + 1
    
    # =========================================================================
    # REPORT TYPE SELECTOR
    # =========================================================================
    st.subheader("📋 Report Type")
    
    report_type = st.radio(
        "Choose what to include in your report:",
        ["Habits", "Tasks", "Finances", "Health", "All"],
        horizontal=True
    )
    
    # =========================================================================
    # GENERATE REPORT
    # =========================================================================
    if st.button("🔄 Generate Report", type="primary"):
        with st.spinner("Generating report..."):
            # Build report data
            report_data = _generate_report(storage, processor, start_date, end_date, report_type)
            
            # Store in session state for export
            st.session_state.current_report = report_data
            
            # Display report
            _render_report(report_data, start_date, end_date, days_in_range)
    
    # =========================================================================
    # EXPORT OPTIONS
    # =========================================================================
    st.subheader("💾 Export Options")
    
    # Initialize report data in session state if not exists
    if 'current_report' not in st.session_state:
        st.session_state.current_report = None
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.session_state.current_report:
            # Generate CSV download
            report = st.session_state.current_report
            csv_data = _generate_csv(report)
            st.download_button(
                label="📥 Export as CSV",
                data=csv_data,
                file_name=f"veryfyn_report_{start_date}_{end_date}.csv",
                mime="text/csv"
            )
        else:
            st.button("📥 Export as CSV", disabled=True)
            st.caption("Generate a report first")
    
    with col2:
        if st.session_state.current_report:
            # Generate JSON download
            import json
            report_json = json.dumps(st.session_state.current_report, indent=2)
            st.download_button(
                label="📥 Export as JSON",
                data=report_json,
                file_name=f"veryfyn_report_{start_date}_{end_date}.json",
                mime="application/json"
            )
        else:
            st.button("📥 Export as JSON", disabled=True)
            st.caption("Generate a report first")


def _generate_report(storage, processor, start_date: date, end_date: date, report_type: str) -> Dict[str, Any]:
    """
    Generate report data for the given date range.
    
    Args:
        storage: Storage instance
        processor: TimeViewsProcessor instance
        start_date: Start of date range
        end_date: End of date range
        report_type: Type of report to generate
    
    Returns:
        Dictionary containing report data
    """
    report = {
        "date_range": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        "generated_at": datetime.now().isoformat(),
        "habits": None,
        "tasks": None,
        "finances": None,
        "health": None
    }
    
    # Get habits data
    if report_type in ["Habits", "All"]:
        habits = storage.get_habits()
        habit_data = []
        
        for habit in habits:
            # Get entries for this habit in date range
            entries = storage.get_habit_entries(habit.id)
            
            # Filter to date range
            entries_in_range = [
                e for e in entries 
                if start_date <= e.date <= end_date
            ]
            
            # Calculate completion rate
            days_in_range = (end_date - start_date).days + 1
            completion_rate = len(entries_in_range) / days_in_range if days_in_range > 0 else 0
            
            habit_data.append({
                "id": habit.id,
                "name": habit.name,
                "icon": habit.icon,
                "color": habit.color,
                "entries_count": len(entries_in_range),
                "completion_rate": round(completion_rate * 100, 1),
                "streak_current": getattr(habit, 'streak_current', 0),
                "streak_best": getattr(habit, 'streak_best', 0)
            })
        
        report["habits"] = habit_data
    
    # Get tasks data
    if report_type in ["Tasks", "All"]:
        tasks = storage.get_tasks()
        
        tasks_data = []
        for task in tasks:
            # Filter by completion in date range
            if task.completed_at:
                completed_in_range = start_date <= task.completed_at.date() <= end_date
            else:
                completed_in_range = False
            
            tasks_data.append({
                "id": task.id,
                "title": task.title,
                "priority": getattr(task, 'priority', 'medium'),
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "completed": task.completed,
                "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                "completed_in_range": completed_in_range
            })
        
        # Calculate completion stats
        completed_count = sum(1 for t in tasks_data if t["completed"])
        total_count = len(tasks_data)
        
        report["tasks"] = {
            "items": tasks_data,
            "total": total_count,
            "completed": completed_count,
            "completion_rate": round((completed_count / total_count * 100) if total_count > 0 else 0, 1)
        }
    
    # Get finances data
    if report_type in ["Finances", "All"]:
        transactions = storage.get_transactions()
        
        transactions_in_range = [
            t for t in transactions 
            if start_date <= t.date <= end_date
        ]
        
        income = sum(t.amount for t in transactions_in_range if t.amount > 0)
        expense = sum(t.amount for t in transactions_in_range if t.amount < 0)
        
        # Group by category
        by_category = {}
        for t in transactions_in_range:
            cat = getattr(t, 'category', 'Other') or 'Other'
            if cat not in by_category:
                by_category[cat] = {"income": 0, "expense": 0}
            if t.amount > 0:
                by_category[cat]["income"] += t.amount
            else:
                by_category[cat]["expense"] += abs(t.amount)
        
        report["finances"] = {
            "total_income": income,
            "total_expense": abs(expense),
            "net": income - abs(expense),
            "transaction_count": len(transactions_in_range),
            "by_category": by_category
        }
    
    # Get health data
    if report_type in ["Health", "All"]:
        health_entries = storage.get_health_entries()
        
        health_in_range = [
            e for e in health_entries 
            if start_date <= e.date <= end_date
        ]
        
        # Calculate averages
        weights = [e.weight for e in health_in_range if e.weight]
        sleeps = [e.sleep_hours for e in health_in_range if e.sleep_hours]
        moods = [e.mood for e in health_in_range if e.mood]
        
        report["health"] = {
            "entries_count": len(health_in_range),
            "avg_weight": round(sum(weights) / len(weights), 1) if weights else None,
            "avg_sleep": round(sum(sleeps) / len(sleeps), 1) if sleeps else None,
            "avg_mood": round(sum(moods) / len(moods), 1) if moods else None,
            "mood_range": {"min": min(moods) if moods else None, "max": max(moods) if moods else None}
        }
    
    return report


def _render_report(report: Dict[str, Any], start_date: date, end_date: date, days_in_range: int) -> None:
    """
    Render the report data to the page.
    
    Args:
        report: Report data dictionary
        start_date: Report start date
        end_date: Report end date  
        days_in_range: Number of days in range
    """
    st.divider()
    
    # Header
    st.markdown(f"### 📊 Report: {start_date.strftime('%B %d, %Y')} - {end_date.strftime('%B %d, %Y')}")
    st.markdown(f"**Period:** {days_in_range} days")
    
    # =========================================================================
    # MULTI-HABIT COMPARISON SECTION
    # =========================================================================
    if report.get("habits") and len(report.get("habits", [])) > 1:
        st.markdown("---")
        st.markdown("### 📈 Habit Comparison")
        
        habits = report["habits"]
        
        # Create comparison chart data
        habit_names = [h["name"] for h in habits]
        completion_rates = [h["completion_rate"] for h in habits]
        
        # Display as bar chart
        chart_df = pd.DataFrame({
            "Habit": habit_names,
            "Completion Rate (%)": completion_rates
        })
        
        fig = px.bar(
            chart_df, 
            x="Habit", 
            y="Completion Rate (%)",
            title="Habit Completion Comparison",
            color="Completion Rate (%)",
            color_continuous_scale="viridis"
        )
        fig.update_layout(yaxis_range=[0, 100])
        st.plotly_chart(fig, use_container_width=True)
        
        # Show streaks comparison
        st.markdown("#### Streak Comparison")
        streak_df = pd.DataFrame({
            "Habit": [h["name"] for h in habits],
            "Current Streak": [h["streak_current"] for h in habits],
            "Best Streak": [h["streak_best"] for h in habits]
        })
        
        fig2 = px.bar(
            streak_df,
            x="Habit",
            y=["Current Streak", "Best Streak"],
            title="Streak Comparison",
            barmode="group"
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    # =========================================================================
    # HABITS SECTION
    # =========================================================================
    if report.get("habits"):
        st.markdown("---")
        st.markdown("### ✅ Habits")
        
        habits = report["habits"]
        
        if habits:
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            
            total_habits = len(habits)
            avg_completion = sum(h["completion_rate"] for h in habits) / total_habits if total_habits > 0 else 0
            best_streak = max((h["streak_best"] for h in habits), default=0)
            total_entries = sum(h["entries_count"] for h in habits)
            
            with col1:
                st.metric("Total Habits", total_habits)
            with col2:
                st.metric("Avg Completion", f"{avg_completion:.1f}%")
            with col3:
                st.metric("Best Streak", f"{best_streak} days")
            with col4:
                st.metric("Total Completions", total_entries)
            
            # Habit details table
            habit_df = []
            for h in habits:
                habit_df.append({
                    "Habit": f"{h['icon']} {h['name']}",
                    "Completions": h["entries_count"],
                    "Rate": f"{h['completion_rate']}%",
                    "Current Streak": h["streak_current"],
                    "Best Streak": h["streak_best"]
                })
            
            if habit_df:
                st.dataframe(habit_df, use_container_width=True, hide_index=True)
        else:
            st.info("No habits found in this period.")
    
    # =========================================================================
    # TASKS SECTION
    # =========================================================================
    if report.get("tasks"):
        st.markdown("---")
        st.markdown("### 📋 Tasks")
        
        tasks_info = report["tasks"]
        
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Tasks", tasks_info["total"])
        with col2:
            st.metric("Completed", tasks_info["completed"])
        with col3:
            st.metric("Completion Rate", f"{tasks_info['completion_rate']}%")
        
        # Show task list
        if tasks_info["items"]:
            task_df = []
            for t in tasks_info["items"][:20]:  # Limit to 20
                status = "✅" if t["completed"] else "⬜"
                task_df.append({
                    "Status": status,
                    "Title": t["title"],
                    "Priority": t["priority"].upper(),
                    "Due": t["due_date"][:10] if t["due_date"] else "-"
                })
            
            if task_df:
                st.dataframe(task_df, use_container_width=True, hide_index=True)
            
            if len(tasks_info["items"]) > 20:
                st.info(f"Showing 20 of {len(tasks_info['items'])} tasks")
    
    # =========================================================================
    # FINANCES SECTION
    # =========================================================================
    if report.get("finances"):
        st.markdown("---")
        st.markdown("### 💰 Finances")
        
        finances = report["finances"]
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Income", f"${finances['total_income']:,.2f}")
        with col2:
            st.metric("Expenses", f"${finances['total_expense']:,.2f}")
        with col3:
            st.metric("Net", f"${finances['net']:,.2f}")
        with col4:
            st.metric("Transactions", finances["transaction_count"])
        
        # Category breakdown
        if finances["by_category"]:
            st.markdown("#### By Category")
            cat_data = []
            for cat, amounts in finances["by_category"].items():
                cat_data.append({
                    "Category": cat,
                    "Income": f"${amounts['income']:,.2f}",
                    "Expense": f"${amounts['expense']:,.2f}"
                })
            
            if cat_data:
                st.dataframe(cat_data, use_container_width=True, hide_index=True)
    
    # =========================================================================
    # HEALTH SECTION
    # =========================================================================
    if report.get("health"):
        st.markdown("---")
        st.markdown("### ❤️ Health")
        
        health = report["health"]
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Entries", health["entries_count"])
        with col2:
            avg_w = health["avg_weight"]
            st.metric("Avg Weight", f"{avg_w} kg" if avg_w else "-")
        with col3:
            avg_s = health["avg_sleep"]
            st.metric("Avg Sleep", f"{avg_s} hrs" if avg_s else "-")
        with col4:
            avg_m = health["avg_mood"]
            st.metric("Avg Mood", f"{avg_m}/10" if avg_m else "-")
    
    st.divider()
    st.caption(f"Report generated: {report['generated_at']}")


def _generate_csv(report: Dict[str, Any]) -> str:
    """
    Generate CSV from report data.
    
    Args:
        report: Report data dictionary
    
    Returns:
        CSV formatted string
    """
    import csv
    import io
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(["Veryfyn Report Export"])
    writer.writerow(["Date Range", f"{report['date_range']['start']} to {report['date_range']['end']}"])
    writer.writerow(["Generated", report['generated_at']])
    writer.writerow([])
    
    # Write habits
    if report.get("habits"):
        writer.writerow(["HABITS"])
        writer.writerow(["Name", "Icon", "Completions", "Completion Rate", "Current Streak", "Best Streak"])
        for h in report["habits"]:
            writer.writerow([
                h["name"], h["icon"], h["entries_count"], 
                f"{h['completion_rate']}%", h["streak_current"], h["streak_best"]
            ])
        writer.writerow([])
    
    # Write tasks
    if report.get("tasks"):
        writer.writerow(["TASKS"])
        writer.writerow(["Total", "Completed", "Completion Rate"])
        t = report["tasks"]
        writer.writerow([t["total"], t["completed"], f"{t['completion_rate']}%"])
        writer.writerow([])
    
    # Write finances
    if report.get("finances"):
        writer.writerow(["FINANCES"])
        f = report["finances"]
        writer.writerow(["Total Income", f"${f['total_income']}"])
        writer.writerow(["Total Expenses", f"${f['total_expense']}"])
        writer.writerow(["Net", f"${f['net']}"])
        writer.writerow(["Transactions", f['transaction_count']])
        writer.writerow([])
    
    # Write health
    if report.get("health"):
        writer.writerow(["HEALTH"])
        h = report["health"]
        writer.writerow(["Entries", h["entries_count"]])
        if h.get("avg_weight"):
            writer.writerow(["Avg Weight", f"{h['avg_weight']} kg"])
        if h.get("avg_sleep"):
            writer.writerow(["Avg Sleep", f"{h['avg_sleep']} hrs"])
        if h.get("avg_mood"):
            writer.writerow(["Avg Mood", f"{h['avg_mood']}/10"])
    
    return output.getvalue()


# Entry point for direct execution
if __name__ == "__main__":
    import sys
    sys.path.insert(0, ".")
    st.set_page_config(page_title="Reports - Veryfyn", page_icon="📊", layout="wide")
    render_page()

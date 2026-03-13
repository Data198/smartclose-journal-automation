"""Close Task Tracker Dashboard Page."""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.csv_handler import load_close_tasks
from components.charts import task_status_pie

st.set_page_config(page_title="Close Tracker | SmartClose", page_icon="📋", layout="wide")
st.title("📋 Month-End Close Task Tracker")
st.caption("Track close task completion and identify bottlenecks")

# Load data
close_data = load_close_tasks()
tasks = close_data["tasks"]
close_period = close_data["close_period"]

st.subheader(f"Close Period: {close_period}")

# Progress metrics
completed = sum(1 for t in tasks if t["status"] == "complete")
total = len(tasks)
in_progress = sum(1 for t in tasks if t["status"] == "in_progress")
under_review = sum(1 for t in tasks if t["status"] == "under_review")
not_started = sum(1 for t in tasks if t["status"] == "not_started")
pct_complete = completed / total * 100

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Completion", f"{pct_complete:.0f}%")
m2.metric("Complete", completed)
m3.metric("Under Review", under_review)
m4.metric("In Progress", in_progress)
m5.metric("Not Started", not_started)

# Progress bar
st.progress(pct_complete / 100)

# Status chart and category breakdown
col1, col2 = st.columns([1, 2])

with col1:
    st.plotly_chart(task_status_pie(tasks), use_container_width=True)

with col2:
    # Group by category
    st.subheader("Progress by Category")
    categories = {}
    for task in tasks:
        cat = task["category"]
        if cat not in categories:
            categories[cat] = {"total": 0, "complete": 0, "in_progress": 0, "under_review": 0, "not_started": 0}
        categories[cat]["total"] += 1
        categories[cat][task["status"]] += 1

    for cat, counts in categories.items():
        cat_pct = counts["complete"] / counts["total"] * 100
        st.markdown(f"**{cat}** — {counts['complete']}/{counts['total']} complete")
        st.progress(cat_pct / 100)

# Task detail table — Kanban-style columns
st.divider()
st.subheader("Task Board")

status_order = ["not_started", "in_progress", "under_review", "complete"]
status_labels = {
    "not_started": "🔴 Not Started",
    "in_progress": "🟡 In Progress",
    "under_review": "🟠 Under Review",
    "complete": "🟢 Complete",
}

cols = st.columns(4)
for i, status in enumerate(status_order):
    with cols[i]:
        st.markdown(f"### {status_labels[status]}")
        status_tasks = [t for t in tasks if t["status"] == status]
        for task in status_tasks:
            schedule_indicator = ""
            if task.get("actual_day") and task["actual_day"] > task["target_day"]:
                schedule_indicator = " ⚠️ Late"
            elif status in ("not_started",) and task["target_day"] <= 2:
                schedule_indicator = " ⚠️ Behind"

            st.markdown(f"""
            <div style="background: #f8f9fa; border-radius: 8px; padding: 12px; margin-bottom: 8px; border-left: 3px solid {'#28a745' if status == 'complete' else '#ffc107' if status in ('in_progress', 'under_review') else '#dc3545'};">
                <strong>{task['name']}</strong>{schedule_indicator}<br>
                <small>Owner: {task['owner']} | Day {task['target_day']}</small>
            </div>
            """, unsafe_allow_html=True)

# Timeline view
st.divider()
st.subheader("Close Timeline")
st.caption("Target completion day vs actual (green = on time, red = late)")

timeline_data = []
for task in tasks:
    status_emoji = {"complete": "✅", "under_review": "🔍", "in_progress": "⏳", "not_started": "⬜"}
    on_time = "N/A"
    if task["status"] == "complete":
        on_time = "✅ Yes" if task.get("actual_day", 99) <= task["target_day"] else "❌ No"

    timeline_data.append({
        "Status": status_emoji.get(task["status"], ""),
        "Task": task["name"],
        "Category": task["category"],
        "Owner": task["owner"],
        "Target Day": task["target_day"],
        "Actual Day": task.get("actual_day", "-"),
        "On Time": on_time,
    })

st.dataframe(pd.DataFrame(timeline_data), use_container_width=True, hide_index=True)

# Bottleneck identification
st.divider()
st.subheader("Bottleneck Identification")

late_or_behind = [t for t in tasks if
                  (t.get("actual_day") and t["actual_day"] > t["target_day"]) or
                  (t["status"] in ("not_started",) and t["target_day"] <= 2)]

if late_or_behind:
    st.warning(f"{len(late_or_behind)} task(s) are behind schedule:")
    for task in late_or_behind:
        reason = "started late" if task.get("actual_day") else "not yet started"
        st.markdown(f"- **{task['name']}** (Target: Day {task['target_day']}, {reason}) — Owner: {task['owner']}")
else:
    st.success("All tasks are on track. No bottlenecks identified.")

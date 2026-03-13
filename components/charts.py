"""Plotly chart builders for SmartClose."""

import plotly.express as px
import plotly.graph_objects as go

COLORS = {
    "primary": "#1E3A5F",
    "secondary": "#3D6B99",
    "accent": "#5BA4E6",
    "success": "#28a745",
    "danger": "#dc3545",
    "warning": "#ffc107",
}


def close_cycle_trend(metrics_df, title="Close Cycle Duration Trend"):
    """Line chart of days-to-close over time."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=metrics_df["period"], y=metrics_df["business_days_to_close"],
        mode="lines+markers", name="Actual",
        line=dict(color=COLORS["primary"], width=2.5),
    ))
    fig.add_hline(y=5, line_dash="dash", line_color=COLORS["danger"],
                  annotation_text="Target: 5 days")
    fig.update_layout(
        title=title, xaxis_title="Period", yaxis_title="Business Days",
        plot_bgcolor="rgba(0,0,0,0)", height=400,
    )
    return fig


def automation_progress_chart(metrics_df, title="Journal Entry Automation Progress"):
    """Stacked bar chart: manual vs automated JEs over time."""
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=metrics_df["period"], y=metrics_df["automated_je_count"],
        name="Automated", marker_color=COLORS["success"],
    ))
    fig.add_trace(go.Bar(
        x=metrics_df["period"], y=metrics_df["manual_je_count"],
        name="Manual", marker_color=COLORS["danger"],
    ))
    fig.update_layout(
        title=title, barmode="stack",
        xaxis_title="Period", yaxis_title="Journal Entries",
        plot_bgcolor="rgba(0,0,0,0)", height=400,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig


def hours_saved_chart(metrics_df, title="Monthly Hours Saved Through Automation"):
    """Bar chart of hours saved per month."""
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=metrics_df["period"], y=metrics_df["automation_hours_saved"],
        marker_color=COLORS["accent"],
    ))
    fig.update_layout(
        title=title, xaxis_title="Period", yaxis_title="Hours Saved",
        plot_bgcolor="rgba(0,0,0,0)", height=350,
    )
    return fig


def before_after_comparison(metrics_df, title="Before vs. After Automation"):
    """Side-by-side comparison of pre- and post-automation metrics."""
    pre = metrics_df.head(6)
    post = metrics_df.tail(6)

    categories = ["Avg Days to Close", "Avg Manual JEs", "Avg Errors", "Tasks On Time %"]
    pre_values = [
        pre["business_days_to_close"].mean(),
        pre["manual_je_count"].mean(),
        pre["errors_caught"].mean(),
        (pre["tasks_on_time"] / pre["total_tasks"] * 100).mean(),
    ]
    post_values = [
        post["business_days_to_close"].mean(),
        post["manual_je_count"].mean(),
        post["errors_caught"].mean(),
        (post["tasks_on_time"] / post["total_tasks"] * 100).mean(),
    ]

    fig = go.Figure(data=[
        go.Bar(name="Before Automation", x=categories, y=pre_values, marker_color=COLORS["danger"]),
        go.Bar(name="After Automation", x=categories, y=post_values, marker_color=COLORS["success"]),
    ])
    fig.update_layout(
        title=title, barmode="group",
        plot_bgcolor="rgba(0,0,0,0)", height=400,
    )
    return fig


def task_status_pie(tasks, title="Close Task Status"):
    """Pie chart of close task statuses."""
    status_counts = {}
    status_labels = {
        "complete": "Complete",
        "under_review": "Under Review",
        "in_progress": "In Progress",
        "not_started": "Not Started",
    }
    for task in tasks:
        status = status_labels.get(task["status"], task["status"])
        status_counts[status] = status_counts.get(status, 0) + 1

    fig = px.pie(
        values=list(status_counts.values()),
        names=list(status_counts.keys()),
        title=title,
        color=list(status_counts.keys()),
        color_discrete_map={
            "Complete": COLORS["success"],
            "Under Review": COLORS["warning"],
            "In Progress": COLORS["accent"],
            "Not Started": COLORS["danger"],
        },
        hole=0.4,
    )
    fig.update_layout(height=350)
    return fig

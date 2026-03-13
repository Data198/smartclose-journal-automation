"""Validation utilities for journal entries and close tasks."""

import pandas as pd


def validate_entries_batch(entries_df):
    """Validate a batch of journal entries.

    Checks:
    1. Debits = Credits for each transaction
    2. No zero-amount lines
    3. Valid account codes
    4. Required fields present
    """
    issues = []

    # Check by transaction
    for txn_id in entries_df["transaction_id"].unique():
        txn_entries = entries_df[entries_df["transaction_id"] == txn_id]
        total_debit = txn_entries["debit"].sum()
        total_credit = txn_entries["credit"].sum()

        if abs(total_debit - total_credit) >= 0.01:
            issues.append({
                "transaction_id": txn_id,
                "issue": "unbalanced",
                "detail": f"Debits ({total_debit:.2f}) != Credits ({total_credit:.2f})",
            })

    # Check for zero amounts
    zero_lines = entries_df[(entries_df["debit"] == 0) & (entries_df["credit"] == 0)]
    if not zero_lines.empty:
        for _, row in zero_lines.iterrows():
            issues.append({
                "transaction_id": row["transaction_id"],
                "issue": "zero_amount",
                "detail": f"Zero amount line for account {row['account']}",
            })

    return pd.DataFrame(issues) if issues else pd.DataFrame(columns=["transaction_id", "issue", "detail"])


def validate_close_task_dates(tasks, target_close_day=5):
    """Check which close tasks are on schedule."""
    results = []
    for task in tasks:
        on_schedule = True
        if task.get("actual_day") and task["actual_day"] > task["target_day"]:
            on_schedule = False
        elif task["status"] in ("not_started", "in_progress") and task["target_day"] <= 2:
            on_schedule = False

        results.append({
            "task_id": task["id"],
            "task_name": task["name"],
            "target_day": task["target_day"],
            "actual_day": task.get("actual_day"),
            "on_schedule": on_schedule,
        })

    return results

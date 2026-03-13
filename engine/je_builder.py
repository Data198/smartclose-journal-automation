"""Constructs and validates balanced journal entries."""

import pandas as pd


def validate_balance(entries_df):
    """Validate that total debits equal total credits.

    Returns (is_balanced, total_debits, total_credits, difference).
    """
    total_debits = entries_df["debit"].sum()
    total_credits = entries_df["credit"].sum()
    difference = round(abs(total_debits - total_credits), 2)
    is_balanced = difference < 0.01

    return is_balanced, round(total_debits, 2), round(total_credits, 2), difference


def summarize_by_account(entries_df):
    """Summarize journal entries by account."""
    summary = entries_df.groupby("account").agg(
        total_debit=("debit", "sum"),
        total_credit=("credit", "sum"),
        entry_count=("debit", "count"),
    ).reset_index()
    summary["net"] = summary["total_debit"] - summary["total_credit"]
    return summary.sort_values("account")


def summarize_by_rule(entries_df):
    """Summarize entries by automation rule."""
    summary = entries_df.groupby(["rule_id", "rule_name"]).agg(
        total_debit=("debit", "sum"),
        total_credit=("credit", "sum"),
        transaction_count=("transaction_id", "nunique"),
    ).reset_index()
    return summary


def create_entry_pairs(entries_df):
    """Group entries into debit/credit pairs for review."""
    pairs = []
    grouped = entries_df.groupby(["transaction_id", "entry_type"])

    for (txn_id, entry_type), group in grouped:
        debits = group[group["debit"] > 0]
        credits = group[group["credit"] > 0]

        for _, debit_row in debits.iterrows():
            for _, credit_row in credits.iterrows():
                pairs.append({
                    "transaction_id": txn_id,
                    "date": debit_row["date"],
                    "entry_type": entry_type,
                    "debit_account": debit_row["account"],
                    "credit_account": credit_row["account"],
                    "amount": debit_row["debit"],
                    "description": debit_row["description"],
                })

    return pd.DataFrame(pairs)

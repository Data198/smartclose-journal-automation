"""Journal entry automation rule engine.

Matches source transactions to accounting rules and produces balanced entries.
"""

import pandas as pd
import fnmatch


def match_rule(transaction, rules):
    """Find the matching automation rule for a transaction.

    Returns the matching rule dict or None.
    """
    txn_type = transaction.get("transaction_type", "")
    product = transaction.get("product", "")

    for rule in rules:
        trigger = rule["trigger"]

        # Check transaction type
        if trigger.get("transaction_type") and trigger["transaction_type"] != txn_type:
            continue

        # Check product pattern (supports wildcards)
        if trigger.get("product_pattern"):
            if not fnmatch.fnmatch(product, trigger["product_pattern"]):
                continue

        return rule

    return None


def calculate_amount(amount_type, transaction_amount, term_months=12):
    """Calculate the journal entry amount based on amount type."""
    if amount_type == "full":
        return transaction_amount
    elif amount_type == "full_abs":
        return abs(transaction_amount)
    elif amount_type == "monthly_proration":
        return round(transaction_amount / term_months, 2)
    else:
        return transaction_amount


def process_transactions(transactions_df, rules):
    """Apply automation rules to source transactions and generate journal entries.

    Returns:
        tuple: (journal_entries_df, processing_log)
    """
    entries = []
    log = []

    for _, txn in transactions_df.iterrows():
        rule = match_rule(txn.to_dict(), rules)

        if rule is None:
            log.append({
                "transaction_id": txn["transaction_id"],
                "status": "unmatched",
                "rule_id": None,
                "message": f"No matching rule for {txn['transaction_type']} - {txn['product']}",
            })
            continue

        # Determine term for proration
        term_months = 12  # Default annual
        if "Monthly" in str(txn.get("product", "")):
            term_months = 1

        # Generate billing entries
        je_config = rule["journal_entry"]
        if "on_billing" in je_config:
            for line in je_config["on_billing"]:
                amount = calculate_amount(line["amount"], txn["amount"], term_months)
                entries.append({
                    "transaction_id": txn["transaction_id"],
                    "date": txn["date"],
                    "customer_id": txn["customer_id"],
                    "customer_name": txn["customer_name"],
                    "rule_id": rule["rule_id"],
                    "rule_name": rule["name"],
                    "account": line["account"],
                    "debit": round(amount, 2) if line["type"] == "debit" else 0,
                    "credit": round(amount, 2) if line["type"] == "credit" else 0,
                    "description": f"{rule['description']} - {txn['product']}",
                    "entry_type": "billing",
                })

        # Generate recognition entries (for deferrals)
        if "on_recognition" in je_config:
            for line in je_config["on_recognition"]:
                amount = calculate_amount(line["amount"], txn["amount"], term_months)
                entries.append({
                    "transaction_id": txn["transaction_id"],
                    "date": txn["date"],
                    "customer_id": txn["customer_id"],
                    "customer_name": txn["customer_name"],
                    "rule_id": rule["rule_id"],
                    "rule_name": rule["name"],
                    "account": line["account"],
                    "debit": round(amount, 2) if line["type"] == "debit" else 0,
                    "credit": round(amount, 2) if line["type"] == "credit" else 0,
                    "description": f"Monthly recognition - {txn['product']}",
                    "entry_type": "recognition",
                })

        log.append({
            "transaction_id": txn["transaction_id"],
            "status": "processed",
            "rule_id": rule["rule_id"],
            "message": f"Applied {rule['name']}",
        })

    return pd.DataFrame(entries), log

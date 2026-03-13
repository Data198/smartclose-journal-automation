"""Generate sample data for SmartClose journal automation app."""

import numpy as np
import pandas as pd
import json
from pathlib import Path
from datetime import datetime

np.random.seed(42)
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)


def generate_source_transactions():
    """Generate source billing/usage transactions for JE automation."""
    customers = [
        ("C-100", "TechFlow Inc"), ("C-101", "DataSphere Ltd"),
        ("C-102", "CloudNine Corp"), ("C-103", "InnovateTech"),
        ("C-104", "Quantum Analytics"), ("C-105", "NexGen Solutions"),
        ("C-106", "AlphaWave Digital"), ("C-107", "Prisma Systems"),
        ("C-108", "Vertex AI Labs"), ("C-109", "FusionPoint"),
        ("C-110", "ClearPath Software"), ("C-111", "BlueSky Dynamics"),
        ("C-112", "Pinnacle Data"), ("C-113", "Catalyst Corp"),
        ("C-114", "Meridian Tech"),
    ]

    products = [
        ("Platform Pro Annual", "subscription_billing", "annual"),
        ("Platform Standard Monthly", "subscription_billing", "monthly"),
        ("Platform Basic Monthly", "subscription_billing", "monthly"),
        ("Implementation", "service_billing", "one_time"),
        ("API Overage", "usage_billing", "monthly"),
        ("Premium Support", "subscription_billing", "annual"),
    ]

    rows = []
    txn_id = 1
    for month in range(1, 13):  # Jan to Dec 2025
        period_start = f"2025-{month:02d}-01"
        if month == 12:
            period_end = "2025-12-31"
        else:
            period_end = f"2025-{month:02d}-28"

        for cust_id, cust_name in customers:
            for product_name, txn_type, freq in products:
                # Not all customers have all products
                if np.random.random() < 0.3:
                    continue

                if freq == "annual" and month != 1:
                    continue  # Annual only billed in Jan

                if freq == "one_time" and month != 1:
                    continue

                base_amounts = {
                    "Platform Pro Annual": 24000,
                    "Platform Standard Monthly": 2500,
                    "Platform Basic Monthly": 1200,
                    "Implementation": 8000,
                    "API Overage": np.random.uniform(500, 5000),
                    "Premium Support": 6000,
                }

                amount = round(base_amounts.get(product_name, 1000) * (1 + np.random.normal(0, 0.05)), 2)

                # Occasional refunds
                if np.random.random() < 0.03:
                    rows.append({
                        "transaction_id": f"TXN-{txn_id:04d}",
                        "date": f"2025-{month:02d}-{np.random.randint(15, 28):02d}",
                        "customer_id": cust_id,
                        "customer_name": cust_name,
                        "product": product_name,
                        "transaction_type": "subscription_refund",
                        "amount": -round(amount * np.random.uniform(0.1, 0.5), 2),
                        "currency": "USD",
                        "contract_id": f"CON-{cust_id.split('-')[1]}",
                        "period_start": period_start,
                        "period_end": period_end if freq == "monthly" else f"2025-12-31",
                    })
                    txn_id += 1

                rows.append({
                    "transaction_id": f"TXN-{txn_id:04d}",
                    "date": f"2025-{month:02d}-{np.random.randint(1, 20):02d}",
                    "customer_id": cust_id,
                    "customer_name": cust_name,
                    "product": product_name,
                    "transaction_type": txn_type,
                    "amount": amount,
                    "currency": "USD",
                    "contract_id": f"CON-{cust_id.split('-')[1]}",
                    "period_start": period_start,
                    "period_end": period_end if freq == "monthly" else f"2025-12-31",
                })
                txn_id += 1

    df = pd.DataFrame(rows)
    df.to_csv(DATA_DIR / "sample_source_transactions.csv", index=False)
    return df


def generate_automation_rules():
    """Generate journal entry automation rule definitions."""
    rules = {
        "rules": [
            {
                "rule_id": "RULE-001",
                "name": "Annual Subscription Deferral",
                "description": "Defer annual subscription billings and recognize 1/12 monthly",
                "trigger": {"transaction_type": "subscription_billing", "product_pattern": "*Annual*"},
                "journal_entry": {
                    "on_billing": [
                        {"account": "1200 - Accounts Receivable", "type": "debit", "amount": "full"},
                        {"account": "2400 - Deferred Revenue", "type": "credit", "amount": "full"}
                    ],
                    "on_recognition": [
                        {"account": "2400 - Deferred Revenue", "type": "debit", "amount": "monthly_proration"},
                        {"account": "4100 - Subscription Revenue", "type": "credit", "amount": "monthly_proration"}
                    ]
                }
            },
            {
                "rule_id": "RULE-002",
                "name": "Monthly Subscription Recognition",
                "description": "Recognize monthly subscriptions immediately upon billing",
                "trigger": {"transaction_type": "subscription_billing", "product_pattern": "*Monthly*"},
                "journal_entry": {
                    "on_billing": [
                        {"account": "1200 - Accounts Receivable", "type": "debit", "amount": "full"},
                        {"account": "4100 - Subscription Revenue", "type": "credit", "amount": "full"}
                    ]
                }
            },
            {
                "rule_id": "RULE-003",
                "name": "Usage-Based Revenue",
                "description": "Recognize usage-based charges in the period incurred",
                "trigger": {"transaction_type": "usage_billing"},
                "journal_entry": {
                    "on_billing": [
                        {"account": "1200 - Accounts Receivable", "type": "debit", "amount": "full"},
                        {"account": "4200 - Usage Revenue", "type": "credit", "amount": "full"}
                    ]
                }
            },
            {
                "rule_id": "RULE-004",
                "name": "Service Revenue Recognition",
                "description": "Recognize service revenue upon completion of delivery",
                "trigger": {"transaction_type": "service_billing"},
                "journal_entry": {
                    "on_billing": [
                        {"account": "1200 - Accounts Receivable", "type": "debit", "amount": "full"},
                        {"account": "4300 - Services Revenue", "type": "credit", "amount": "full"}
                    ]
                }
            },
            {
                "rule_id": "RULE-005",
                "name": "Refund Processing",
                "description": "Reverse revenue and reduce receivable for refunds",
                "trigger": {"transaction_type": "subscription_refund"},
                "journal_entry": {
                    "on_billing": [
                        {"account": "4100 - Subscription Revenue", "type": "debit", "amount": "full_abs"},
                        {"account": "1200 - Accounts Receivable", "type": "credit", "amount": "full_abs"}
                    ]
                }
            }
        ]
    }

    with open(DATA_DIR / "sample_automation_rules.json", "w") as f:
        json.dump(rules, f, indent=2)
    return rules


def generate_close_tasks():
    """Generate month-end close task checklist."""
    tasks = {
        "close_period": "2025-01",
        "tasks": [
            {"id": "T-001", "name": "Close Sub-Ledger: Accounts Receivable", "category": "Sub-Ledger Closes", "owner": "Revenue Team", "target_day": 1, "status": "complete", "actual_day": 1},
            {"id": "T-002", "name": "Close Sub-Ledger: Deferred Revenue", "category": "Sub-Ledger Closes", "owner": "Revenue Team", "target_day": 1, "status": "complete", "actual_day": 1},
            {"id": "T-003", "name": "Run Automated Journal Entries", "category": "Journal Entries", "owner": "Revenue Team", "target_day": 1, "status": "complete", "actual_day": 1},
            {"id": "T-004", "name": "Review & Post Automated JEs", "category": "Journal Entries", "owner": "Senior Accountant", "target_day": 2, "status": "complete", "actual_day": 2},
            {"id": "T-005", "name": "Prepare Manual Adjusting Entries", "category": "Journal Entries", "owner": "Senior Accountant", "target_day": 2, "status": "complete", "actual_day": 2},
            {"id": "T-006", "name": "Post Manual Adjusting Entries", "category": "Journal Entries", "owner": "Revenue Manager", "target_day": 2, "status": "complete", "actual_day": 2},
            {"id": "T-007", "name": "Reconcile Accounts Receivable", "category": "Reconciliations", "owner": "Revenue Team", "target_day": 2, "status": "complete", "actual_day": 2},
            {"id": "T-008", "name": "Reconcile Deferred Revenue", "category": "Reconciliations", "owner": "Revenue Team", "target_day": 2, "status": "complete", "actual_day": 3},
            {"id": "T-009", "name": "Reconcile Contract Assets", "category": "Reconciliations", "owner": "Senior Accountant", "target_day": 3, "status": "under_review", "actual_day": 3},
            {"id": "T-010", "name": "Revenue Flux Analysis - MoM", "category": "Flux Analysis", "owner": "Senior Accountant", "target_day": 3, "status": "in_progress", "actual_day": None},
            {"id": "T-011", "name": "Revenue Flux Analysis - Budget vs Actual", "category": "Flux Analysis", "owner": "Senior Accountant", "target_day": 3, "status": "not_started", "actual_day": None},
            {"id": "T-012", "name": "Prepare Management Revenue Report", "category": "Management Reporting", "owner": "Revenue Manager", "target_day": 4, "status": "not_started", "actual_day": None},
            {"id": "T-013", "name": "Prepare ASC 606 Disclosure Schedules", "category": "Management Reporting", "owner": "Senior Accountant", "target_day": 4, "status": "not_started", "actual_day": None},
            {"id": "T-014", "name": "Revenue Close Sign-Off", "category": "Management Reporting", "owner": "Controller", "target_day": 5, "status": "not_started", "actual_day": None},
        ]
    }

    with open(DATA_DIR / "sample_close_tasks.json", "w") as f:
        json.dump(tasks, f, indent=2)
    return tasks


def generate_historical_close_metrics():
    """Generate 18 months of close cycle metrics showing automation impact."""
    rows = []
    periods = pd.period_range("2023-07", "2024-12", freq="M")

    # Phase 1: Fully manual (first 6 months)
    # Phase 2: Partial automation (months 7-12)
    # Phase 3: Full automation (months 13-18)

    for i, period in enumerate(periods):
        if i < 6:
            # Manual phase
            close_days = np.random.randint(5, 8)
            manual_je = np.random.randint(130, 155)
            auto_je = 0
            errors = np.random.randint(3, 10)
            tasks_on_time = np.random.randint(30, 38)
            hours_saved = 0
        elif i < 12:
            # Transition phase
            auto_pct = (i - 5) / 7
            close_days = max(3, int(7 - auto_pct * 3) + np.random.randint(-1, 1))
            total_je = np.random.randint(140, 155)
            auto_je = int(total_je * auto_pct)
            manual_je = total_je - auto_je
            errors = max(1, int(8 * (1 - auto_pct)) + np.random.randint(-1, 2))
            tasks_on_time = min(42, 33 + int(auto_pct * 9))
            hours_saved = round(auto_pct * 22, 1)
        else:
            # Full automation
            close_days = np.random.randint(3, 5)
            total_je = np.random.randint(145, 160)
            auto_je = int(total_je * np.random.uniform(0.88, 0.95))
            manual_je = total_je - auto_je
            errors = np.random.randint(4, 9)
            tasks_on_time = np.random.randint(39, 43)
            hours_saved = round(np.random.uniform(18, 22), 1)

        close_month = period.month + 1 if period.month < 12 else 1
        close_year = period.year if period.month < 12 else period.year + 1
        close_date = f"{close_year}-{close_month:02d}-{min(close_days + 1, 28):02d}"

        rows.append({
            "period": str(period),
            "close_date": close_date,
            "business_days_to_close": close_days,
            "manual_je_count": manual_je,
            "automated_je_count": auto_je,
            "errors_caught": errors,
            "total_tasks": 42,
            "tasks_on_time": min(tasks_on_time, 42),
            "automation_hours_saved": hours_saved,
        })

    df = pd.DataFrame(rows)
    df.to_csv(DATA_DIR / "historical_close_metrics.csv", index=False)
    return df


def generate_reconciliations():
    """Generate balance sheet reconciliation status data."""
    recons = {
        "period": "2025-01",
        "reconciliations": [
            {"account": "1200 - Accounts Receivable", "gl_balance": 2850000, "sub_ledger_balance": 2850000, "variance": 0, "status": "reconciled", "preparer": "Revenue Team", "reviewer": "Senior Accountant"},
            {"account": "2400 - Deferred Revenue (Current)", "gl_balance": 1305000, "sub_ledger_balance": 1302500, "variance": 2500, "status": "variance_under_threshold", "preparer": "Revenue Team", "reviewer": "Senior Accountant"},
            {"account": "2410 - Deferred Revenue (Non-Current)", "gl_balance": 485000, "sub_ledger_balance": 485000, "variance": 0, "status": "reconciled", "preparer": "Revenue Team", "reviewer": "Senior Accountant"},
            {"account": "1300 - Contract Assets", "gl_balance": 125000, "sub_ledger_balance": 118500, "variance": 6500, "status": "variance_under_threshold", "preparer": "Senior Accountant", "reviewer": "Revenue Manager"},
            {"account": "1310 - Unbilled Revenue", "gl_balance": 95000, "sub_ledger_balance": 82000, "variance": 13000, "status": "variance_over_threshold", "preparer": "Senior Accountant", "reviewer": "Revenue Manager"},
            {"account": "4100 - Subscription Revenue", "gl_balance": 875000, "sub_ledger_balance": 875000, "variance": 0, "status": "reconciled", "preparer": "Revenue Team", "reviewer": "Senior Accountant"},
            {"account": "4200 - Usage Revenue", "gl_balance": 125000, "sub_ledger_balance": 125000, "variance": 0, "status": "reconciled", "preparer": "Revenue Team", "reviewer": "Senior Accountant"},
            {"account": "4300 - Services Revenue", "gl_balance": 48000, "sub_ledger_balance": 48000, "variance": 0, "status": "reconciled", "preparer": "Revenue Team", "reviewer": "Senior Accountant"},
        ]
    }

    with open(DATA_DIR / "sample_reconciliations.json", "w") as f:
        json.dump(recons, f, indent=2)
    return recons


if __name__ == "__main__":
    print("Generating source transactions...")
    txn = generate_source_transactions()
    print(f"  -> {len(txn)} rows")

    print("Generating automation rules...")
    rules = generate_automation_rules()
    print(f"  -> {len(rules['rules'])} rules")

    print("Generating close tasks...")
    tasks = generate_close_tasks()
    print(f"  -> {len(tasks['tasks'])} tasks")

    print("Generating historical close metrics...")
    metrics = generate_historical_close_metrics()
    print(f"  -> {len(metrics)} rows")

    print("Generating reconciliation data...")
    recons = generate_reconciliations()
    print(f"  -> {len(recons['reconciliations'])} accounts")

    print("\nAll SmartClose sample data generated successfully.")

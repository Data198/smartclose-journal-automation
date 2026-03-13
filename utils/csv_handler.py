"""CSV upload and download helpers."""

import pandas as pd
import streamlit as st
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"


@st.cache_data
def load_sample_transactions():
    return pd.read_csv(DATA_DIR / "sample_source_transactions.csv")


@st.cache_data
def load_historical_metrics():
    return pd.read_csv(DATA_DIR / "historical_close_metrics.csv")


def load_automation_rules():
    import json
    with open(DATA_DIR / "sample_automation_rules.json") as f:
        return json.load(f)


def load_close_tasks():
    import json
    with open(DATA_DIR / "sample_close_tasks.json") as f:
        return json.load(f)


def load_reconciliations():
    import json
    with open(DATA_DIR / "sample_reconciliations.json") as f:
        return json.load(f)

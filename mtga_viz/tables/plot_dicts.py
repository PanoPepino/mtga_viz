# This file contains all functions to convert tables into specific dictionaries to pass manim classes


import pandas as pd
import json
from math import tau
from pathlib import Path


def save_arch_share(
    df,
    arch_col: str = "user_deck_arch",
    colors_dict: dict | None = None,
    dropna: bool = True,
    save_path: str | None = None,
):
    """
    Build a plotting dictionary for archetype share pie chart.

    Args:
        df: Input dataframe.
        arch_col (str, optional): Column containing archetype labels.
        colors_dict (dict | None, optional): Mapping from archetype to color.
        dropna (bool, optional): Whether to ignore missing values.
        save_path (str | None, optional): Path where the resulting plot dict
            should be saved as JSON. Defaults to None.

    Returns:
        dict: Plot-ready dictionary for PieChart.
    """

    shares = (
        df[arch_col]
        .value_counts(normalize=True, dropna=dropna)
        .sort_values(ascending=False)
        .mul(100)
        .round(2)
    )

    labels = shares.index.tolist()
    shares_pct = shares.tolist()
    shares_rad = [x * tau/100 for x in shares_pct]

    plot_dict = {
        "plot_type": "arch_share",
        "source_col": arch_col,
        "labels": labels,
        "shares_pct": shares_pct,
        "shares_rad": shares_rad,
        "n": len(labels),
        "colors_dict": colors_dict or {},
    }

    if save_path is not None:
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(plot_dict, f, indent=2, ensure_ascii=False)


def save_top_n_deck_share(
    df,
    deck_col: str = "user_deck",
    top_n: int = 10,
    other_label: str = "Other",
    dropna: bool = True,
    save_path: str | None = None,
):
    """
    Build a plotting dictionary for top N deck metagame share.

    Args:
        df: Input dataframe.
        deck_col (str, optional): Column containing deck labels.
        top_n (int, optional): Number of top decks to keep before aggregating tail.
        other_label (str, optional): Label for aggregated remaining share.
        dropna (bool, optional): Whether to ignore missing values.
        save_path (str | None, optional): Path where the resulting plot dict
            should be saved as JSON. Defaults to None.

    Returns:
        dict: Plot-ready dictionary for top N deck share.
    """

    shares = (
        df[deck_col]
        .value_counts(normalize=True, dropna=dropna)
        .sort_values(ascending=False)
    )

    top = shares.iloc[:top_n].copy()

    if len(shares) > top_n:
        top.loc[other_label] = shares.iloc[top_n:].sum()

    labels = top.index.tolist()
    shares_pct = (top * 100).round(2).tolist()

    plot_dict = {
        "plot_type": "top_n_deck_share",
        "source_col": deck_col,
        "labels": labels,
        "shares_pct": (shares_pct),
        "top_n": top_n,
        "n": len(labels),
        "other_label": other_label,
    }

    if save_path is not None:
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(plot_dict, f, indent=2, ensure_ascii=False)


def save_general_data(
    df,
    time_col: str,
    save_path: str | None = None,
):
    """
    Build and optionally save for general data.

    Args:
        df: Input dataframe.
        time_col (str): Datetime column used to compute start and end date.
        save_path (str | None, optional): Path where the metadata dict
            should be saved as JSON. Defaults to None.

    Returns:
        dict: Metadata dictionary with start_date, end_date, and n_samples.
    """

    dt = pd.to_datetime(df[time_col], errors="coerce").dropna()

    meta_dict = {
        "start_date": dt.min().date().isoformat() if not dt.empty else None,
        "end_date": dt.max().date().isoformat() if not dt.empty else None,
        "n_samples": int(len(df)),
    }

    if save_path is not None:
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(meta_dict, f, indent=2, ensure_ascii=False)

# This file contains all functions to convert tables into specific dictionaries to pass manim classes


import pandas as pd
import json
from math import tau
from pathlib import Path


def save_arch_share(
    df,
    arch_col: str = "deck_name_arch",
    count_col: str = "count",
    colors_dict: dict | None = None,
    dropna: bool = True,
    save_path: str | None = None,
):
    """
    Build a plotting dictionary for archetype share pie chart from a deck-count
    table.

    This expects a DataFrame where each row is already a deck summary, e.g.:

        deck_name | count | share_pct | deck_name_arch

    Archetype share is therefore computed by summing ``count`` within each
    archetype, not by counting rows.

    Args:
        df: Input dataframe.
        arch_col (str, optional): Column containing archetype labels.
        count_col (str, optional): Column containing per-deck counts.
        colors_dict (dict | None, optional): Mapping from archetype to color.
        dropna (bool, optional): Whether to ignore missing archetype values.
        save_path (str | None, optional): Path where the resulting plot dict
            should be saved as JSON. Defaults to None.

    Returns:
        dict: Plot-ready dictionary for PieChart.
    """

    df_new = df.copy()

    if dropna:
        df_new = df_new.dropna(subset=[arch_col])

    shares = (
        df_new.groupby(arch_col, dropna=dropna)[count_col]
        .sum()
        .sort_values(ascending=False)
    )

    total = shares.sum()
    shares_pct = (shares / total * 100).round(2)

    labels = shares_pct.index.tolist()
    shares_pct_list = shares_pct.tolist()
    shares_rad = [x * tau / 100 for x in shares_pct_list]

    plot_dict = {
        "plot_type": "arch_share",
        "source_col": arch_col,
        "count_col": count_col,
        "labels": labels,
        "shares_pct": shares_pct_list,
        "shares_rad": shares_rad,
        "counts": shares.tolist(),
        "total": int(total),
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
    deck_col: str = "deck_name",
    count_col: str = "count",
    top_n: int = 10,
    dropna: bool = True,
    save_path: str | None = None,
):
    """
    Build a plotting dictionary for top N deck metagame share from a deck-count
    table.


    This expects a DataFrame where each row is already a deck summary, e.g.:


        deck_name | count | share_pct | deck_name_arch


    Deck share is therefore computed by summing ``count`` within each deck
    label, not by counting rows.


    Args:
        df: Input dataframe.
        deck_col (str, optional): Column containing deck labels.
        count_col (str, optional): Column containing per-deck counts.
        top_n (int, optional): Number of top decks to keep.
        dropna (bool, optional): Whether to ignore missing deck values.
        save_path (str | None, optional): Path where the resulting plot dict
            should be saved as JSON. Defaults to None.


    Returns:
        dict: Plot-ready dictionary for top N deck share.
    """

    df_new = df.copy()

    if dropna:
        df_new = df_new.dropna(subset=[deck_col])

    # Remove rogue/other rows if they already exist in input
    df_new = df_new[
        ~df_new[deck_col].astype(str).str.strip().str.lower().isin(["rogue", "other"])
    ].copy()

    counts_series = (
        df_new.groupby(deck_col, dropna=dropna)[count_col]
        .sum()
        .sort_values(ascending=False)
    )

    total = counts_series.sum()
    top_counts = counts_series.iloc[:top_n].copy()
    top_shares = top_counts / total

    labels = top_counts.index.tolist()
    shares_pct = (top_shares * 100).round(2).tolist()
    counts = top_counts.astype(int).tolist()

    plot_dict = {
        "plot_type": "top_n_deck_share",
        "source_col": deck_col,
        "count_col": count_col,
        "labels": labels,
        "shares_pct": shares_pct,
        "counts": counts,
        "top_n": top_n,
        "n": len(labels),
        "total": int(total),
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
        "n_matches": int(len(df)/2),
    }

    if save_path is not None:
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(meta_dict, f, indent=2, ensure_ascii=False)


def save_top_n_wr_interval(
    df,
    deck_col: str = "user_deck",
    matches_col: str = "matches_played",
    wr_col: str = "wr",
    wr_low_col: str = "wr_low",
    wr_high_col: str = "wr_high",
    confidence_col: str = "confidence",
    top_n: int = 15,
    dropna: bool = True,
    save_path: str | None = None,
):
    """
    Build a plotting dictionary for top N deck win rate intervals from a deck
    summary table.


    This expects a DataFrame where each row is already a deck summary, e.g.:


        user_deck | matches_played | wr | wr_low | wr_high | confidence


    Top-N selection is therefore computed by sorting on ``matches_played`` and
    keeping the first ``top_n`` rows.


    Args:
        df: Input dataframe.
        deck_col (str, optional): Column containing deck labels.
        matches_col (str, optional): Column containing per-deck match counts.
        wr_col (str, optional): Column containing win rate in percent.
        wr_low_col (str, optional): Column containing lower interval bound in percent.
        wr_high_col (str, optional): Column containing upper interval bound in percent.
        confidence_col (str, optional): Column containing qualitative confidence.
        top_n (int, optional): Number of top decks to keep.
        dropna (bool, optional): Whether to ignore missing deck values.
        save_path (str | None, optional): Path where resulting plot dict
            should be saved as JSON. Defaults to None.


    Returns:
        dict: Plot-ready dictionary for top N deck win rate intervals.
    """

    df_new = df.copy()

    required_cols = [deck_col, matches_col, wr_col, wr_low_col, wr_high_col, confidence_col]
    missing_cols = [col for col in required_cols if col not in df_new.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    if dropna:
        df_new = df_new.dropna(subset=[deck_col])

    df_new = (
        df_new.sort_values(matches_col, ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )

    plot_dict = {
        "plot_type": "top_n_wr_interval",
        "source_col": deck_col,
        "matches_col": matches_col,
        "labels": df_new[deck_col].tolist(),
        "matches_played": df_new[matches_col].astype(int).tolist(),
        "wr": df_new[wr_col].round(1).tolist(),
        "wr_low": df_new[wr_low_col].round(1).tolist(),
        "wr_high": df_new[wr_high_col].round(1).tolist(),
        "confidence": df_new[confidence_col].astype(str).tolist(),
        "top_n": top_n,
        "n": len(df_new),
        "total_matches": int(df_new[matches_col].sum()),
    }

    if save_path is not None:
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(plot_dict, f, indent=2, ensure_ascii=False)


def save_matchup_matrix(
    wr_matrix: pd.DataFrame,
    matchup_long: pd.DataFrame,
    user_col: str = "user_deck",
    oppo_col: str = "oppo_deck",
    matches_col: str = "matches",
    wins_col: str = "wins",
    losses_col: str = "losses",
    wr_col: str = "wr",
    wr_low_col: str = "wr_low",
    wr_high_col: str = "wr_high",
    confidence_col: str = "confidence",
    save_path: str | None = None,
):
    """
    Build a plotting dictionary for a matchup matrix and optionally save it as JSON.

    Expected matchup_long columns:

        user_deck | oppo_deck | matches | wins | losses | wr | wr_high | wr_low | confidence

    Args:
        wr_matrix: Pivoted win-rate matrix.
        matchup_long: Directional matchup table.
        user_col (str, optional): Column containing row deck labels.
        oppo_col (str, optional): Column containing column deck labels.
        matches_col (str, optional): Column containing number of matches.
        wins_col (str, optional): Column containing wins.
        losses_col (str, optional): Column containing losses.
        wr_col (str, optional): Column containing win rate.
        wr_low_col (str, optional): Column containing lower Wilson bound.
        wr_high_col (str, optional): Column containing upper Wilson bound.
        confidence_col (str, optional): Column containing qualitative confidence.
        save_path (str | None, optional): Path where resulting dict should be saved as JSON.

    Returns:
        dict: Plot-ready dictionary for matchup matrix.
    """
    wr_matrix_new = wr_matrix.copy()
    matchup_new = matchup_long.copy()

    required_cols = [
        user_col,
        oppo_col,
        matches_col,
        wins_col,
        losses_col,
        wr_col,
        wr_low_col,
        wr_high_col,
        confidence_col,
    ]
    missing_cols = [col for col in required_cols if col not in matchup_new.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns in matchup_long: {missing_cols}")

    matchup_new[confidence_col] = matchup_new[confidence_col].astype(str)

    matchup_new = matchup_new.sort_values(
        [user_col, oppo_col],
        ascending=[True, True],
    ).reset_index(drop=True)

    deck_order_rows = [str(x) for x in wr_matrix_new.index.tolist()]
    deck_order_cols = [str(x) for x in wr_matrix_new.columns.tolist()]

    wr_matrix_dict = {
        str(row_name): {
            str(col_name): (
                None if pd.isna(value) else round(float(value), 1)
            )
            for col_name, value in wr_matrix_new.loc[row_name].items()
        }
        for row_name in wr_matrix_new.index
    }

    matchup_records = []
    matchup_lookup = {}

    for _, row in matchup_new.iterrows():
        user_deck = str(row[user_col])
        oppo_deck = str(row[oppo_col])

        record = {
            user_col: user_deck,
            oppo_col: oppo_deck,
            matches_col: int(row[matches_col]),
            wins_col: int(row[wins_col]),
            losses_col: int(row[losses_col]),
            wr_col: None if pd.isna(row[wr_col]) else round(float(row[wr_col]), 1),
            wr_low_col: None if pd.isna(row[wr_low_col]) else round(float(row[wr_low_col]), 1),
            wr_high_col: None if pd.isna(row[wr_high_col]) else round(float(row[wr_high_col]), 1),
            confidence_col: str(row[confidence_col]),
        }

        matchup_records.append(record)

        if user_deck not in matchup_lookup:
            matchup_lookup[user_deck] = {}

        matchup_lookup[user_deck][oppo_deck] = {
            matches_col: record[matches_col],
            wins_col: record[wins_col],
            losses_col: record[losses_col],
            wr_col: record[wr_col],
            wr_low_col: record[wr_low_col],
            wr_high_col: record[wr_high_col],
            confidence_col: record[confidence_col],
        }

    plot_dict = {
        "plot_type": "matchup_matrix",
        "user_col": user_col,
        "oppo_col": oppo_col,
        "deck_order_rows": deck_order_rows,
        "deck_order_cols": deck_order_cols,
        "n_rows": len(deck_order_rows),
        "n_cols": len(deck_order_cols),
        "wr_matrix": wr_matrix_dict,
        "matchup_long": matchup_records,
        "matchup_lookup": matchup_lookup,
    }

    if save_path is not None:
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(plot_dict, f, indent=2, ensure_ascii=False)

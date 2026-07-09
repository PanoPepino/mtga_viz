import pandas as pd
import numpy as np
from pandas import DataFrame

from statsmodels.stats.proportion import proportion_confint


def get_table_wr_error(df: DataFrame,
                       result_col: str,
                       study_col: str,
                       oppo_col: str = "oppo_deck",
                       exclude_mirrors: bool = True,
                       # Can be modified depending on the heuristic discussion on what is a good confidence and not.
                       bins: list = [0, 10, 50, float("inf")],
                       alpha=0.05,
                       top_n: int | None = None,
                       include_rogue=False,
                       rogue_label: str = "other",
                       order_df: DataFrame | None = None,
                       order_col: str | None = None) -> DataFrame:
    """
    Compute per-deck win rate with Wilson confidence intervals and a qualitative confidence label.


    For each unique entry in ``study_col``, the function:


    1. Parses ``result_col`` (expected format ``'W-L'``, e.g. ``'2-1'``) to
       determine whether the player won each match.
    2. Aggregates match counts and win counts.
    3. Computes the win rate and a Wilson confidence interval at level
       ``1 - alpha``.
    4. Assigns ``confidence`` label based on sample size.
    5. If ``top_n`` is provided, keeps only the top ``top_n`` entries by
       ``matches_played`` and aggregates the remaining entries into one row
       labelled ``rogue_label`` before recomputing the win rate and Wilson
       confidence interval for that aggregated row.


    Args:
        df (DataFrame): Enriched match DataFrame (output of
            :func:`~mtga_viz.core.database_manipulation.create_new_columns`).
        result_col (str): Column containing match results in ``'W-L'`` format
            (e.g. ``'result_vs_oppo'``).
        study_col (str): Column to group by — typically ``'user_deck'`` or
            ``'user_deck_arch'``.
        oppo_col (str, optional): Opponent deck column used to identify mirror
            matches. Defaults to ``'oppo_deck'``.
        exclude_mirrors (bool, optional): If ``True``, remove rows where
            ``study_col == oppo_col`` before computing win rates. Defaults to
            ``False``.
        bins (list, optional): list of how many matches are required to establish a given label confidence (very low, low, medium, high)
        alpha (float, optional): Significance level for the Wilson interval.
            Defaults to ``0.05`` (95 % confidence).
        top_n (int | None, optional): Number of most-played entries to keep.
            If provided, all remaining entries are aggregated into one extra
            row. Defaults to ``None``.
        rogue_label (str, optional): Label used for the aggregated remaining
            entries when ``top_n`` is provided. Defaults to ``"rogue"``.


    Returns:
        DataFrame: One row per unique ``study_col`` value, sorted descending by
        ``matches_played``, with columns:



        - ``study_col`` — deck or archetype name.
        - ``matches_played`` — total valid matches parsed.
        - ``wr`` — win rate in percent, rounded to 1 decimal.
        - ``wr_error`` — half-width of the Wilson CI in percent, rounded to 1 decimal.
        - ``confidence``


        If ``top_n`` is provided, the returned table contains the top
        ``top_n`` rows plus one aggregated ``rogue_label`` row when applicable.
    """

    if exclude_mirrors:
        df = df[df[study_col] != df[oppo_col]].copy()

    # Parse the wins and losses and group
    win_tbl = (
        df.assign(
            wins=df[result_col].astype(str).str.extract(r"^(\d+)-(\d+)$")[0].astype(float),
            losses=df[result_col].astype(str).str.extract(r"^(\d+)-(\d+)$")[1].astype(float),
        )
        .assign(won_match=lambda x: x["wins"] > x["losses"])
        .groupby(study_col, as_index=False)
        .agg(
            matches_played=("won_match", "count"),
            matches_won=("won_match", "sum")
        )
        .sort_values("matches_played", ascending=False)
        .reset_index(drop=True)
    )

    if top_n is not None and len(win_tbl) > top_n and include_rogue is True:
        top_tbl = win_tbl.iloc[:top_n].copy()
        tail_tbl = win_tbl.iloc[top_n:].copy()

        rogue_row = pd.DataFrame({
            study_col: [rogue_label],
            "matches_played": [int(tail_tbl["matches_played"].sum())],
            "matches_won": [int(tail_tbl["matches_won"].sum())],
        })

        win_tbl = pd.concat([top_tbl, rogue_row], ignore_index=True)

    # Compute the win rate
    win_tbl["wr"] = 100 * win_tbl["matches_won"] / win_tbl["matches_played"]

    # Compute the error given your confidence proportionally (we are looking at 95%)
    ci = win_tbl.apply(
        lambda r: proportion_confint(
            count=int(r["matches_won"]),
            nobs=int(r["matches_played"]),
            alpha=alpha,
            method="wilson"
        ),
        axis=1,
        result_type="expand"
    )

    # Table manipulation
    win_tbl["wr_low"] = 100 * ci[0]
    win_tbl["wr_high"] = 100 * ci[1]
    win_tbl["wr_error"] = (win_tbl["wr_high"] - win_tbl["wr_low"]) / 2

    win_tbl["confidence"] = pd.cut(
        win_tbl["matches_played"],
        bins=bins,
        labels=["low", "medium", "high"],
        include_lowest=True,
    )

    win_tbl["wr"] = win_tbl["wr"].round(1)
    win_tbl["wr_low"] = win_tbl["wr_low"].round(1)
    win_tbl["wr_high"] = win_tbl["wr_high"].round(1)
    win_tbl["wr_error"] = win_tbl["wr_error"].round(1)

    table_wr = (
        win_tbl[[study_col, 'matches_played', 'wr', 'wr_low', 'wr_high', 'confidence']]).copy()

    if order_df is not None:
        if order_col is None:
            order_col = study_col

        order_map = {v: i for i, v in enumerate(order_df[order_col].tolist())}
        table_wr["_order"] = table_wr[study_col].map(order_map).fillna(float("inf"))
        table_wr = (
            table_wr
            .sort_values(["_order", "matches_played"], ascending=[True, False])
            .drop(columns="_order")
            .reset_index(drop=True)
        )
    else:
        table_wr = (
            table_wr
            .sort_values("matches_played", ascending=False)
            .reset_index(drop=True)
        )

    return table_wr

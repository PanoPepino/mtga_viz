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
                       bins: list = [0, 10, 30, 50, float("inf")],
                       alpha=0.05) -> DataFrame:
    """
    Compute per-deck win rate with Wilson confidence intervals and a qualitative confidence label.

    For each unique entry in ``study_col``, the function:

    1. Parses ``result_col`` (expected format ``'W-L'``, e.g. ``'2-1'``) to
       determine whether the player won each match.
    2. Aggregates match counts and win counts.
    3. Computes the win rate and a Wilson confidence interval at level
       ``1 - alpha``.
    4. Assigns ``confidence`` label based on sample size.

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


    Returns:
        DataFrame: One row per unique ``study_col`` value, sorted descending by
        ``matches_played``, with columns:


        - ``study_col`` — deck or archetype name.
        - ``matches_played`` — total valid matches parsed.
        - ``wr`` — win rate in percent, rounded to 1 decimal.
        - ``wr_error`` — half-width of the Wilson CI in percent, rounded to 1 decimal.
        - ``confidence``
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
    )

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
        labels=["very low", "low", "medium", "high"]
    )

    win_tbl["wr"] = win_tbl["wr"].round(1)
    win_tbl["wr_low"] = win_tbl["wr_low"].round(1)
    win_tbl["wr_high"] = win_tbl["wr_high"].round(1)
    win_tbl["wr_error"] = win_tbl["wr_error"].round(1)

    table_wr = (
        win_tbl[[study_col, 'matches_played', 'wr', 'wr_low', 'wr_high', 'confidence']]
        .sort_values("matches_played", ascending=False)
    )

    return table_wr

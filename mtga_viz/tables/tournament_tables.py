import numpy as np
import pandas as pd
from statsmodels.stats.proportion import proportion_confint


def get_matchup_matrix(
    df,
    user_col="user_deck",
    oppo_col="oppo_deck",
    result_col="result_vs_oppo",
    top_n=10,
    min_matches=5,
    bins: list = [0, 9, 19, 29, float("inf")],
    exclude_mirrors=True,
    alpha=0.05,
):
    """
    This function will create a match matrix + other dataframe information about the performance of each deck against any other deck in the metagame. 
    Observe it can be limited to top N decks of the format and the user can define minimal amount of matches to be considered.

    Args:
        df (Dataframe): 
        user_col (str, optional): The column containing information about the user_deck. Defaults to "user_deck".
        oppo_col (str, optional): Same, but with opponent. Defaults to "oppo_deck".
        result_col (str, optional): The column that contains the result of the match to study. Defaults to "result_vs_oppo".
        top_n (int, optional): Top N decks to display in the matrix. Defaults to 10.
        bins (list, optional): list of how many matches are required to establish a given label confidence (very low, low, medium, high)
        min_matches (int, optional): Minimal amount of matches to be displayed. Defaults to 5.
        exclude_mirrors (bool, optional):

    Returns:
        wr_matrix (Dataframe): win rate layer
        matchup_long (Dataframe): directional matchup table with columns
            [user_deck, oppo_deck, matches, wins, losses, wr, wr_high, wr_low, confidence]
    """
    work = df.copy()

    if exclude_mirrors:
        work = work[work[user_col] != work[oppo_col]].copy()

    parsed = work[result_col].astype(str).str.extract(r"^(\d+)-(\d+)$")
    work["wins"] = pd.to_numeric(parsed[0], errors="coerce")
    work["losses"] = pd.to_numeric(parsed[1], errors="coerce")
    work = work.dropna(subset=["wins", "losses"]).copy()
    work["won_match"] = work["wins"] > work["losses"]

    play_counts = pd.concat([
        work[user_col].value_counts(),
        work[oppo_col].value_counts()
    ], axis=1).fillna(0)

    play_counts.columns = ["user_count", "oppo_count"]
    play_counts["total_count"] = play_counts["user_count"] + play_counts["oppo_count"]

    top_decks = play_counts.sort_values("total_count", ascending=False).head(top_n).index

    work = work[
        work[user_col].isin(top_decks) &
        work[oppo_col].isin(top_decks)
    ].copy()

    ordered = work[[user_col, oppo_col]].apply(
        lambda row: sorted([row[user_col], row[oppo_col]]),
        axis=1,
        result_type="expand"
    )
    work["deck_a"] = ordered[0]
    work["deck_b"] = ordered[1]

    work["deck_a_win"] = np.where(
        work[user_col] == work["deck_a"],
        work["won_match"].astype(int),
        1 - work["won_match"].astype(int)
    )

    matchup = (
        work.groupby(["deck_a", "deck_b"], as_index=False)
        .agg(
            matches=("deck_a_win", "count"),
            wins_a=("deck_a_win", "sum"),
        )
    )

    matchup["wins_b"] = matchup["matches"] - matchup["wins_a"]
    matchup["losses_a"] = matchup["wins_b"]
    matchup["losses_b"] = matchup["wins_a"]

    ci_a = matchup.apply(
        lambda r: proportion_confint(
            count=int(r["wins_a"]),
            nobs=int(r["matches"]),
            alpha=alpha,
            method="wilson"
        ),
        axis=1,
        result_type="expand"
    )

    ci_b = matchup.apply(
        lambda r: proportion_confint(
            count=int(r["wins_b"]),
            nobs=int(r["matches"]),
            alpha=alpha,
            method="wilson"
        ),
        axis=1,
        result_type="expand"
    )

    matchup["wr_a"] = 100 * matchup["wins_a"] / matchup["matches"]
    matchup["wr_b"] = 100 * matchup["wins_b"] / matchup["matches"]
    matchup["wr_low_a"] = 100 * ci_a[0]
    matchup["wr_high_a"] = 100 * ci_a[1]
    matchup["wr_low_b"] = 100 * ci_b[0]
    matchup["wr_high_b"] = 100 * ci_b[1]

    forward = matchup.rename(columns={
        "deck_a": user_col,
        "deck_b": oppo_col,
        "wins_a": "wins",
        "losses_a": "losses",
        "wr_a": "wr",
        "wr_low_a": "wr_low",
        "wr_high_a": "wr_high",
    })[[user_col, oppo_col, "matches", "wins", "losses", "wr", "wr_high", "wr_low"]]

    backward = matchup.rename(columns={
        "deck_b": user_col,
        "deck_a": oppo_col,
        "wins_b": "wins",
        "losses_b": "losses",
        "wr_b": "wr",
        "wr_low_b": "wr_low",
        "wr_high_b": "wr_high",
    })[[user_col, oppo_col, "matches", "wins", "losses", "wr", "wr_high", "wr_low"]]

    matchup_long = pd.concat([forward, backward], ignore_index=True)

    matchup_long["confidence"] = pd.cut(
        matchup_long["matches"],
        bins=bins,
        labels=["very low", "low", "medium", "high"],
        include_lowest=True,
    )

    matchup_long["wr"] = matchup_long["wr"].round(1)
    matchup_long["wr_low"] = matchup_long["wr_low"].round(1)
    matchup_long["wr_high"] = matchup_long["wr_high"].round(1)

    matchup_long = matchup_long[
        [user_col, oppo_col, "matches", "wins", "losses", "wr", "wr_high", "wr_low", "confidence"]
    ].sort_values([user_col, oppo_col]).reset_index(drop=True)

    wr_matrix = matchup_long.copy()
    wr_matrix["wr_plot"] = wr_matrix["wr"].where(wr_matrix["matches"] >= min_matches, np.nan)
    wr_matrix = wr_matrix.pivot(index=user_col, columns=oppo_col, values="wr_plot")

    return wr_matrix, matchup_long

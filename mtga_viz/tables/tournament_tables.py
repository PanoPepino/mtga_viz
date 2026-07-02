

import numpy as np
import pandas as pd


def get_matchup_matrix(
        df,
        user_col="user_deck",
        oppo_col="oppo_deck",
        result_col="result_vs_oppo",
        top_n=10,
        min_matches=5,
        bins: list = [0, 9, 19, 29, float("inf")],
        exclude_mirrors=True):
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
        match_matrix (Dataframe): win rate layer
        count_matrix (Dataframe): match count layer
        count_dataframe (Dataframe): List-like object containing information about win and loss
        match_counting (Dataframe): Total amount of matches for a given deck

    """

    work = df.copy()

    # Exclude the mirrors to avoid crazy stuff
    if exclude_mirrors:
        work = work[work[user_col] != work[oppo_col]].copy()

    # Extract information if it is a win or a loss for that match
    parsed = work[result_col].astype(str).str.extract(r"^(\d+)-(\d+)$")
    work["wins"] = pd.to_numeric(parsed[0], errors="coerce")
    work["losses"] = pd.to_numeric(parsed[1], errors="coerce")
    work = work.dropna(subset=["wins", "losses"]).copy()
    work["won_match"] = work["wins"] > work["losses"]

    #  Concatenate # of wins and losses for a given deck and add to the dataframe
    play_counts = pd.concat([
        work[user_col].value_counts(),
        work[oppo_col].value_counts()
    ], axis=1).fillna(0)

    play_counts.columns = ["user_count", "oppo_count"]
    play_counts["total_count"] = play_counts["user_count"] + play_counts["oppo_count"]

    # Sort by top decks
    top_decks = play_counts.sort_values("total_count", ascending=False).head(top_n).index

    work = work[
        work[user_col].isin(top_decks) &
        work[oppo_col].isin(top_decks)
    ].copy()

    # Canonical unordered pair
    ordered = work[[user_col, oppo_col]].apply(
        lambda row: sorted([row[user_col], row[oppo_col]]),
        axis=1,
        result_type="expand"
    )
    work["deck_a"] = ordered[0]
    work["deck_b"] = ordered[1]

    # Wins from deck_a perspective
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

    # Compute the WR of the upper triangular part and the lower
    matchup["wins_b"] = matchup["matches"] - matchup["wins_a"]
    matchup["wr_a"] = (100 * matchup["wins_a"] / matchup["matches"]).round(1)
    matchup["wr_b"] = 100 - matchup["wr_a"]

    # If not enough data, then mask it
    matchup["wr_a_masked"] = matchup["wr_a"].where(matchup["matches"] >= min_matches, np.nan)
    matchup["wr_b_masked"] = matchup["wr_b"].where(matchup["matches"] >= min_matches, np.nan)

    # Expand back to directional rows (UT and DT)
    forward = matchup.rename(columns={
        "deck_a": user_col,
        "deck_b": oppo_col,
        "wins_a": "wins",
        "wins_b": "losses",
        "wr_a": "wr",
        "wr_a_masked": "wr_masked",
    })[[user_col, oppo_col, "matches", "wins", "losses", "wr", "wr_masked"]]

    backward = matchup.rename(columns={
        "deck_b": user_col,
        "deck_a": oppo_col,
        "wins_b": "wins",
        "wins_a": "losses",
        "wr_b": "wr",
        "wr_b_masked": "wr_masked",
    })[[user_col, oppo_col, "matches", "wins", "losses", "wr", "wr_masked"]]

    matchup_long = pd.concat([forward, backward], ignore_index=True)
    matchup_long["wr"] = matchup_long["wr"].round(1)
    matchup_long['confidence'] = pd.cut(
        matchup_long['matches'],
        bins=bins,
        labels=["very low", "low", "medium", "high"]
    )

    wr_matrix = matchup_long.pivot(index=user_col, columns=oppo_col, values="wr_masked")
    n_matrix = matchup_long.pivot(index=user_col, columns=oppo_col, values="matches")

    return wr_matrix, n_matrix, matchup_long, play_counts.loc[top_decks]

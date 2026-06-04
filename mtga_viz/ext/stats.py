import pandas as pd
import numpy as np

from mtga_viz.ext.database_manipulation import add_match_score, rogue_filter
from statsmodels.stats.proportion import proportion_confint


def get_wr_error(df,
                 column,
                 wins_col="win",
                 losses_col="loss",
                 granularity: int = 1):
    """
    Return the winrate for a given column (deck or archetype) based on a binomial interval. (Better than 95% confidence with t-student.)

    Args:
        df : Your DataFrame with the tracking.
        column : The specific column you want to study (i.e. Archetype or Deck)
        wins_col : Defaults to "win".
        losses_col : Defaults to "loss".
        granularity (int, optional): How much you want to filter through to have reliable data. If the number of iterations of a given entry in the column is less than the granularity, those entries will be considered part of a greater group. Defaults to 1.

    Returns:
        stats: A DataFrame with columns as the input column, the wr, and the extremes of the wr.
    """
    df = rogue_filter(df.copy(), column, granularity)

    df["match_win"] = (df[wins_col] == 2).astype(int)
    df["match_loss"] = (df[losses_col] == 2).astype(int)
    df = df[(df["match_win"] + df["match_loss"]) == 1]

    stats = df.groupby(column)["match_win"].agg(n="count", wins="sum").reset_index()
    stats["wr"] = stats["wins"] / stats["n"]

    ci = stats.apply(lambda r: proportion_confint(r["wins"], r["n"], alpha=0.05, method="wilson"),
                     axis=1, result_type="expand")
    stats["wr_low"] = ci[0]
    stats["wr_high"] = ci[1]

    stats["wr"] = (stats["wr"] * 100).round(1)
    stats["wr_low"] = (stats["wr_low"] * 100).round(1)
    stats["wr_high"] = (stats["wr_high"] * 100).round(1)

    return stats[[column, "wr", "wr_low", "wr_high"]]


def get_archetype_summary(df, granularity=10):
    """
    Return a summary DataFrame with one row per archetype.
    Includes total matches, share, radians, match score breakdown, WR and WR error.
    """

    df_1 = rogue_filter(df, 'archetype', granularity=granularity, rogue_name='Rogue')
    df_2 = rogue_filter(df_1, 'deck', granularity=1, rogue_name='Rogue')
    df_3 = add_match_score(df_2)

    out = (
        df_3.groupby("archetype", as_index=False)
            .size()
            .rename(columns={"size": "count"})
    )

    out["share_pct"] = out["count"] / out["count"].sum() * 100
    out["share_rad"] = out["share_pct"] * 2 * np.pi / 100

    score_breakdown = (
        df_3.groupby(["archetype", "match_score"])
            .size()
            .unstack(fill_value=0)
            .reindex(columns=["2-0", "2-1", "1-2", "0-2"], fill_value=0)
            .reset_index()
    )

    wr_rate_arch = get_wr_error(df_3, "archetype", granularity=granularity)

    summary_output = (
        out.merge(wr_rate_arch, on="archetype", how="left").merge(score_breakdown, on="archetype", how="left")
    )

    return summary_output.round(2)


def get_deck_summary(df, archetype_name, granularity=5):
    """
    Similar to `get_archetype_summary` but for decks.
    """
    df_1 = rogue_filter(df, 'archetype', granularity=granularity)
    df_2 = rogue_filter(df_1, 'deck', granularity=granularity, rogue_name=f"Gen. {archetype_name}")
    sub = df_2[df_2["archetype"] == archetype_name]
    out = (
        sub.groupby("deck", as_index=False)
           .size()
           .rename(columns={"size": "count"})
    )
    wr_deck = get_wr_error(df_2, 'deck')
    out["share_pct_in_arch"] = (out["count"] / out["count"].sum() * 100).round(2)
    out["share_rad_in_arch"] = (out["share_pct_in_arch"] * 2 * np.pi / 100).round(2)

    summary_deck_output = (out[["deck", "share_pct_in_arch", "share_rad_in_arch", "count"]]).merge(wr_deck)
    return summary_deck_output


def get_tricks(df):
    out = (
        df["trick"]
        .fillna("")
        .astype(str)
        .str.strip()
    )
    out = out[out != ""].value_counts().reset_index()
    out.columns = ["tricks", "numbers"]
    return out

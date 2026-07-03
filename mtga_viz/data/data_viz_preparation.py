from math import tau  # to directly convert to angles


def get_pie_chart_arch(
    df,
    arch_col: str,
    colors_dict: dict,
    top_n: int | None = None,
    include_other: bool = False,
    other_label: str = "Other",
):
    """
    Build the inputs needed by PieChart from a dataframe column.

    Args:
        df: Input dataframe.
        deck_col (str): Column with archetype names.
        colors_dict (dict): Mapping from label to manim color.
        top_n (int | None, optional): Keep only the top N entries. Defaults to None.
        include_other (bool, optional): Aggregate the remaining entries into 'Other'. Defaults to False.
        other_label (str, optional): Label used for the aggregated tail. Defaults to "Other".

    Returns:
        tuple: labels, shares_rad, colors_dict
    """

    shares = df[arch_col].value_counts(normalize=True)

    if top_n is not None:
        top = shares.iloc[:top_n]

        if include_other and len(shares) > top_n:
            other_share = shares.iloc[top_n:].sum()
            top.loc[other_label] = other_share

        shares = top

    labels = shares.index.tolist()
    shares_rad = [share * tau for share in shares.tolist()]

    return labels, shares_rad, colors_dict

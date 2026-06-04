
import numpy as np
from numbers_parser import Document
import pandas as pd


def is_nonempty_cell(cell):
    """
    To not count empty entries
    """
    if cell is None:
        return False
    if isinstance(cell, str) and cell.strip() == "":
        return False
    return True


def numbers_to_df(path, sheet_index=0, table_index=0):
    """
    Transform a numbers shee to dataframe
    """
    doc = Document(path)
    table = doc.sheets[sheet_index].tables[table_index]
    rows = table.rows(values_only=True)

    non_empty_rows = [row for row in rows if any(is_nonempty_cell(cell) for cell in row)]

    header = non_empty_rows[0]
    data = non_empty_rows[1:]
    return pd.DataFrame(data, columns=header)


def excel_to_df(path, sheet_index=0):
    """
    Transform an Excel-like sheet to dataframe
    """
    df = pd.read_excel(path, sheet_name=sheet_index, header=None)
    df = df.replace(r"^\s*$", pd.NA, regex=True).dropna(how="all")

    header = df.iloc[0].tolist()
    data = df.iloc[1:].reset_index(drop=True)
    data.columns = header
    return data


def add_match_score(
    df,
    wins_col="win",
    losses_col="loss",
    drop_invalid=True
):
    out = df.copy()

    valid_scores = {(2, 0), (2, 1), (1, 2), (0, 2)}

    out["match_score"] = list(zip(out[wins_col], out[losses_col]))
    out["match_score"] = out["match_score"].where(
        out["match_score"].isin(valid_scores),
        other=np.nan
    )
    out["match_score"] = out["match_score"].map(
        lambda x: f"{int(x[0])}-{int(x[1])}" if pd.notna(x) else np.nan
    )
    if drop_invalid:
        out = out[out["match_score"].notna()].copy()

    return out


def rogue_filter(df,
                 column,
                 granularity=1,
                 rogue_name="Rogue"):
    """
    Replace rare categories in a column with `rogue_name`.

    Args:
        df: pandas DataFrame
        column: column to rewrite
        threshold: entries with count <= threshold become rogue
        rogue_name: label for grouped rare entries

    Returns:
        pandas DataFrame
    """
    df = df.copy()

    counts = df[column].value_counts()
    rare_entries = counts[counts <= granularity].index

    df[column] = df[column].where(~df[column].isin(rare_entries), rogue_name)

    return df

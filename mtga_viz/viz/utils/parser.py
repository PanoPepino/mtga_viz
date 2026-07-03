

def simple_parser(s: str) -> str:
    """Parser to translate spaces to _"""
    return s.lower().replace(" ", "_")


def underscore_parser(s: str) -> str:
    """Parser to translate spaces from regular string to LaTeX manipulation"""
    return s.replace("_", "$\\_$")


def capitalise_no_score(s: str) -> str:
    """Parser to translate spaces from regular string to LaTeX manipulation"""
    parts = s.split("_")

    mana_letters = set("wubrgx")

    if not parts:
        return s

    if parts[0] == "mono" and len(parts) >= 2 and parts[1] in mana_letters:
        prefix = f"mono {parts[1]}"
        rest = " ".join(parts[2:])
        return f"{prefix} {rest.capitalize()}".strip()

    if all(letter in mana_letters for letter in parts[0]):
        prefix = parts[0]
        rest = " ".join(parts[1:])
        return f"{prefix} {rest.capitalize()}".strip()

    return s.replace("_", " ").capitalize()


def extract_color_letters(asset_name: str) -> list[str]:
    """
    Extract MTG color letters from an asset name prefix.

    Examples:
        ubx_tempo -> ["u", "b", "x"]
        wbr_energy -> ["w", "b", "r"]
        mono_r_stompy -> ["r"]
    """
    prefix = asset_name.split("_", 2)

    if prefix[0] == "mono" and len(prefix) > 1:
        return [prefix[1]]

    if prefix[0] == "colorless":
        return ["x"]

    if prefix[0] == "other":
        return ["x"]

    first_chunk = prefix[0]
    return list(first_chunk)

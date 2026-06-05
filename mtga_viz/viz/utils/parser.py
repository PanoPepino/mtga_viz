

def simple_parser(s: str) -> str:
    """Parser to translate spaces to _"""
    return s.lower().replace(" ", "_")


def underscore_parser(s: str) -> str:
    """Parser to translate spaces from regular string to LaTeX manipulation"""
    return s.replace("_", "$\\_$")



def simple_parser(s: str) -> str:
    return s.lower().replace(" ", "_")


def underscore_parser(s: str) -> str:
    return s.replace("_", "$\\_$")

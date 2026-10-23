"""Conservative text identities shared by review and grouping."""
import re


def normalized_text(value: str) -> str:
    return re.sub(r'\s+', ' ', value.strip())

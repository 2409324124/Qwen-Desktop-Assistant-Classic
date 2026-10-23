"""Locate the research checkout without assuming an installed package lives in it."""
import os
from pathlib import Path


def repository_root(root=None):
    explicit = root or os.environ.get('LATEX_SFT_ROOT')
    if explicit:
        candidate = Path(explicit).expanduser().resolve()
        if (candidate/'training/data').is_dir():
            return candidate
        raise ValueError(f'Not a research checkout: {candidate}')
    for start in (Path.cwd().resolve(), Path(__file__).resolve().parent):
        for candidate in (start, *start.parents):
            if (candidate/'training/data').is_dir():
                return candidate
    raise ValueError('A research checkout is required; use --root or LATEX_SFT_ROOT. Scoring saved predictions does not require a checkout.')

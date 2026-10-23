"""Versioned formula transcription instruction shared with the npm CLI."""
from importlib.resources import files

PROMPT_VERSION = "latex-correction-v1"
SYSTEM_PROMPT = files("latex_sft.core").joinpath("resources/latex-correction.txt").read_text(encoding="utf-8")

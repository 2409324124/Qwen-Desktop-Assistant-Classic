"""Compatibility entrypoint; implementation lives in latex_sft.evaluation.evaluate_latex."""
import sys
from latex_sft.evaluation import evaluate_latex as _implementation

if __name__ == "__main__":
    _implementation.main()
else:
    sys.modules[__name__] = _implementation

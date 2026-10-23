"""Compatibility entrypoint; implementation lives in latex_sft.evaluation.prepare_latexc_benchmark."""
import sys
from latex_sft.evaluation import prepare_latexc_benchmark as _implementation

if __name__ == "__main__":
    _implementation.main()
else:
    sys.modules[__name__] = _implementation

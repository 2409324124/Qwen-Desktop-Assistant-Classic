"""Compatibility entrypoint; implementation lives in latex_sft.evaluation.reevaluate_offline."""
import sys
from latex_sft.evaluation import reevaluate_offline as _implementation

if __name__ == "__main__":
    _implementation.main()
else:
    sys.modules[__name__] = _implementation

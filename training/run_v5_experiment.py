"""Compatibility entrypoint; implementation lives in latex_sft.experiments.run_v5_experiment."""
import sys
from latex_sft.experiments import run_v5_experiment as _implementation

if __name__ == "__main__":
    _implementation.main()
else:
    sys.modules[__name__] = _implementation

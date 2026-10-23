"""Compatibility entrypoint; implementation lives in latex_sft.experiments.run_lora_inference."""
import sys
from latex_sft.experiments import run_lora_inference as _implementation

if __name__ == "__main__":
    _implementation.main()
else:
    sys.modules[__name__] = _implementation

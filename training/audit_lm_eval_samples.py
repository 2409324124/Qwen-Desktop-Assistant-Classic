"""Compatibility entrypoint; implementation lives in latex_sft.evaluation.audit_lm_eval_samples."""
import sys
from latex_sft.evaluation import audit_lm_eval_samples as _implementation

if __name__ == "__main__":
    _implementation.main()
else:
    sys.modules[__name__] = _implementation

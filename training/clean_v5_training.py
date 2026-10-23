"""Compatibility entry point; implementation lives in latex_sft.data.clean_v5_training."""
if __name__ == "__main__":
    import runpy
    runpy.run_module("latex_sft.data.clean_v5_training", run_name="__main__")
else:
    import importlib
    import sys
    sys.modules[__name__] = importlib.import_module("latex_sft.data.clean_v5_training")

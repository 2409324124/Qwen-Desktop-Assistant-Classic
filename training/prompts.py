"""Compatibility entry point; implementation lives in latex_sft.core.prompts."""
if __name__ == "__main__":
    import runpy
    runpy.run_module("latex_sft.core.prompts", run_name="__main__")
else:
    import importlib
    import sys
    sys.modules[__name__] = importlib.import_module("latex_sft.core.prompts")

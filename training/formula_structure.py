"""Compatibility entry point; implementation lives in latex_sft.data.formula_structure."""
if __name__ == "__main__":
    import runpy
    runpy.run_module("latex_sft.data.formula_structure", run_name="__main__")
else:
    import importlib
    import sys
    sys.modules[__name__] = importlib.import_module("latex_sft.data.formula_structure")

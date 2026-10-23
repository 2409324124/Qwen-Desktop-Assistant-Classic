"""Compatibility entry point for latex_sft.data.generation.noisy_builder."""
if __name__ == "__main__":
    import runpy
    runpy.run_module("latex_sft.data.generation.noisy_builder", run_name="__main__")
else:
    import importlib
    import sys
    sys.modules[__name__] = importlib.import_module("latex_sft.data.generation.noisy_builder")

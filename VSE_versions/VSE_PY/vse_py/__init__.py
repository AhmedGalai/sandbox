"""VSE_PY - Visual Scripting Environment for Python"""

__version__ = "0.1.0"
__author__ = "VSE Team"
__license__ = "MIT"

# Core exports - only import modules that are implemented
try:
    from .core.parameter import Parameter, IntParameter, FloatParameter, StringParameter, BoolParameter
except ImportError:
    pass

__all__ = [
    "Parameter",
    "IntParameter",
    "FloatParameter",
    "StringParameter",
    "BoolParameter",
]

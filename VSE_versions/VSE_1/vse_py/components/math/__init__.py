"""Math components for arithmetic and comparison operations.

This package provides mathematical processor components for VSE_PY:
- AddComponent: Adds two float values (A + B)
- SubtractComponent: Subtracts two float values (A - B)
- MultiplyComponent: Multiplies two float values (A * B)
- CompareComponent: Compares two float values using configurable operations

All components extend ProcessorComponent and are registered with the
component registry system.

Example:
    >>> from vse_py.components.math import AddComponent, MultiplyComponent
    >>> add = AddComponent()
    >>> multiply = MultiplyComponent()
"""

from .add import AddComponent
from .subtract import SubtractComponent
from .multiply import MultiplyComponent
from .compare import CompareComponent

__all__ = [
    "AddComponent",
    "SubtractComponent",
    "MultiplyComponent",
    "CompareComponent"
]

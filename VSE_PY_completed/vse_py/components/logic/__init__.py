"""Logic components

This module provides logical gate components for boolean operations in VSE_PY.

Components:
    - AndGateComponent: Logical AND operation with two inputs
    - OrGateComponent: Logical OR operation with two inputs
    - NotGateComponent: Logical NOT operation with one input
    - XorGateComponent: Logical XOR operation with two inputs

All components extend ProcessorComponent and are registered with the global
component registry for discovery and instantiation.

Examples:
    >>> from vse_py.components.logic import AndGateComponent, OrGateComponent
    >>> and_gate = AndGateComponent()
    >>> or_gate = OrGateComponent()
"""

from .and_gate import AndGateComponent
from .or_gate import OrGateComponent
from .not_gate import NotGateComponent
from .xor_gate import XorGateComponent

__all__ = [
    "AndGateComponent",
    "OrGateComponent",
    "NotGateComponent",
    "XorGateComponent",
]

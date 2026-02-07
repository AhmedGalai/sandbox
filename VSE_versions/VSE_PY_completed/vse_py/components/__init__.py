"""Component implementations for VSE_PY

This module provides base classes and concrete implementations of all component types
for VSE_PY. It includes publishers, subscribers, processors, and specialized logic
and math components.

Components are automatically registered when imported through the @register_component
decorator, making them available in the component registry for discovery and instantiation.

Subpackages:
    - logic: Boolean logic gate components (AND, OR, NOT, XOR)
    - math: Mathematical operation components
    - processor: Base ProcessorComponent class for data processing
    - publisher: Base PublisherComponent class for data sources
    - subscriber: Base SubscriberComponent class for data sinks
"""

# Import all logic components to register them
from . import logic as _logic_components
from . import math as _math_components

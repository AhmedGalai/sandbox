"""Component registry and factory system.

This package provides the component registry system for VSE_PY, enabling
dynamic component discovery, registration, and instantiation.

Main Components:
- ComponentMetadata: Dataclass for storing component metadata
- ComponentRegistry: Singleton registry for component management
- register_component: Decorator for easy component registration

Example:
    >>> from vse_py.registry import ComponentRegistry, register_component
    >>> from vse_py.core.component_base import ComponentBase
    >>>
    >>> @register_component(
    ...     type_name="custom.my_component",
    ...     display_name="My Component",
    ...     category="Custom",
    ...     description="My custom component"
    ... )
    ... class MyComponent(ComponentBase):
    ...     pass
    >>>
    >>> registry = ComponentRegistry.instance()
    >>> component = registry.create_component("custom.my_component")
"""

from .component_registry import (
    ComponentMetadata,
    ComponentRegistry,
    register_component,
)

__all__ = [
    "ComponentMetadata",
    "ComponentRegistry",
    "register_component",
]

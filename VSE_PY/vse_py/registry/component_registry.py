"""Component registry and factory system.

This module provides a thread-safe registry for managing component metadata
and factory functions. It enables runtime registration, discovery, and
instantiation of VSE_PY components.

Key Features:
- ComponentMetadata dataclass for storing component information
- ComponentRegistry singleton for managing all registered components
- register_component decorator for easy component registration
- Thread-safe access using double-checked locking pattern
- Factory pattern for dynamic component instantiation
"""

from dataclasses import dataclass, field
from typing import Dict, List, Callable, Optional, Type, Any
import threading

from ..core.component_base import ComponentBase


@dataclass
class ComponentMetadata:
    """Metadata for a registered component.

    This dataclass stores information about a component including its type name,
    display information, categorization, and optional tags for discovery.

    Attributes:
        type_name: Unique identifier for the component type (e.g., "math.add")
        display_name: Human-readable display name (e.g., "Addition")
        category: Component category for organization (e.g., "Math", "Logic")
        description: Brief description of the component's purpose and functionality
        icon_path: Optional path to an icon file for UI representation (default "")
        tags: List of tags for component discovery and filtering (default [])
        version: Component version number for tracking compatibility (default 1)

    Examples:
        >>> metadata = ComponentMetadata(
        ...     type_name="math.add",
        ...     display_name="Addition",
        ...     category="Math",
        ...     description="Adds two numbers together",
        ...     tags=["arithmetic", "basic"],
        ...     icon_path="/icons/add.png"
        ... )
    """
    type_name: str
    display_name: str
    category: str
    description: str
    icon_path: str = ""
    tags: List[str] = field(default_factory=list)
    version: int = 1


class ComponentRegistry:
    """Thread-safe singleton registry for VSE_PY components.

    The ComponentRegistry manages component registration, metadata storage,
    and factory-based instantiation. It uses double-checked locking to ensure
    thread-safe singleton behavior.

    The registry maintains:
    - Component metadata indexed by type_name
    - Factory functions for creating component instances
    - Category mappings for efficient discovery

    Examples:
        >>> registry = ComponentRegistry.instance()
        >>> registry.register_component(metadata, AddComponent)
        >>> add_comp = registry.create_component("math.add", {})
    """

    _instance: Optional['ComponentRegistry'] = None
    _lock: threading.Lock = threading.Lock()

    def __new__(cls) -> 'ComponentRegistry':
        """Prevent direct instantiation. Use instance() class method instead.

        This is an implementation detail supporting the singleton pattern.
        """
        raise TypeError("Use ComponentRegistry.instance() to get the singleton instance")

    def __init__(self) -> None:
        """Initialize the registry with empty component storage.

        This method is called internally by instance() only once.
        """
        self._components: Dict[str, tuple[ComponentMetadata, Callable[..., ComponentBase]]] = {}
        self._lock_internal: threading.Lock = threading.Lock()

    @classmethod
    def instance(cls) -> 'ComponentRegistry':
        """Get or create the singleton ComponentRegistry instance.

        Uses double-checked locking pattern to ensure thread-safe lazy
        initialization while minimizing lock contention.

        Returns:
            ComponentRegistry: The singleton instance

        Examples:
            >>> registry = ComponentRegistry.instance()
            >>> registry.register_component(metadata, component_class)
        """
        # First check (without lock) for performance
        if cls._instance is None:
            # Acquire lock for initialization
            with cls._lock:
                # Double-check after acquiring lock
                if cls._instance is None:
                    # Create instance by temporarily allowing __new__
                    instance = object.__new__(cls)
                    instance.__init__()
                    cls._instance = instance

        return cls._instance

    def register_component(
        self,
        metadata: ComponentMetadata,
        factory: Callable[..., ComponentBase]
    ) -> None:
        """Register a component with its metadata and factory function.

        The factory function should be a callable that returns a ComponentBase
        instance when called with optional parameters.

        Thread-safe registration using internal lock.

        Args:
            metadata: ComponentMetadata describing the component
            factory: Callable that returns a ComponentBase instance

        Raises:
            ValueError: If type_name is empty or already registered
            TypeError: If factory is not callable
            TypeError: If metadata is not a ComponentMetadata instance

        Examples:
            >>> metadata = ComponentMetadata(
            ...     type_name="math.add",
            ...     display_name="Addition",
            ...     category="Math",
            ...     description="Adds two numbers"
            ... )
            >>> registry.register_component(metadata, AddComponent)
        """
        if not isinstance(metadata, ComponentMetadata):
            raise TypeError("metadata must be a ComponentMetadata instance")

        if not metadata.type_name:
            raise ValueError("type_name cannot be empty")

        if not callable(factory):
            raise TypeError("factory must be callable")

        with self._lock_internal:
            if metadata.type_name in self._components:
                raise ValueError(f"Component '{metadata.type_name}' is already registered")

            self._components[metadata.type_name] = (metadata, factory)

    def create_component(
        self,
        type_name: str,
        params: Optional[Dict[str, Any]] = None
    ) -> ComponentBase:
        """Create a component instance from registered type.

        Looks up the component factory by type_name and calls it with
        optional parameters to create a new instance.

        Args:
            type_name: The type_name of the component to create
            params: Optional dictionary of parameters to pass to factory (default None)

        Returns:
            ComponentBase: A new instance of the requested component

        Raises:
            ValueError: If type_name is not registered
            TypeError: If the factory cannot be called or returns non-ComponentBase

        Examples:
            >>> component = registry.create_component("math.add")
            >>> component = registry.create_component("math.add", {"initial_value": 5})
        """
        with self._lock_internal:
            if type_name not in self._components:
                raise ValueError(f"Unknown component type: '{type_name}'")

            metadata, factory = self._components[type_name]

        # Create outside of lock to reduce contention
        try:
            if params is None:
                component = factory()
            else:
                component = factory(**params)

            if not isinstance(component, ComponentBase):
                raise TypeError(
                    f"Factory for '{type_name}' must return ComponentBase instance, "
                    f"got {type(component)}"
                )

            return component

        except TypeError as e:
            raise TypeError(f"Failed to create component '{type_name}': {str(e)}")

    def get_metadata(self, type_name: str) -> Optional[ComponentMetadata]:
        """Get metadata for a registered component type.

        Args:
            type_name: The type_name of the component

        Returns:
            ComponentMetadata: The component's metadata, or None if not found

        Examples:
            >>> metadata = registry.get_metadata("math.add")
            >>> print(metadata.display_name)
            Addition
        """
        with self._lock_internal:
            if type_name in self._components:
                return self._components[type_name][0]
            return None

    def get_components_by_category(self, category: str) -> List[ComponentMetadata]:
        """Get all components in a specific category.

        Args:
            category: The category name to filter by

        Returns:
            List[ComponentMetadata]: List of metadata for components in the category,
                                    sorted by display_name

        Examples:
            >>> math_components = registry.get_components_by_category("Math")
            >>> for metadata in math_components:
            ...     print(metadata.display_name)
        """
        with self._lock_internal:
            result = [
                metadata
                for metadata, _ in self._components.values()
                if metadata.category == category
            ]

        # Sort by display_name outside of lock
        return sorted(result, key=lambda m: m.display_name)

    def get_all_categories(self) -> List[str]:
        """Get all unique component categories.

        Returns:
            List[str]: Sorted list of unique category names

        Examples:
            >>> categories = registry.get_all_categories()
            >>> print(categories)
            ['Logic', 'Math', 'Publisher', 'Subscriber']
        """
        with self._lock_internal:
            categories = {
                metadata.category
                for metadata, _ in self._components.values()
            }

        return sorted(list(categories))

    def get_all_components(self) -> List[ComponentMetadata]:
        """Get metadata for all registered components.

        Returns:
            List[ComponentMetadata]: List of all component metadata,
                                    sorted by display_name

        Examples:
            >>> all_components = registry.get_all_components()
            >>> for metadata in all_components:
            ...     print(f"{metadata.display_name} ({metadata.category})")
        """
        with self._lock_internal:
            result = [
                metadata
                for metadata, _ in self._components.values()
            ]

        # Sort by display_name outside of lock
        return sorted(result, key=lambda m: m.display_name)

    def has_component(self, type_name: str) -> bool:
        """Check if a component type is registered.

        Args:
            type_name: The type_name to check

        Returns:
            bool: True if the component is registered, False otherwise

        Examples:
            >>> if registry.has_component("math.add"):
            ...     print("Addition component is available")
        """
        with self._lock_internal:
            return type_name in self._components

    def clear(self) -> None:
        """Clear all registered components.

        WARNING: This is intended for testing purposes only. In production,
        the registry should be populated once during initialization.

        After calling clear(), the registry will be empty and needs to be
        repopulated with component registrations.

        Examples:
            >>> registry.clear()
            >>> registry.get_all_components()
            []
        """
        with self._lock_internal:
            self._components.clear()


def register_component(
    type_name: str,
    display_name: str,
    category: str,
    description: str,
    tags: Optional[List[str]] = None,
    icon_path: str = "",
    version: int = 1
) -> Callable[[Type[ComponentBase]], Type[ComponentBase]]:
    """Decorator for registering a component class.

    This decorator automatically registers a component class with the global
    registry, using the provided metadata. The decorated class is returned
    unchanged, allowing normal class usage while side-effectfully registering it.

    The decorator can be stacked with other decorators and works with both
    direct classes and factory functions that return ComponentBase instances.

    Args:
        type_name: Unique identifier for the component (e.g., "math.add")
        display_name: Human-readable display name (e.g., "Addition")
        category: Category for organization (e.g., "Math", "Logic")
        description: Description of the component's purpose
        tags: Optional list of tags for discovery (default None)
        icon_path: Optional path to an icon file (default "")
        version: Component version number (default 1)

    Returns:
        Decorator function that registers the class and returns it unchanged

    Raises:
        ValueError: If type_name is empty
        ValueError: If component type is already registered

    Examples:
        >>> @register_component(
        ...     type_name="math.add",
        ...     display_name="Addition",
        ...     category="Math",
        ...     description="Adds two numbers together",
        ...     tags=["arithmetic", "basic"]
        ... )
        ... class AddComponent(ComponentBase):
        ...     def get_name(self) -> str:
        ...         return "Add"
        ...     def get_category(self) -> str:
        ...         return "Math"
        ...     def get_color(self) -> tuple:
        ...         return (76, 175, 80)
        ...     def execute(self) -> None:
        ...         pass

    Notes:
        - The decorated class must be a subclass of ComponentBase
        - The decorator registers the class immediately when the module is imported
        - Multiple components can be registered with the same category
        - Type names should follow the convention "category.component_name"
    """
    if not type_name:
        raise ValueError("type_name cannot be empty")

    def decorator(cls: Type[ComponentBase]) -> Type[ComponentBase]:
        """Inner decorator function that performs the registration."""
        # Create metadata for the component
        metadata = ComponentMetadata(
            type_name=type_name,
            display_name=display_name,
            category=category,
            description=description,
            icon_path=icon_path,
            tags=tags if tags is not None else [],
            version=version
        )

        # Get the singleton registry instance
        registry = ComponentRegistry.instance()

        # Register the component class as a factory
        registry.register_component(metadata, cls)

        # Return the class unchanged for normal usage
        return cls

    return decorator

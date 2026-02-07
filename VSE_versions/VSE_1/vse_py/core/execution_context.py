"""ExecutionContext for component execution

This module provides the ExecutionContext class, which serves as a container
for the component graph and connections during execution. It maintains lists
of components and connections, and provides methods for querying and managing
them.

The ExecutionContext is primarily used by the ExecutionEngine to organize
and traverse the component network during execution.
"""

from typing import List, Optional
import threading


class ExecutionContext:
    """Container for component graph and connections during execution.

    The ExecutionContext maintains the current set of components and their
    connections. It provides methods to add/remove components and connections,
    as well as query methods to find components by ID.

    This class is thread-safe for read operations. Write operations should
    be performed when the execution engine is not running.

    Attributes:
        _components: Internal list of components in this context
        _connections: Internal list of connections between pins
        _lock: Threading lock for thread-safe access
    """

    def __init__(self) -> None:
        """Initialize an empty ExecutionContext.

        Creates a new context with empty component and connection lists.
        """
        self._components: List = []
        self._connections: List = []
        self._lock = threading.Lock()

    def add_component(self, component: 'ComponentBase') -> None:
        """Add a component to the execution context.

        Args:
            component: The ComponentBase instance to add

        Raises:
            TypeError: If component is not a ComponentBase instance
            ValueError: If component is already in the context

        Examples:
            >>> context = ExecutionContext()
            >>> from vse_py.components.math.add import AddComponent
            >>> add_comp = AddComponent()
            >>> context.add_component(add_comp)
            >>> len(context.components)
            1
        """
        if not hasattr(component, 'id'):
            raise TypeError("component must be a ComponentBase instance")

        with self._lock:
            # Check if component already exists
            for comp in self._components:
                if comp.id == component.id:
                    raise ValueError(f"Component with ID {component.id} already exists")

            self._components.append(component)

    def remove_component(self, component: 'ComponentBase') -> bool:
        """Remove a component from the execution context.

        Args:
            component: The ComponentBase instance to remove

        Returns:
            bool: True if component was removed, False if not found

        Examples:
            >>> context = ExecutionContext()
            >>> from vse_py.components.math.add import AddComponent
            >>> add_comp = AddComponent()
            >>> context.add_component(add_comp)
            >>> context.remove_component(add_comp)
            True
            >>> context.remove_component(add_comp)
            False
        """
        with self._lock:
            for i, comp in enumerate(self._components):
                if comp.id == component.id:
                    self._components.pop(i)
                    return True
            return False

    def get_component_by_id(self, component_id: str) -> Optional['ComponentBase']:
        """Get a component by its unique ID.

        Args:
            component_id: The unique ID of the component to retrieve

        Returns:
            The ComponentBase instance if found, None otherwise

        Examples:
            >>> context = ExecutionContext()
            >>> from vse_py.components.math.add import AddComponent
            >>> add_comp = AddComponent()
            >>> context.add_component(add_comp)
            >>> retrieved = context.get_component_by_id(add_comp.id)
            >>> retrieved is add_comp
            True
        """
        with self._lock:
            for comp in self._components:
                if comp.id == component_id:
                    return comp
            return None

    def add_connection(self, connection: 'Connection') -> None:
        """Add a connection between two pins to the context.

        Args:
            connection: The Connection instance to add

        Raises:
            TypeError: If connection is not a Connection instance

        Examples:
            >>> context = ExecutionContext()
            >>> # Connection setup would happen here
            >>> # context.add_connection(connection)
        """
        if not hasattr(connection, 'source') or not hasattr(connection, 'destination'):
            raise TypeError("connection must be a Connection instance")

        with self._lock:
            self._connections.append(connection)

    def remove_connection(self, connection: 'Connection') -> bool:
        """Remove a connection from the context.

        Args:
            connection: The Connection instance to remove

        Returns:
            bool: True if connection was removed, False if not found

        Examples:
            >>> context = ExecutionContext()
            >>> # Connection cleanup
            >>> # context.remove_connection(connection)
        """
        with self._lock:
            for i, conn in enumerate(self._connections):
                if (conn.source.id == connection.source.id and
                    conn.destination.id == connection.destination.id):
                    self._connections.pop(i)
                    return True
            return False

    @property
    def components(self) -> List['ComponentBase']:
        """Get a copy of all components in the context.

        Returns a copy to prevent external modification of the internal
        components list.

        Returns:
            List of ComponentBase instances in this context

        Examples:
            >>> context = ExecutionContext()
            >>> comp1 = AddComponent()
            >>> comp2 = MultiplyComponent()
            >>> context.add_component(comp1)
            >>> context.add_component(comp2)
            >>> len(context.components)
            2
        """
        with self._lock:
            return self._components.copy()

    @property
    def connections(self) -> List['Connection']:
        """Get a copy of all connections in the context.

        Returns a copy to prevent external modification of the internal
        connections list.

        Returns:
            List of Connection instances in this context

        Examples:
            >>> context = ExecutionContext()
            >>> # Setup connections
            >>> conns = context.connections
            >>> # conns is a copy, modifications won't affect context
        """
        with self._lock:
            return self._connections.copy()

    def clear(self) -> None:
        """Clear all components and connections from the context.

        This method removes all components and connections, returning the
        context to an empty state. This is useful for resetting a project
        or preparing for a new set of components.

        Examples:
            >>> context = ExecutionContext()
            >>> comp = AddComponent()
            >>> context.add_component(comp)
            >>> context.clear()
            >>> len(context.components)
            0
            >>> len(context.connections)
            0
        """
        with self._lock:
            self._components.clear()
            self._connections.clear()

    def __repr__(self) -> str:
        """Return string representation of this ExecutionContext.

        Returns:
            str: Representation showing component and connection counts
        """
        with self._lock:
            return (f"ExecutionContext("
                    f"components={len(self._components)}, "
                    f"connections={len(self._connections)})")

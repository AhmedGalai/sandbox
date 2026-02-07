"""Connection and ConnectionManager classes

This module provides the connection system for VSE_PY, which manages the
data flow pathways between component pins. It includes:
- PinReference: Data class identifying pins by component and pin IDs
- Connection: Represents a single connection with type checking and serialization
- ConnectionManager: Manages all connections in the system
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
import uuid
import json


@dataclass
class PinReference:
    """Reference to a pin using component ID and pin ID.

    This data class identifies a specific pin within the system by the
    ID of its parent component and the pin's own unique ID.

    Attributes:
        component_id: UUID string identifying the component that owns the pin
        pin_id: UUID string identifying the pin within that component

    Examples:
        >>> ref = PinReference("comp-123", "pin-456")
        >>> ref.component_id
        'comp-123'
        >>> ref.pin_id
        'pin-456'
    """
    component_id: str
    pin_id: str


class Connection:
    """Represents a single connection between two pins with a topic.

    A Connection links an output pin from a source component to an input pin
    of a destination component via a named topic. Connections include type
    checking, validation, and serialization capabilities.

    Attributes:
        id: Unique UUID-based identifier for this connection
        source: PinReference to the source (output) pin
        destination: PinReference to the destination (input) pin
        topic_name: String name of the topic for this connection

    Examples:
        >>> source = PinReference("comp-A", "out-pin-1")
        >>> dest = PinReference("comp-B", "in-pin-1")
        >>> conn = Connection(source, dest, "temperature_data")
        >>> conn.validate()
        True
    """

    def __init__(
        self,
        source: PinReference,
        destination: PinReference,
        topic_name: str
    ) -> None:
        """Initialize a Connection.

        Args:
            source: PinReference to the source (output) pin
            destination: PinReference to the destination (input) pin
            topic_name: String name identifying the topic for data flow

        Raises:
            TypeError: If source or destination is not a PinReference
            ValueError: If topic_name is empty

        Examples:
            >>> source = PinReference("comp-1", "pin-1")
            >>> dest = PinReference("comp-2", "pin-2")
            >>> conn = Connection(source, dest, "data_topic")
        """
        if not isinstance(source, PinReference):
            raise TypeError("source must be a PinReference instance")
        if not isinstance(destination, PinReference):
            raise TypeError("destination must be a PinReference instance")
        if not isinstance(topic_name, str) or not topic_name.strip():
            raise ValueError("topic_name must be a non-empty string")

        self._id: str = str(uuid.uuid4())
        self._source: PinReference = source
        self._destination: PinReference = destination
        self._topic_name: str = topic_name

    @property
    def id(self) -> str:
        """Get the unique ID of this connection.

        Returns:
            str: UUID string uniquely identifying this connection
        """
        return self._id

    @property
    def source(self) -> PinReference:
        """Get the source pin reference.

        Returns:
            PinReference: Reference to the source (output) pin
        """
        return self._source

    @property
    def destination(self) -> PinReference:
        """Get the destination pin reference.

        Returns:
            PinReference: Reference to the destination (input) pin
        """
        return self._destination

    @property
    def topic_name(self) -> str:
        """Get the topic name for this connection.

        Returns:
            str: Name of the topic associated with this connection
        """
        return self._topic_name

    def validate(self) -> bool:
        """Validate the connection structure.

        Checks that:
        - source is a valid PinReference with non-empty IDs
        - destination is a valid PinReference with non-empty IDs
        - topic_name is a non-empty string
        - source and destination are different pins

        Returns:
            bool: True if all validation checks pass, False otherwise

        Examples:
            >>> source = PinReference("comp-1", "pin-1")
            >>> dest = PinReference("comp-2", "pin-2")
            >>> conn = Connection(source, dest, "topic")
            >>> conn.validate()
            True

            >>> # Invalid: empty topic name would fail earlier in __init__
            >>> # Invalid: source and destination same component but different pins is OK
        """
        try:
            # Check source
            if not isinstance(self._source, PinReference):
                return False
            if not self._source.component_id or not self._source.pin_id:
                return False

            # Check destination
            if not isinstance(self._destination, PinReference):
                return False
            if not self._destination.component_id or not self._destination.pin_id:
                return False

            # Check topic_name
            if not isinstance(self._topic_name, str) or not self._topic_name.strip():
                return False

            # Check that source and destination are different
            if (self._source.component_id == self._destination.component_id and
                self._source.pin_id == self._destination.pin_id):
                return False

            return True
        except Exception:
            return False

    def to_json(self) -> str:
        """Serialize the Connection to a JSON string.

        The JSON structure contains all connection information:
        {
            "id": "<connection_uuid>",
            "source": {
                "component_id": "<component_uuid>",
                "pin_id": "<pin_uuid>"
            },
            "destination": {
                "component_id": "<component_uuid>",
                "pin_id": "<pin_uuid>"
            },
            "topic_name": "<topic_name>"
        }

        Returns:
            str: JSON string representation of this connection

        Raises:
            TypeError: If any field contains non-JSON-serializable data

        Examples:
            >>> source = PinReference("comp-1", "pin-1")
            >>> dest = PinReference("comp-2", "pin-2")
            >>> conn = Connection(source, dest, "data_flow")
            >>> json_str = conn.to_json()
            >>> '"source"' in json_str
            True
        """
        try:
            data = {
                "id": self._id,
                "source": {
                    "component_id": self._source.component_id,
                    "pin_id": self._source.pin_id
                },
                "destination": {
                    "component_id": self._destination.component_id,
                    "pin_id": self._destination.pin_id
                },
                "topic_name": self._topic_name
            }
            return json.dumps(data)
        except TypeError as e:
            raise TypeError(f"Cannot serialize Connection to JSON: {e}")

    @classmethod
    def from_json(cls, json_str: str) -> "Connection":
        """Deserialize a Connection from a JSON string.

        The JSON string must contain all required fields: id, source,
        destination, and topic_name. The ID is preserved but a new
        instance is created with the deserialized data.

        Args:
            json_str: A JSON string produced by to_json()

        Returns:
            Connection: A new Connection instance with deserialized data

        Raises:
            json.JSONDecodeError: If the JSON string is invalid
            KeyError: If required fields are missing from the JSON
            TypeError: If field types are incorrect
            ValueError: If field values are invalid

        Examples:
            >>> source = PinReference("comp-1", "pin-1")
            >>> dest = PinReference("comp-2", "pin-2")
            >>> conn = Connection(source, dest, "test_topic")
            >>> json_str = conn.to_json()
            >>> restored = Connection.from_json(json_str)
            >>> restored.topic_name
            'test_topic'
        """
        try:
            data = json.loads(json_str)

            source = PinReference(
                data["source"]["component_id"],
                data["source"]["pin_id"]
            )
            destination = PinReference(
                data["destination"]["component_id"],
                data["destination"]["pin_id"]
            )

            conn = cls(source, destination, data["topic_name"])
            # Restore the original ID
            conn._id = data["id"]

            return conn
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"Invalid JSON format: {e.msg}",
                e.doc,
                e.pos
            )
        except KeyError as e:
            raise KeyError(f"Missing required field in JSON: {e}")
        except TypeError as e:
            raise TypeError(f"Invalid field type in JSON: {e}")

    def __repr__(self) -> str:
        """Return string representation of this connection.

        Returns:
            str: String showing source, destination, topic, and ID prefix

        Examples:
            >>> source = PinReference("comp-1", "pin-1")
            >>> dest = PinReference("comp-2", "pin-2")
            >>> conn = Connection(source, dest, "test")
            >>> "Connection(" in repr(conn)
            True
        """
        return (f"Connection("
                f"id={self._id[:8]}..., "
                f"source={self._source.component_id[:8]}.../"
                f"{self._source.pin_id[:8]}..., "
                f"destination={self._destination.component_id[:8]}.../"
                f"{self._destination.pin_id[:8]}..., "
                f"topic='{self._topic_name}')")

    def __str__(self) -> str:
        """Return user-friendly string representation.

        Returns:
            str: A readable description of the connection

        Examples:
            >>> source = PinReference("comp-A", "out")
            >>> dest = PinReference("comp-B", "in")
            >>> conn = Connection(source, dest, "data")
            >>> str(conn)
            'comp-A/out -> comp-B/in (data)'
        """
        return (f"{self._source.component_id}/{self._source.pin_id} -> "
                f"{self._destination.component_id}/{self._destination.pin_id} "
                f"({self._topic_name})")

    def __eq__(self, other: object) -> bool:
        """Check equality based on connection ID.

        Args:
            other: Another Connection or other object

        Returns:
            bool: True if connections have the same ID
        """
        if isinstance(other, Connection):
            return self._id == other._id
        return False

    def __hash__(self) -> int:
        """Return hash of this connection based on its ID.

        Returns:
            int: Hash of the connection's UUID
        """
        return hash(self._id)


class ConnectionManager:
    """Manages all connections in the VSE_PY system.

    The ConnectionManager maintains a registry of all connections between
    component pins, providing methods to add, remove, and query connections.
    It validates all connections and can report on connections for specific
    components.

    Examples:
        >>> manager = ConnectionManager()
        >>> source = PinReference("comp-1", "out-1")
        >>> dest = PinReference("comp-2", "in-1")
        >>> conn = Connection(source, dest, "topic-1")
        >>> manager.add_connection(conn)
        >>> manager.get_all_connections()
        [Connection(...)]
    """

    def __init__(self) -> None:
        """Initialize a new ConnectionManager.

        Creates an empty connection registry.
        """
        self._connections: Dict[str, Connection] = {}

    def add_connection(self, connection: Connection) -> bool:
        """Add a connection to the manager.

        Validates the connection before adding. If a connection with the
        same ID already exists, it is replaced.

        Args:
            connection: The Connection instance to add

        Returns:
            bool: True if connection was added successfully, False if validation failed

        Raises:
            TypeError: If connection is not a Connection instance

        Examples:
            >>> manager = ConnectionManager()
            >>> source = PinReference("comp-1", "out-1")
            >>> dest = PinReference("comp-2", "in-1")
            >>> conn = Connection(source, dest, "data")
            >>> manager.add_connection(conn)
            True
        """
        if not isinstance(connection, Connection):
            raise TypeError("connection must be a Connection instance")

        if not connection.validate():
            return False

        self._connections[connection.id] = connection
        return True

    def remove_connection(self, connection_id: str) -> bool:
        """Remove a connection from the manager.

        Args:
            connection_id: The ID of the connection to remove

        Returns:
            bool: True if connection was removed, False if ID not found

        Examples:
            >>> manager = ConnectionManager()
            >>> source = PinReference("comp-1", "out-1")
            >>> dest = PinReference("comp-2", "in-1")
            >>> conn = Connection(source, dest, "data")
            >>> manager.add_connection(conn)
            True
            >>> manager.remove_connection(conn.id)
            True
            >>> manager.remove_connection(conn.id)
            False
        """
        if connection_id in self._connections:
            del self._connections[connection_id]
            return True
        return False

    def remove_connections_for_component(self, component_id: str) -> int:
        """Remove all connections associated with a component.

        Removes all connections where the component appears as either
        source or destination.

        Args:
            component_id: The ID of the component

        Returns:
            int: Number of connections removed

        Examples:
            >>> manager = ConnectionManager()
            >>> source = PinReference("comp-1", "out-1")
            >>> dest = PinReference("comp-2", "in-1")
            >>> conn1 = Connection(source, dest, "topic-1")
            >>> conn2 = Connection(dest, source, "topic-2")
            >>> manager.add_connection(conn1)
            True
            >>> manager.add_connection(conn2)
            True
            >>> manager.remove_connections_for_component("comp-1")
            2
        """
        conn_ids_to_remove = []

        for conn_id, conn in self._connections.items():
            if (conn.source.component_id == component_id or
                conn.destination.component_id == component_id):
                conn_ids_to_remove.append(conn_id)

        for conn_id in conn_ids_to_remove:
            del self._connections[conn_id]

        return len(conn_ids_to_remove)

    def get_connections_for_component(self, component_id: str) -> List[Connection]:
        """Get all connections for a specific component.

        Returns all connections where the component appears as either
        source or destination.

        Args:
            component_id: The ID of the component

        Returns:
            List[Connection]: List of connections for this component

        Examples:
            >>> manager = ConnectionManager()
            >>> source = PinReference("comp-1", "out-1")
            >>> dest = PinReference("comp-2", "in-1")
            >>> conn = Connection(source, dest, "topic-1")
            >>> manager.add_connection(conn)
            True
            >>> conns = manager.get_connections_for_component("comp-1")
            >>> len(conns)
            1
            >>> conns[0].topic_name
            'topic-1'
        """
        result = []

        for conn in self._connections.values():
            if (conn.source.component_id == component_id or
                conn.destination.component_id == component_id):
                result.append(conn)

        return result

    def get_all_connections(self) -> List[Connection]:
        """Get all connections in the manager.

        Returns:
            List[Connection]: List of all connections

        Examples:
            >>> manager = ConnectionManager()
            >>> source = PinReference("comp-1", "out-1")
            >>> dest = PinReference("comp-2", "in-1")
            >>> conn = Connection(source, dest, "topic-1")
            >>> manager.add_connection(conn)
            True
            >>> manager.get_all_connections()
            [Connection(...)]
        """
        return list(self._connections.values())

    def validate_all(self) -> bool:
        """Validate all connections in the manager.

        Checks that all stored connections are still valid. This can be useful
        after deserializing or loading connections from storage.

        Returns:
            bool: True if all connections are valid, False if any are invalid

        Examples:
            >>> manager = ConnectionManager()
            >>> source = PinReference("comp-1", "out-1")
            >>> dest = PinReference("comp-2", "in-1")
            >>> conn = Connection(source, dest, "data")
            >>> manager.add_connection(conn)
            True
            >>> manager.validate_all()
            True
        """
        for conn in self._connections.values():
            if not conn.validate():
                return False
        return True

    def clear(self) -> None:
        """Clear all connections from the manager.

        Removes all connections, resetting the manager to an empty state.

        Examples:
            >>> manager = ConnectionManager()
            >>> source = PinReference("comp-1", "out-1")
            >>> dest = PinReference("comp-2", "in-1")
            >>> conn = Connection(source, dest, "data")
            >>> manager.add_connection(conn)
            True
            >>> manager.clear()
            >>> len(manager.get_all_connections())
            0
        """
        self._connections.clear()

    def __len__(self) -> int:
        """Return the number of connections in the manager.

        Returns:
            int: Number of connections
        """
        return len(self._connections)

    def __repr__(self) -> str:
        """Return string representation of this manager.

        Returns:
            str: String showing number of managed connections
        """
        return f"ConnectionManager(connections={len(self._connections)})"

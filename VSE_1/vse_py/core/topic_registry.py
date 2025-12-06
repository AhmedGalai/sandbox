"""Topic and TopicRegistry classes

This module provides the topic-based pub/sub system for VSE_PY. It includes:
- Topic: A named publication channel with type checking and subscriber management
- TopicRegistry: Thread-safe singleton registry managing all topics in the system
"""

from typing import Dict, Set, Callable, Optional
from threading import Lock
from .data_types import DataVariant, DataType


class Topic:
    """A named publication channel for data distribution with type checking.

    A Topic represents a named channel through which data can be published to
    multiple subscribers. Topics enforce type compatibility and maintain
    statistics about publications. All operations are thread-safe through
    internal locking.

    Attributes:
        name: The unique name of this topic
        expected_type: The DataType expected for values published on this topic
        publish_count: Number of times data has been published to this topic
        last_value: The most recently published value (None if never published)

    Examples:
        >>> topic = Topic("sensor_data", DataType.FLOAT)
        >>> def on_data(topic_name: str, data: DataVariant):
        ...     print(f"Received on {topic_name}: {data.value}")
        >>> sub_id = topic.subscribe(on_data)
        >>> topic.publish(DataVariant(42.5))
        >>> topic.unsubscribe(sub_id)
    """

    def __init__(self, name: str, expected_type: DataType) -> None:
        """Initialize a Topic.

        Args:
            name: Unique name identifying this topic
            expected_type: DataType for values published on this topic

        Raises:
            ValueError: If name is empty
            TypeError: If expected_type is not a DataType

        Examples:
            >>> topic = Topic("temperature", DataType.FLOAT)
            >>> topic.name
            'temperature'
        """
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Topic name must be a non-empty string")
        if not isinstance(expected_type, DataType):
            raise TypeError("expected_type must be a DataType enum value")

        self._name: str = name
        self._expected_type: DataType = expected_type
        self._subscribers: Dict[str, Callable[[str, DataVariant], None]] = {}
        self._publish_count: int = 0
        self._last_value: Optional[DataVariant] = None
        self._lock: Lock = Lock()

    @property
    def name(self) -> str:
        """Get the name of this topic.

        Returns:
            str: The topic's unique name
        """
        return self._name

    @property
    def expected_type(self) -> DataType:
        """Get the expected data type for this topic.

        Returns:
            DataType: The DataType expected for published values
        """
        return self._expected_type

    @property
    def publish_count(self) -> int:
        """Get the number of times data has been published to this topic.

        Returns:
            int: Total publish count

        Examples:
            >>> topic = Topic("counter", DataType.INTEGER)
            >>> topic.publish_count
            0
            >>> topic.publish(DataVariant(1))
            >>> topic.publish_count
            1
        """
        with self._lock:
            return self._publish_count

    @property
    def last_value(self) -> Optional[DataVariant]:
        """Get the last value published to this topic.

        Returns:
            Optional[DataVariant]: The most recent value, or None if never published

        Examples:
            >>> topic = Topic("data", DataType.STRING)
            >>> topic.last_value is None
            True
            >>> topic.publish(DataVariant("hello"))
            >>> topic.last_value.value
            'hello'
        """
        with self._lock:
            return self._last_value

    def publish(self, data: DataVariant) -> bool:
        """Publish data to this topic.

        Publishes the data to all subscribers and updates statistics.
        Type checking is performed if the topic has an expected type.
        If expected_type is DataType.ANY, any value is accepted.

        Args:
            data: The DataVariant to publish

        Returns:
            bool: True if publish succeeded, False if type is incompatible

        Raises:
            TypeError: If data is not a DataVariant

        Examples:
            >>> topic = Topic("temp", DataType.FLOAT)
            >>> topic.publish(DataVariant(23.5))
            True
            >>> topic.publish(DataVariant("text"))
            False
        """
        if not isinstance(data, DataVariant):
            raise TypeError("data must be a DataVariant instance")

        with self._lock:
            # Check type compatibility
            if self._expected_type != DataType.ANY:
                if data.dtype != DataType.ANY and data.dtype != self._expected_type:
                    return False

            # Update statistics
            self._publish_count += 1
            self._last_value = data

            # Notify all subscribers
            # Create a copy of subscribers to avoid holding lock during callbacks
            subscribers_copy = list(self._subscribers.items())

        # Call subscribers outside the lock to prevent deadlocks
        for sub_id, callback in subscribers_copy:
            try:
                callback(self._name, data)
            except Exception as e:
                # Log callback errors but don't propagate them
                print(f"Error in Topic '{self._name}' subscriber {sub_id}: {e}")

        return True

    def subscribe(self, callback: Callable[[str, DataVariant], None]) -> str:
        """Subscribe to this topic with a callback function.

        The callback will be invoked whenever data is published to this topic.
        The callback receives two arguments: topic name (str) and data (DataVariant).

        Args:
            callback: Function taking (topic_name: str, data: DataVariant) and
                     returning None

        Returns:
            str: Subscriber ID that can be used to unsubscribe

        Raises:
            TypeError: If callback is not callable

        Examples:
            >>> topic = Topic("updates", DataType.STRING)
            >>> def handler(name, data):
            ...     print(f"{name}: {data.value}")
            >>> sub_id = topic.subscribe(handler)
            >>> topic.publish(DataVariant("new data"))
            updates: new data
            >>> topic.unsubscribe(sub_id)
        """
        if not callable(callback):
            raise TypeError("callback must be callable")

        with self._lock:
            # Generate unique subscriber ID
            import uuid
            sub_id = str(uuid.uuid4())
            self._subscribers[sub_id] = callback
            return sub_id

    def unsubscribe(self, subscriber_id: str) -> bool:
        """Unsubscribe a callback from this topic.

        Args:
            subscriber_id: The ID returned by subscribe()

        Returns:
            bool: True if unsubscribed, False if ID not found

        Examples:
            >>> topic = Topic("test", DataType.INTEGER)
            >>> sub_id = topic.subscribe(lambda n, d: None)
            >>> topic.unsubscribe(sub_id)
            True
            >>> topic.unsubscribe(sub_id)
            False
        """
        with self._lock:
            if subscriber_id in self._subscribers:
                del self._subscribers[subscriber_id]
                return True
            return False

    def get_subscriber_count(self) -> int:
        """Get the number of active subscribers to this topic.

        Returns:
            int: Number of subscribed callbacks

        Examples:
            >>> topic = Topic("data", DataType.INTEGER)
            >>> topic.get_subscriber_count()
            0
            >>> sub_id = topic.subscribe(lambda n, d: None)
            >>> topic.get_subscriber_count()
            1
        """
        with self._lock:
            return len(self._subscribers)

    def clear_subscribers(self) -> None:
        """Remove all subscribers from this topic.

        Examples:
            >>> topic = Topic("data", DataType.STRING)
            >>> topic.subscribe(lambda n, d: None)
            >>> topic.clear_subscribers()
            >>> topic.get_subscriber_count()
            0
        """
        with self._lock:
            self._subscribers.clear()

    def __repr__(self) -> str:
        """Return string representation of this topic.

        Returns:
            str: String showing name, type, and subscriber count
        """
        return (f"Topic("
                f"name='{self._name}', "
                f"type={self._expected_type.name}, "
                f"subscribers={self.get_subscriber_count()})")

    def __str__(self) -> str:
        """Return user-friendly string representation.

        Returns:
            str: A readable description of the topic
        """
        return f"{self._name} ({self._expected_type.name})"


class TopicRegistry:
    """Thread-safe singleton registry for all topics in VSE_PY.

    The TopicRegistry maintains a centralized repository of all topics in the
    system. It provides methods to create, delete, and interact with topics.
    The registry is implemented as a thread-safe singleton using double-checked
    locking to ensure only one instance exists.

    This is a singleton - access via TopicRegistry.instance()

    Examples:
        >>> registry = TopicRegistry.instance()
        >>> registry.create_topic("sensor_data", DataType.FLOAT)
        >>> registry.publish("sensor_data", DataVariant(23.5))
        >>> def handler(name, data):
        ...     print(f"Got: {data.value}")
        >>> sub_id = registry.subscribe("sensor_data", handler)
        >>> registry.delete_topic("sensor_data")
    """

    _instance: Optional["TopicRegistry"] = None
    _instance_lock: Lock = Lock()

    def __new__(cls) -> "TopicRegistry":
        """Create or return the singleton instance.

        Uses double-checked locking pattern for thread-safe singleton creation.

        Returns:
            TopicRegistry: The singleton instance
        """
        # First check without lock (fast path)
        if cls._instance is None:
            # Check again inside lock (slow path)
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = super(TopicRegistry, cls).__new__(cls)
                    # Initialize only once
                    cls._instance._initialized = False

        return cls._instance

    def __init__(self) -> None:
        """Initialize the TopicRegistry (called only once for singleton).

        Uses a flag to ensure initialization happens only on first creation.
        """
        # Only initialize once
        if hasattr(self, '_initialized') and self._initialized:
            return

        self._topics: Dict[str, Topic] = {}
        self._lock: Lock = Lock()
        self._initialized = True

    @classmethod
    def instance(cls) -> "TopicRegistry":
        """Get the singleton instance of TopicRegistry.

        Returns:
            TopicRegistry: The singleton instance

        Examples:
            >>> registry = TopicRegistry.instance()
            >>> registry2 = TopicRegistry.instance()
            >>> registry is registry2
            True
        """
        return cls()

    def create_topic(self, name: str, expected_type: DataType) -> bool:
        """Create a new topic in the registry.

        Args:
            name: Unique name for the topic
            expected_type: DataType for values published to this topic

        Returns:
            bool: True if topic was created, False if name already exists

        Raises:
            ValueError: If name is empty
            TypeError: If expected_type is not a DataType

        Examples:
            >>> registry = TopicRegistry.instance()
            >>> registry.create_topic("temperature", DataType.FLOAT)
            True
            >>> registry.create_topic("temperature", DataType.FLOAT)
            False
        """
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Topic name must be a non-empty string")
        if not isinstance(expected_type, DataType):
            raise TypeError("expected_type must be a DataType enum value")

        with self._lock:
            if name in self._topics:
                return False

            self._topics[name] = Topic(name, expected_type)
            return True

    def delete_topic(self, name: str) -> bool:
        """Delete a topic from the registry.

        Args:
            name: Name of the topic to delete

        Returns:
            bool: True if topic was deleted, False if not found

        Examples:
            >>> registry = TopicRegistry.instance()
            >>> registry.create_topic("temp", DataType.FLOAT)
            True
            >>> registry.delete_topic("temp")
            True
            >>> registry.delete_topic("temp")
            False
        """
        with self._lock:
            if name in self._topics:
                del self._topics[name]
                return True
            return False

    def has_topic(self, name: str) -> bool:
        """Check if a topic exists in the registry.

        Args:
            name: Name of the topic to check

        Returns:
            bool: True if topic exists, False otherwise

        Examples:
            >>> registry = TopicRegistry.instance()
            >>> registry.create_topic("data", DataType.STRING)
            True
            >>> registry.has_topic("data")
            True
            >>> registry.has_topic("nonexistent")
            False
        """
        with self._lock:
            return name in self._topics

    def get_topic(self, name: str) -> Optional[Topic]:
        """Get a topic from the registry.

        Args:
            name: Name of the topic to retrieve

        Returns:
            Optional[Topic]: The Topic instance, or None if not found

        Examples:
            >>> registry = TopicRegistry.instance()
            >>> registry.create_topic("test", DataType.INTEGER)
            True
            >>> topic = registry.get_topic("test")
            >>> topic.name
            'test'
            >>> registry.get_topic("nonexistent") is None
            True
        """
        with self._lock:
            return self._topics.get(name)

    def publish(self, topic_name: str, data: DataVariant) -> bool:
        """Publish data to a topic.

        Args:
            topic_name: Name of the topic to publish to
            data: The DataVariant to publish

        Returns:
            bool: True if publish succeeded, False if topic not found or type mismatch

        Raises:
            TypeError: If data is not a DataVariant

        Examples:
            >>> registry = TopicRegistry.instance()
            >>> registry.create_topic("value", DataType.FLOAT)
            True
            >>> registry.publish("value", DataVariant(3.14))
            True
            >>> registry.publish("nonexistent", DataVariant(1))
            False
        """
        if not isinstance(data, DataVariant):
            raise TypeError("data must be a DataVariant instance")

        with self._lock:
            topic = self._topics.get(topic_name)
            if topic is None:
                return False

        # Call publish outside the lock to avoid deadlocks
        return topic.publish(data)

    def subscribe(
        self,
        topic_name: str,
        callback: Callable[[str, DataVariant], None]
    ) -> Optional[str]:
        """Subscribe to a topic.

        Args:
            topic_name: Name of the topic to subscribe to
            callback: Function taking (topic_name: str, data: DataVariant)
                     and returning None

        Returns:
            Optional[str]: Subscriber ID if successful, None if topic not found

        Raises:
            TypeError: If callback is not callable

        Examples:
            >>> registry = TopicRegistry.instance()
            >>> registry.create_topic("updates", DataType.STRING)
            True
            >>> def handler(name, data):
            ...     print(f"{name}: {data.value}")
            >>> sub_id = registry.subscribe("updates", handler)
            >>> sub_id is not None
            True
        """
        if not callable(callback):
            raise TypeError("callback must be callable")

        with self._lock:
            topic = self._topics.get(topic_name)
            if topic is None:
                return None

        # Call subscribe outside the lock
        return topic.subscribe(callback)

    def unsubscribe(self, topic_name: str, subscriber_id: str) -> bool:
        """Unsubscribe from a topic.

        Args:
            topic_name: Name of the topic
            subscriber_id: The subscriber ID returned by subscribe()

        Returns:
            bool: True if unsubscribed, False if topic or subscriber not found

        Examples:
            >>> registry = TopicRegistry.instance()
            >>> registry.create_topic("data", DataType.INTEGER)
            True
            >>> sub_id = registry.subscribe("data", lambda n, d: None)
            >>> registry.unsubscribe("data", sub_id)
            True
        """
        with self._lock:
            topic = self._topics.get(topic_name)
            if topic is None:
                return False

        # Call unsubscribe outside the lock
        return topic.unsubscribe(subscriber_id)

    def get_all_topic_names(self) -> list:
        """Get names of all topics in the registry.

        Returns:
            list: List of topic names

        Examples:
            >>> registry = TopicRegistry.instance()
            >>> registry.create_topic("topic1", DataType.STRING)
            True
            >>> registry.create_topic("topic2", DataType.INTEGER)
            True
            >>> "topic1" in registry.get_all_topic_names()
            True
        """
        with self._lock:
            return list(self._topics.keys())

    def get_all_topics(self) -> Dict[str, Topic]:
        """Get all topics in the registry.

        Returns a shallow copy to prevent external modification.

        Returns:
            Dict[str, Topic]: Dictionary mapping topic names to Topic instances

        Examples:
            >>> registry = TopicRegistry.instance()
            >>> registry.create_topic("test", DataType.FLOAT)
            True
            >>> topics = registry.get_all_topics()
            >>> "test" in topics
            True
        """
        with self._lock:
            return self._topics.copy()

    def clear(self) -> None:
        """Clear all topics from the registry.

        This removes all topics and their subscribers. Useful for cleanup
        and testing.

        Examples:
            >>> registry = TopicRegistry.instance()
            >>> registry.create_topic("topic1", DataType.STRING)
            True
            >>> registry.clear()
            >>> registry.get_all_topic_names()
            []
        """
        with self._lock:
            self._topics.clear()

    def get_topic_count(self) -> int:
        """Get the number of topics in the registry.

        Returns:
            int: Total number of topics

        Examples:
            >>> registry = TopicRegistry.instance()
            >>> registry.clear()
            >>> registry.get_topic_count()
            0
            >>> registry.create_topic("t1", DataType.STRING)
            True
            >>> registry.get_topic_count()
            1
        """
        with self._lock:
            return len(self._topics)

    def __repr__(self) -> str:
        """Return string representation of the registry.

        Returns:
            str: String showing number of topics
        """
        return f"TopicRegistry(topics={self.get_topic_count()})"

    def __str__(self) -> str:
        """Return user-friendly string representation.

        Returns:
            str: List of all topic names
        """
        names = self.get_all_topic_names()
        if not names:
            return "TopicRegistry(empty)"
        return f"TopicRegistry({', '.join(names)})"

"""PublisherComponent base class for data publishing components.

This module provides the abstract base class for components that publish data
at regular intervals or on-demand. Publishers are commonly used as sources
in VSE_PY graphs to feed data into the processing pipeline.

Features:
- Green color designation for visual identification
- Periodic publishing support with configurable intervals
- Optional background thread for timer-based publication
- Abstract publish() method for subclass customization
"""

from abc import abstractmethod
from typing import Optional
import threading
import time

from ..core.component_base import ComponentBase, ComponentState
from ..core.data_types import DataType, DataVariant


class PublisherComponent(ComponentBase):
    """Abstract base class for components that publish data.

    PublisherComponent extends ComponentBase to provide a framework for components
    that act as data sources, publishing output at regular intervals or on-demand.

    Key features:
    - Green color (76, 175, 80) for visual identification in graphs
    - "Publisher" category classification
    - Optional periodic publishing with configurable intervals
    - Background thread support for timer-based execution
    - Abstract publish() method for subclass implementation

    Attributes:
        periodic_publishing: Whether periodic publishing is enabled
        publish_interval: Interval in seconds between publications

    Examples:
        >>> class SensorPublisher(PublisherComponent):
        ...     def get_name(self):
        ...         return "Temperature Sensor"
        ...     def publish(self):
        ...         output = self.get_output_pin("Temperature")
        ...         output.transmit_data(DataVariant(23.5))
        >>> publisher = SensorPublisher()
        >>> publisher.set_periodic_publishing(True)
        >>> publisher.set_publish_interval(1.0)
        >>> publisher.start()
    """

    def __init__(self) -> None:
        """Initialize a PublisherComponent.

        Sets up periodic publishing support and initializes the background timer thread.
        """
        self._periodic_publishing: bool = False
        self._publish_interval: float = 1.0  # Default 1 second
        self._timer_thread: Optional[threading.Thread] = None
        self._should_stop: bool = False

        super().__init__()

    def get_category(self) -> str:
        """Get the component category.

        Returns:
            str: "Publisher"
        """
        return "Publisher"

    def get_color(self) -> tuple:
        """Get the component display color.

        Returns:
            tuple: Green color (76, 175, 80)
        """
        return (76, 175, 80)

    def set_periodic_publishing(self, enabled: bool) -> None:
        """Enable or disable periodic publishing.

        When enabled, the component will publish data at regular intervals
        defined by the publish_interval. When disabled, publishing only
        occurs on explicit calls to publish().

        Args:
            enabled: True to enable periodic publishing, False to disable

        Raises:
            TypeError: If enabled is not a boolean

        Examples:
            >>> publisher.set_periodic_publishing(True)
            >>> publisher.set_periodic_publishing(False)
        """
        if not isinstance(enabled, bool):
            raise TypeError("enabled must be a boolean")

        self._periodic_publishing = enabled

    def set_publish_interval(self, interval: float) -> None:
        """Set the publishing interval in seconds.

        This interval is used when periodic publishing is enabled. The actual
        time between publications may be slightly longer due to the time taken
        by the publish() method itself.

        Args:
            interval: Time in seconds between publications (must be positive)

        Raises:
            ValueError: If interval is not positive
            TypeError: If interval is not a number

        Examples:
            >>> publisher.set_publish_interval(0.5)  # Publish every 500ms
            >>> publisher.set_publish_interval(10.0)  # Publish every 10 seconds
        """
        try:
            interval_float = float(interval)
        except (TypeError, ValueError):
            raise TypeError("interval must be a number")

        if interval_float <= 0:
            raise ValueError("interval must be positive")

        self._publish_interval = interval_float

    @property
    def periodic_publishing(self) -> bool:
        """Get periodic publishing status.

        Returns:
            bool: True if periodic publishing is enabled
        """
        return self._periodic_publishing

    @property
    def publish_interval(self) -> float:
        """Get the current publish interval in seconds.

        Returns:
            float: The publish interval
        """
        return self._publish_interval

    @abstractmethod
    def publish(self) -> None:
        """Publish data from this component.

        Must be implemented by subclasses. This method should transmit data
        through the component's output pins.

        Subclasses should:
        1. Gather or generate data
        2. Transmit data via output_pin.transmit_data()
        3. Handle any errors by calling report_error()

        Examples:
            >>> def publish(self):
            ...     output = self.get_output_pin("Data")
            ...     output.transmit_data(DataVariant(42))
        """
        pass

    def execute(self) -> None:
        """Execute the component's main logic.

        Calls the abstract publish() method to generate and transmit data.
        This is called by the execution engine.

        Examples:
            >>> publisher.execute()
        """
        try:
            self.set_state(ComponentState.RUNNING)
            self.publish()
            self.set_state(ComponentState.IDLE)
        except Exception as e:
            self.report_error(f"Error during publish: {str(e)}")

    def start(self) -> None:
        """Start periodic publishing in a background thread.

        Launches a background thread that calls publish() at the configured
        interval. If periodic publishing is not enabled, this method does nothing.

        Can be called multiple times safely; if a timer is already running,
        subsequent calls are ignored.

        Examples:
            >>> publisher.set_periodic_publishing(True)
            >>> publisher.start()
        """
        if not self._periodic_publishing:
            return

        # Don't start if already running
        if self._timer_thread is not None and self._timer_thread.is_alive():
            return

        self._should_stop = False
        self._timer_thread = threading.Thread(target=self._timer_loop, daemon=True)
        self._timer_thread.start()

    def stop(self) -> None:
        """Stop periodic publishing.

        Signals the background timer thread to exit. The thread is given a short
        grace period to exit cleanly before returning.

        Safe to call even if publishing is not active.

        Examples:
            >>> publisher.stop()
        """
        self._should_stop = True

        # Wait briefly for thread to exit
        if self._timer_thread is not None:
            self._timer_thread.join(timeout=1.0)
            self._timer_thread = None

    def _timer_loop(self) -> None:
        """Background timer loop for periodic publishing.

        This method runs in a daemon thread and periodically calls publish().
        It respects the _should_stop flag to allow graceful shutdown.

        This is called internally; subclasses should not override this method.
        Override publish() instead.
        """
        while not self._should_stop:
            try:
                # Wait for the configured interval
                time.sleep(self._publish_interval)

                # Check again in case stop() was called during sleep
                if self._should_stop:
                    break

                # Call execute which in turn calls publish()
                self.execute()

            except Exception as e:
                # Log errors but continue the loop
                self.report_error(f"Error in timer loop: {str(e)}")

    def __del__(self) -> None:
        """Cleanup when component is destroyed.

        Ensures background thread is stopped before destruction.
        """
        try:
            self.stop()
        except Exception:
            pass

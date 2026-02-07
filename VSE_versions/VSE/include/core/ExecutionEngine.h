/**
 * @file ExecutionEngine.h
 * @brief Execution engine for running visual programs in VSE
 *
 * Manages the execution of component graphs with proper dependency ordering,
 * state management, and error handling. Integrates with Qt event loop for
 * smooth UI updates during execution.
 */

#ifndef VSE_CORE_EXECUTIONENGINE_H
#define VSE_CORE_EXECUTIONENGINE_H

#include <QObject>
#include <QTimer>
#include <QString>
#include <memory>
#include <vector>

namespace VSE {
namespace Core {

class ExecutionContext;
class Component;

/**
 * @enum ExecutionState
 * @brief States of the execution engine
 */
enum class ExecutionState {
    Idle,       ///< Not running, ready to start
    Running,    ///< Actively executing components
    Paused,     ///< Execution paused, can be resumed
    Error       ///< Error occurred, requires reset
};

/**
 * @enum ExecutionMode
 * @brief Execution modes controlling iteration behavior
 */
enum class ExecutionMode {
    Continuous,  ///< Execute repeatedly until stopped
    SingleStep   ///< Execute one iteration then pause
};

/**
 * @class ExecutionEngine
 * @brief Manages execution of component graphs
 *
 * The ExecutionEngine orchestrates the execution of visual programs by:
 * - Performing topological sort to determine execution order
 * - Managing execution state (idle, running, paused, error)
 * - Executing components in dependency order
 * - Handling errors gracefully with detailed reporting
 * - Integrating with Qt event loop via QTimer
 * - Controlling execution rate
 *
 * State transitions:
 * - Idle -> Running: start()
 * - Running -> Paused: pause()
 * - Running -> Idle: stop()
 * - Paused -> Running: start()
 * - Paused -> Idle: stop()
 * - Any -> Error: on execution error
 * - Error -> Idle: reset()
 *
 * Example usage:
 * @code
 * ExecutionEngine engine;
 * engine.setExecutionContext(context);
 * engine.setExecutionRate(60); // 60 iterations per second
 * engine.start();
 * @endcode
 */
class ExecutionEngine : public QObject {
    Q_OBJECT

public:
    /**
     * @brief Construct a new Execution Engine object
     * @param parent Parent QObject
     */
    explicit ExecutionEngine(QObject* parent = nullptr);

    /**
     * @brief Destructor
     */
    ~ExecutionEngine() override;

    /**
     * @brief Set the execution context containing the component graph
     * @param context Shared pointer to execution context
     */
    void setExecutionContext(std::shared_ptr<ExecutionContext> context);

    /**
     * @brief Get the current execution context
     * @return std::shared_ptr<ExecutionContext> Current context
     */
    std::shared_ptr<ExecutionContext> getExecutionContext() const;

    /**
     * @brief Get current execution state
     * @return ExecutionState Current state
     */
    ExecutionState getState() const { return m_state; }

    /**
     * @brief Get current execution mode
     * @return ExecutionMode Current mode
     */
    ExecutionMode getMode() const { return m_mode; }

    /**
     * @brief Set execution mode
     * @param mode New execution mode
     */
    void setMode(ExecutionMode mode);

    /**
     * @brief Get execution rate in iterations per second
     * @return double Execution rate (Hz)
     */
    double getExecutionRate() const { return m_executionRate; }

    /**
     * @brief Set execution rate
     * @param rate Iterations per second (0.1 to 1000 Hz)
     */
    void setExecutionRate(double rate);

    /**
     * @brief Get total iteration count
     * @return uint64_t Number of iterations completed
     */
    uint64_t getIterationCount() const { return m_iterationCount; }

    /**
     * @brief Get elapsed execution time in milliseconds
     * @return int64_t Elapsed time
     */
    int64_t getElapsedTimeMs() const;

    /**
     * @brief Get error count
     * @return size_t Number of errors encountered
     */
    size_t getErrorCount() const { return m_errorCount; }

    /**
     * @brief Get last error message
     * @return QString Last error message
     */
    QString getLastError() const { return m_lastError; }

    /**
     * @brief Check if execution is in progress
     * @return true if running
     */
    bool isRunning() const { return m_state == ExecutionState::Running; }

    /**
     * @brief Check if execution is paused
     * @return true if paused
     */
    bool isPaused() const { return m_state == ExecutionState::Paused; }

    /**
     * @brief Check if in error state
     * @return true if error occurred
     */
    bool hasError() const { return m_state == ExecutionState::Error; }

public slots:
    /**
     * @brief Start or resume execution
     *
     * Transitions from Idle or Paused to Running state.
     * Validates execution context before starting.
     */
    void start();

    /**
     * @brief Stop execution and reset to idle state
     *
     * Stops the execution timer and transitions to Idle state.
     * Does not clear statistics.
     */
    void stop();

    /**
     * @brief Pause execution
     *
     * Transitions from Running to Paused state.
     * Execution can be resumed with start().
     */
    void pause();

    /**
     * @brief Execute a single iteration then pause
     *
     * Executes one full iteration of all components in dependency order,
     * then automatically pauses. Useful for debugging.
     */
    void step();

    /**
     * @brief Reset execution engine to initial state
     *
     * Clears all statistics, errors, and transitions to Idle state.
     * Does not modify the execution context.
     */
    void reset();

signals:
    /**
     * @brief Emitted when execution state changes
     * @param newState New execution state
     * @param oldState Previous execution state
     */
    void stateChanged(ExecutionState newState, ExecutionState oldState);

    /**
     * @brief Emitted after each iteration completes
     * @param iteration Iteration number
     */
    void iterationCompleted(uint64_t iteration);

    /**
     * @brief Emitted when an error occurs
     * @param message Error message
     * @param componentId ID of component that caused error (if applicable)
     */
    void errorOccurred(const QString& message, const QString& componentId);

    /**
     * @brief Emitted when execution starts
     */
    void executionStarted();

    /**
     * @brief Emitted when execution stops
     */
    void executionStopped();

    /**
     * @brief Emitted when execution pauses
     */
    void executionPaused();

    /**
     * @brief Emitted when statistics update
     * @param iterations Total iterations
     * @param elapsedMs Elapsed time in milliseconds
     * @param errors Error count
     */
    void statisticsUpdated(uint64_t iterations, int64_t elapsedMs, size_t errors);

private slots:
    /**
     * @brief Execute one iteration (called by timer)
     */
    void executeIteration();

private:
    /**
     * @brief Change execution state and emit signal
     * @param newState New state to transition to
     */
    void setState(ExecutionState newState);

    /**
     * @brief Perform topological sort on component graph
     * @return true if sort successful (no cycles)
     */
    bool buildExecutionOrder();

    /**
     * @brief Validate execution context before starting
     * @return true if context is valid
     */
    bool validateContext();

    /**
     * @brief Handle execution error
     * @param message Error message
     * @param componentId Component that caused error
     */
    void handleError(const QString& message, const QString& componentId = "");

    /**
     * @brief Update timer interval based on execution rate
     */
    void updateTimerInterval();

    /**
     * @brief Reset statistics counters
     */
    void resetStatistics();

    // Execution state
    ExecutionState m_state;                              ///< Current execution state
    ExecutionMode m_mode;                                ///< Current execution mode
    std::shared_ptr<ExecutionContext> m_context;         ///< Execution context

    // Execution control
    QTimer* m_executionTimer;                            ///< Timer for execution loop
    double m_executionRate;                              ///< Iterations per second
    std::vector<Component*> m_executionOrder;            ///< Components in execution order

    // Statistics
    uint64_t m_iterationCount;                           ///< Total iterations executed
    int64_t m_startTimeMs;                               ///< Start time (milliseconds since epoch)
    size_t m_errorCount;                                 ///< Number of errors encountered
    QString m_lastError;                                 ///< Last error message

    // Safety limits
    static constexpr uint64_t MAX_ITERATIONS = 1000000000; ///< Maximum iterations before auto-stop
    static constexpr double MIN_EXEC_RATE = 0.1;         ///< Minimum execution rate (Hz)
    static constexpr double MAX_EXEC_RATE = 1000.0;      ///< Maximum execution rate (Hz)
};

/**
 * @brief Convert ExecutionState to string for debugging
 * @param state Execution state
 * @return QString String representation
 */
QString executionStateToString(ExecutionState state);

/**
 * @brief Convert ExecutionMode to string for debugging
 * @param mode Execution mode
 * @return QString String representation
 */
QString executionModeToString(ExecutionMode mode);

} // namespace Core
} // namespace VSE

#endif // VSE_CORE_EXECUTIONENGINE_H

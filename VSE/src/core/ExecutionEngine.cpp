/**
 * @file ExecutionEngine.cpp
 * @brief Implementation of the execution engine for VSE visual programs
 */

#include "core/ExecutionEngine.h"
#include "core/ExecutionContext.h"
#include "core/Component.h"
#include <QDateTime>
#include <QDebug>
#include <stdexcept>
#include <algorithm>

namespace VSE {
namespace Core {

ExecutionEngine::ExecutionEngine(QObject* parent)
    : QObject(parent)
    , m_state(ExecutionState::Idle)
    , m_mode(ExecutionMode::Continuous)
    , m_context(nullptr)
    , m_executionTimer(new QTimer(this))
    , m_executionRate(10.0)  // Default 10 Hz
    , m_iterationCount(0)
    , m_startTimeMs(0)
    , m_errorCount(0)
{
    // Connect timer to execution slot
    connect(m_executionTimer, &QTimer::timeout, this, &ExecutionEngine::executeIteration);

    // Set initial timer interval
    updateTimerInterval();
}

ExecutionEngine::~ExecutionEngine()
{
    // Ensure timer is stopped
    if (m_executionTimer->isActive()) {
        m_executionTimer->stop();
    }
}

void ExecutionEngine::setExecutionContext(std::shared_ptr<ExecutionContext> context)
{
    // Don't allow changing context while running
    if (m_state == ExecutionState::Running) {
        qWarning() << "Cannot change execution context while running";
        return;
    }

    m_context = context;

    // Clear execution order when context changes
    m_executionOrder.clear();
}

std::shared_ptr<ExecutionContext> ExecutionEngine::getExecutionContext() const
{
    return m_context;
}

void ExecutionEngine::setMode(ExecutionMode mode)
{
    m_mode = mode;
}

void ExecutionEngine::setExecutionRate(double rate)
{
    // Clamp to valid range
    m_executionRate = std::clamp(rate, MIN_EXEC_RATE, MAX_EXEC_RATE);
    updateTimerInterval();
}

int64_t ExecutionEngine::getElapsedTimeMs() const
{
    if (m_state == ExecutionState::Idle) {
        return 0;
    }

    int64_t currentTime = QDateTime::currentMSecsSinceEpoch();
    return currentTime - m_startTimeMs;
}

void ExecutionEngine::start()
{
    // Can start from Idle or Paused states
    if (m_state == ExecutionState::Running) {
        qDebug() << "Execution already running";
        return;
    }

    // Validate context before starting
    if (!validateContext()) {
        return;
    }

    // If starting from Idle, build execution order
    if (m_state == ExecutionState::Idle) {
        if (!buildExecutionOrder()) {
            handleError("Failed to build execution order (graph may have cycles)", "");
            return;
        }

        // Record start time
        m_startTimeMs = QDateTime::currentMSecsSinceEpoch();
    }

    // Transition to Running state
    setState(ExecutionState::Running);

    // Start execution timer
    m_executionTimer->start();

    emit executionStarted();
}

void ExecutionEngine::stop()
{
    if (m_state == ExecutionState::Idle) {
        return;
    }

    // Stop timer
    m_executionTimer->stop();

    // Transition to Idle state
    setState(ExecutionState::Idle);

    emit executionStopped();
}

void ExecutionEngine::pause()
{
    if (m_state != ExecutionState::Running) {
        return;
    }

    // Stop timer
    m_executionTimer->stop();

    // Transition to Paused state
    setState(ExecutionState::Paused);

    emit executionPaused();
}

void ExecutionEngine::step()
{
    // Can step from Idle or Paused states
    if (m_state == ExecutionState::Running) {
        qWarning() << "Cannot step while running (pause first)";
        return;
    }

    // Validate context
    if (!validateContext()) {
        return;
    }

    // Build execution order if needed
    if (m_state == ExecutionState::Idle) {
        if (!buildExecutionOrder()) {
            handleError("Failed to build execution order (graph may have cycles)", "");
            return;
        }

        // Record start time if first step
        if (m_iterationCount == 0) {
            m_startTimeMs = QDateTime::currentMSecsSinceEpoch();
        }
    }

    // Execute one iteration
    executeIteration();

    // Transition to Paused state
    if (m_state != ExecutionState::Error) {
        setState(ExecutionState::Paused);
    }
}

void ExecutionEngine::reset()
{
    // Stop timer if running
    m_executionTimer->stop();

    // Reset state
    setState(ExecutionState::Idle);

    // Clear statistics
    resetStatistics();

    // Clear execution order
    m_executionOrder.clear();

    // Clear error
    m_lastError.clear();
}

void ExecutionEngine::executeIteration()
{
    if (!m_context) {
        handleError("No execution context set", "");
        return;
    }

    // Safety check for runaway iterations
    if (m_iterationCount >= MAX_ITERATIONS) {
        handleError(QString("Maximum iteration limit reached (%1)").arg(MAX_ITERATIONS), "");
        stop();
        return;
    }

    // Execute each component in dependency order
    for (Component* component : m_executionOrder) {
        if (!component) {
            continue;
        }

        try {
            // Execute the component
            component->execute(m_context.get());
        }
        catch (const std::exception& e) {
            handleError(
                QString("Component execution failed: %1").arg(e.what()),
                component->getId()
            );
            return;  // Stop execution on error
        }
        catch (...) {
            handleError(
                "Component execution failed with unknown error",
                component->getId()
            );
            return;
        }
    }

    // Increment iteration count
    m_iterationCount++;

    // Update context statistics
    if (m_context) {
        m_context->updateIterationCount(m_iterationCount);
        m_context->updateElapsedTime(getElapsedTimeMs());
    }

    // Emit iteration completed signal
    emit iterationCompleted(m_iterationCount);

    // Emit statistics update
    emit statisticsUpdated(m_iterationCount, getElapsedTimeMs(), m_errorCount);

    // In single-step mode, pause after one iteration
    if (m_mode == ExecutionMode::SingleStep && m_state == ExecutionState::Running) {
        pause();
    }
}

void ExecutionEngine::setState(ExecutionState newState)
{
    if (m_state == newState) {
        return;
    }

    ExecutionState oldState = m_state;
    m_state = newState;

    emit stateChanged(newState, oldState);
}

bool ExecutionEngine::buildExecutionOrder()
{
    m_executionOrder.clear();

    if (!m_context) {
        qWarning() << "No execution context";
        return false;
    }

    // Build the execution graph
    if (!m_context->buildExecutionGraph()) {
        qWarning() << "Failed to build execution graph";
        return false;
    }

    // Get topologically sorted component IDs
    std::vector<QString> sortedIds;
    if (!m_context->getTopologicalOrder(sortedIds)) {
        qWarning() << "Failed to get topological order (graph has cycles)";
        return false;
    }

    // Convert IDs to component pointers
    m_executionOrder.reserve(sortedIds.size());
    for (const QString& id : sortedIds) {
        auto component = m_context->getComponent(id);
        if (component) {
            m_executionOrder.push_back(component.get());
        }
    }

    qDebug() << "Built execution order with" << m_executionOrder.size() << "components";
    return true;
}

bool ExecutionEngine::validateContext()
{
    if (!m_context) {
        handleError("No execution context set", "");
        return false;
    }

    if (m_context->getComponentCount() == 0) {
        handleError("Execution context has no components", "");
        return false;
    }

    // Validate the graph
    QString errorMessage;
    if (!m_context->validateGraph(errorMessage)) {
        handleError("Graph validation failed: " + errorMessage, "");
        return false;
    }

    return true;
}

void ExecutionEngine::handleError(const QString& message, const QString& componentId)
{
    m_lastError = message;
    m_errorCount++;

    // Update context error count
    if (m_context) {
        m_context->incrementErrorCount();
    }

    // Transition to error state
    setState(ExecutionState::Error);

    // Stop timer
    m_executionTimer->stop();

    // Emit error signal
    emit errorOccurred(message, componentId);

    // Log error
    qCritical() << "Execution error:" << message;
    if (!componentId.isEmpty()) {
        qCritical() << "Component:" << componentId;
    }
}

void ExecutionEngine::updateTimerInterval()
{
    // Convert rate (Hz) to interval (ms)
    int intervalMs = static_cast<int>(1000.0 / m_executionRate);
    m_executionTimer->setInterval(intervalMs);
}

void ExecutionEngine::resetStatistics()
{
    m_iterationCount = 0;
    m_startTimeMs = 0;
    m_errorCount = 0;

    if (m_context) {
        m_context->resetStatistics();
    }
}

// Utility functions

QString executionStateToString(ExecutionState state)
{
    switch (state) {
        case ExecutionState::Idle:    return "Idle";
        case ExecutionState::Running: return "Running";
        case ExecutionState::Paused:  return "Paused";
        case ExecutionState::Error:   return "Error";
        default:                      return "Unknown";
    }
}

QString executionModeToString(ExecutionMode mode)
{
    switch (mode) {
        case ExecutionMode::Continuous: return "Continuous";
        case ExecutionMode::SingleStep: return "Single-Step";
        default:                        return "Unknown";
    }
}

} // namespace Core
} // namespace VSE

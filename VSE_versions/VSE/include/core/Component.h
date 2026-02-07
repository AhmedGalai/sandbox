/**
 * @file Component.h
 * @brief Base component class for all VSE visual scripting components
 *
 * Provides the foundational interface for all components in the visual
 * scripting system, including pins, parameters, and execution lifecycle.
 */

#ifndef VSE_CORE_COMPONENT_H
#define VSE_CORE_COMPONENT_H

#include "core/Pin.h"
#include "core/Parameter.h"
#include <QObject>
#include <QString>
#include <memory>
#include <vector>
#include <nlohmann/json.hpp>

namespace VSE {
namespace Core {

// Forward declaration
class ExecutionContext;

/**
 * @class Component
 * @brief Abstract base class for all visual scripting components
 *
 * Components are the building blocks of visual programs. They have:
 * - Input and output pins for data connections
 * - Parameters for configuration
 * - An execute() method that performs computation
 * - Serialization support for saving/loading
 * - Unique identifier for graph management
 *
 * Component lifecycle:
 * 1. Construction: Create pins and parameters
 * 2. Configuration: User sets parameter values
 * 3. Connection: Pins connected to form graph
 * 4. Execution: execute() called by engine
 * 5. Cleanup: Automatic on destruction
 *
 * Example:
 * @code
 * class MyComponent : public Component {
 * public:
 *     MyComponent() : Component("My Component", "Custom") {
 *         addInputPin("input", DataType::Integer);
 *         addOutputPin("output", DataType::Integer);
 *         addParameter(std::make_shared<IntParameter>("multiplier", 2));
 *     }
 *
 *     void execute(ExecutionContext* context) override {
 *         // Get input value
 *         // Perform computation
 *         // Set output value
 *     }
 * };
 * @endcode
 */
class Component : public QObject {
    Q_OBJECT

public:
    /**
     * @brief Construct a new Component
     * @param name Component type name
     * @param category Component category for organization
     * @param parent Qt parent object
     */
    Component(const QString& name, const QString& category = "General", QObject* parent = nullptr);

    /**
     * @brief Virtual destructor
     */
    virtual ~Component();

    /**
     * @brief Get component type name
     * @return const QString& Component name
     */
    const QString& getName() const { return m_name; }

    /**
     * @brief Get component category
     * @return const QString& Category name
     */
    const QString& getCategory() const { return m_category; }

    /**
     * @brief Get unique instance ID
     * @return const QString& Unique identifier
     */
    const QString& getId() const { return m_id; }

    /**
     * @brief Set unique instance ID
     * @param id New identifier
     */
    void setId(const QString& id) { m_id = id; }

    /**
     * @brief Get user-facing display name
     * @return QString Display name (defaults to type name if not set)
     */
    QString getDisplayName() const;

    /**
     * @brief Set user-facing display name
     * @param name Display name
     */
    void setDisplayName(const QString& name) { m_displayName = name; }

    /**
     * @brief Execute component logic
     * @param context Execution context (access to global state, other components)
     *
     * This is the main computation method that derived classes must implement.
     * It should:
     * - Read input pin values
     * - Perform computation
     * - Write output pin values
     * - Handle errors gracefully
     */
    virtual void execute(ExecutionContext* context) = 0;

    /**
     * @brief Serialize component to JSON
     * @return nlohmann::json JSON representation including parameters and connections
     */
    virtual nlohmann::json serialize() const;

    /**
     * @brief Deserialize component from JSON
     * @param json JSON data
     * @return true if successful
     */
    virtual bool deserialize(const nlohmann::json& json);

    // Pin management

    /**
     * @brief Add an input pin
     * @param name Pin name
     * @param dataType Data type accepted
     * @return Shared pointer to created pin
     */
    std::shared_ptr<InputPin> addInputPin(const QString& name, DataType dataType);

    /**
     * @brief Add an output pin
     * @param name Pin name
     * @param dataType Data type produced
     * @return Shared pointer to created pin
     */
    std::shared_ptr<OutputPin> addOutputPin(const QString& name, DataType dataType);

    /**
     * @brief Get all input pins
     * @return const std::vector<std::shared_ptr<InputPin>>& Input pins
     */
    const std::vector<std::shared_ptr<InputPin>>& getInputPins() const { return m_inputPins; }

    /**
     * @brief Get all output pins
     * @return const std::vector<std::shared_ptr<OutputPin>>& Output pins
     */
    const std::vector<std::shared_ptr<OutputPin>>& getOutputPins() const { return m_outputPins; }

    /**
     * @brief Find input pin by name
     * @param name Pin name
     * @return std::shared_ptr<InputPin> Pin pointer or nullptr if not found
     */
    std::shared_ptr<InputPin> getInputPin(const QString& name) const;

    /**
     * @brief Find output pin by name
     * @param name Pin name
     * @return std::shared_ptr<OutputPin> Pin pointer or nullptr if not found
     */
    std::shared_ptr<OutputPin> getOutputPin(const QString& name) const;

    // Parameter management

    /**
     * @brief Add a parameter
     * @param parameter Parameter to add
     */
    void addParameter(std::shared_ptr<Parameter> parameter);

    /**
     * @brief Get all parameters
     * @return const std::vector<std::shared_ptr<Parameter>>& Parameters
     */
    const std::vector<std::shared_ptr<Parameter>>& getParameters() const { return m_parameters; }

    /**
     * @brief Find parameter by name
     * @param name Parameter name
     * @return std::shared_ptr<Parameter> Parameter pointer or nullptr if not found
     */
    std::shared_ptr<Parameter> getParameter(const QString& name) const;

    /**
     * @brief Get parameter value as specific type
     * @tparam T Parameter type (IntParameter, FloatParameter, etc.)
     * @param name Parameter name
     * @return std::shared_ptr<T> Typed parameter pointer or nullptr
     */
    template<typename T>
    std::shared_ptr<T> getParameter(const QString& name) const;

    /**
     * @brief Check if component has been executed at least once
     * @return true if executed
     */
    bool hasExecuted() const { return m_hasExecuted; }

    /**
     * @brief Reset execution state
     */
    void resetExecutionState();

signals:
    /**
     * @brief Emitted when component finishes execution
     */
    void executionFinished();

    /**
     * @brief Emitted when an error occurs during execution
     * @param message Error message
     */
    void executionError(const QString& message);

    /**
     * @brief Emitted when a parameter value changes
     * @param parameterName Name of changed parameter
     */
    void parameterChanged(const QString& parameterName);

protected:
    /**
     * @brief Helper to get input pin value safely
     * @param pinName Input pin name
     * @return QVariant Value from pin (or invalid QVariant if not found/connected)
     */
    QVariant getInputValue(const QString& pinName) const;

    /**
     * @brief Helper to set output pin value safely
     * @param pinName Output pin name
     * @param value Value to set
     * @return true if successful
     */
    bool setOutputValue(const QString& pinName, const QVariant& value);

    /**
     * @brief Helper to emit execution error signal
     * @param message Error message
     */
    void emitError(const QString& message);

    QString m_name;                                           ///< Component type name
    QString m_category;                                       ///< Component category
    QString m_id;                                             ///< Unique instance ID
    QString m_displayName;                                    ///< User-facing display name
    bool m_hasExecuted;                                       ///< Execution flag

    std::vector<std::shared_ptr<InputPin>> m_inputPins;       ///< Input pins
    std::vector<std::shared_ptr<OutputPin>> m_outputPins;     ///< Output pins
    std::vector<std::shared_ptr<Parameter>> m_parameters;     ///< Parameters
};

/**
 * @brief Template implementation for type-safe parameter access
 */
template<typename T>
std::shared_ptr<T> Component::getParameter(const QString& name) const {
    auto param = getParameter(name);
    return std::dynamic_pointer_cast<T>(param);
}

} // namespace Core
} // namespace VSE

#endif // VSE_CORE_COMPONENT_H

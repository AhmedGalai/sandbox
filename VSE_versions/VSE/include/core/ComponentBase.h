#ifndef VSE_COMPONENT_BASE_H
#define VSE_COMPONENT_BASE_H

#include "core/Pin.h"
#include "core/Parameter.h"
#include <QObject>
#include <QString>
#include <QColor>
#include <memory>
#include <vector>
#include <map>
#include <nlohmann/json.hpp>

namespace VSE {

/**
 * @brief Component execution state
 */
enum class ComponentState {
    Idle,       ///< Component is idle
    Running,    ///< Component is executing
    Error,      ///< Component encountered an error
    Disabled    ///< Component is disabled
};

/**
 * @brief Abstract base class for all visual scripting components
 *
 * Provides the foundation for all components in the VSE system.
 * Components have pins for data flow, parameters for configuration,
 * and metadata for visualization and organization.
 */
class ComponentBase : public QObject {
    Q_OBJECT

public:
    /**
     * @brief Construct a new Component Base object
     * @param parent Parent QObject
     */
    explicit ComponentBase(QObject* parent = nullptr);

    virtual ~ComponentBase() = default;

    /**
     * @brief Get the unique component ID
     * @return const QString& Component ID
     */
    const QString& getId() const { return m_id; }

    /**
     * @brief Set the component ID (typically only used during deserialization)
     * @param id Unique ID
     */
    void setId(const QString& id) { m_id = id; }

    /**
     * @brief Get the component name
     * @return QString Component name
     */
    virtual QString getName() const = 0;

    /**
     * @brief Get the component category
     * @return QString Category (e.g., "Logic", "Math", "I/O")
     */
    virtual QString getCategory() const = 0;

    /**
     * @brief Get the component color for visual representation
     * @return QColor Component color
     */
    virtual QColor getColor() const = 0;

    /**
     * @brief Get the component description
     * @return QString Description
     */
    virtual QString getDescription() const { return ""; }

    /**
     * @brief Execute the component logic
     *
     * This method is called when the component should process its inputs
     * and produce outputs. Implementations should be non-blocking.
     */
    virtual void execute() = 0;

    /**
     * @brief Get the current component state
     * @return ComponentState Current state
     */
    ComponentState getState() const { return m_state; }

    /**
     * @brief Set the component state
     * @param state New state
     */
    void setState(ComponentState state);

    // Pin Management
    /**
     * @brief Get all input pins
     * @return const std::vector<std::shared_ptr<InputPin>>& Input pins
     */
    const std::vector<std::shared_ptr<InputPin>>& getInputPins() const {
        return m_inputPins;
    }

    /**
     * @brief Get all output pins
     * @return const std::vector<std::shared_ptr<OutputPin>>& Output pins
     */
    const std::vector<std::shared_ptr<OutputPin>>& getOutputPins() const {
        return m_outputPins;
    }

    /**
     * @brief Get an input pin by name
     * @param name Pin name
     * @return std::shared_ptr<InputPin> Input pin (or nullptr if not found)
     */
    std::shared_ptr<InputPin> getInputPin(const QString& name) const;

    /**
     * @brief Get an output pin by name
     * @param name Pin name
     * @return std::shared_ptr<OutputPin> Output pin (or nullptr if not found)
     */
    std::shared_ptr<OutputPin> getOutputPin(const QString& name) const;

    // Parameter Management
    /**
     * @brief Get all parameters
     * @return const std::vector<std::shared_ptr<Parameter>>& Parameters
     */
    const std::vector<std::shared_ptr<Parameter>>& getParameters() const {
        return m_parameters;
    }

    /**
     * @brief Get a parameter by name
     * @param name Parameter name
     * @return std::shared_ptr<Parameter> Parameter (or nullptr if not found)
     */
    std::shared_ptr<Parameter> getParameter(const QString& name) const;

    /**
     * @brief Serialize component to JSON
     * @return nlohmann::json JSON representation
     */
    virtual nlohmann::json serialize() const;

    /**
     * @brief Deserialize component from JSON
     * @param json JSON data
     */
    virtual void deserialize(const nlohmann::json& json);

signals:
    /**
     * @brief Emitted when component state changes
     * @param state New state
     */
    void stateChanged(ComponentState state);

    /**
     * @brief Emitted when an error occurs
     * @param message Error message
     */
    void errorOccurred(const QString& message);

    /**
     * @brief Emitted when execution completes
     */
    void executionCompleted();

protected:
    /**
     * @brief Add an input pin to the component
     * @param name Pin name
     * @param dataType Data type
     * @return std::shared_ptr<InputPin> Created input pin
     */
    std::shared_ptr<InputPin> addInputPin(const QString& name, DataType dataType);

    /**
     * @brief Add an output pin to the component
     * @param name Pin name
     * @param dataType Data type
     * @return std::shared_ptr<OutputPin> Created output pin
     */
    std::shared_ptr<OutputPin> addOutputPin(const QString& name, DataType dataType);

    /**
     * @brief Add a parameter to the component
     * @param parameter Parameter to add
     */
    void addParameter(std::shared_ptr<Parameter> parameter);

    /**
     * @brief Report an error
     * @param message Error message
     */
    void reportError(const QString& message);

    /**
     * @brief Initialize the component (called during construction in derived classes)
     *
     * Derived classes should override this to create their pins and parameters.
     */
    virtual void initialize() {}

private:
    QString m_id;                                          ///< Unique component ID
    ComponentState m_state;                                ///< Current state
    std::vector<std::shared_ptr<InputPin>> m_inputPins;    ///< Input pins
    std::vector<std::shared_ptr<OutputPin>> m_outputPins;  ///< Output pins
    std::vector<std::shared_ptr<Parameter>> m_parameters;  ///< Parameters
};

} // namespace VSE

#endif // VSE_COMPONENT_BASE_H

#ifndef VSE_PROCESSOR_COMPONENT_H
#define VSE_PROCESSOR_COMPONENT_H

#include "core/ComponentBase.h"

namespace VSE {

/**
 * @brief Base class for processor components
 *
 * Processor components transform data from input pins to output pins.
 * They typically have one or more input pins and one or more output pins.
 * Processors are the workhorses of the visual scripting system, performing
 * operations like math, logic, data transformation, etc.
 */
class ProcessorComponent : public ComponentBase {
    Q_OBJECT

public:
    /**
     * @brief Construct a new Processor Component object
     * @param parent Parent QObject
     */
    explicit ProcessorComponent(QObject* parent = nullptr);

    virtual ~ProcessorComponent() = default;

    /**
     * @brief Get the component category
     * @return QString Returns category (typically overridden by derived classes)
     */
    QString getCategory() const override { return "Processor"; }

    /**
     * @brief Get the component color
     * @return QColor Orange color for processors
     */
    QColor getColor() const override { return QColor(255, 152, 0); }

    /**
     * @brief Execute the component (processes inputs and produces outputs)
     */
    void execute() override;

    /**
     * @brief Enable or disable automatic execution on input change
     * @param enabled True to enable auto-execution
     */
    void setAutoExecute(bool enabled) { m_autoExecute = enabled; }

    /**
     * @brief Check if auto-execution is enabled
     * @return bool True if enabled
     */
    bool isAutoExecute() const { return m_autoExecute; }

    /**
     * @brief Enable or disable pass-through mode
     *
     * In pass-through mode, the component forwards input data to outputs
     * without processing when disabled or in error state.
     *
     * @param enabled True to enable pass-through
     */
    void setPassThrough(bool enabled) { m_passThrough = enabled; }

    /**
     * @brief Check if pass-through is enabled
     * @return bool True if enabled
     */
    bool isPassThrough() const { return m_passThrough; }

    nlohmann::json serialize() const override;
    void deserialize(const nlohmann::json& json) override;

protected:
    /**
     * @brief Process inputs and generate outputs
     *
     * Derived classes must implement this to perform their specific
     * data transformation logic. Read from input pins using getInputPin()
     * and write to output pins using getOutputPin().
     */
    virtual void process() = 0;

    /**
     * @brief Called during initialization to set up input callbacks
     */
    void initialize() override;

    /**
     * @brief Check if all required inputs have valid data
     * @return bool True if all inputs are valid
     */
    virtual bool validateInputs() const;

private slots:
    /**
     * @brief Callback for input data changes
     * @param data New data value
     */
    void onInputDataChanged(const QVariant& data);

private:
    bool m_autoExecute;  ///< Whether to execute automatically on input change
    bool m_passThrough;  ///< Whether to pass through data when disabled
};

} // namespace VSE

#endif // VSE_PROCESSOR_COMPONENT_H

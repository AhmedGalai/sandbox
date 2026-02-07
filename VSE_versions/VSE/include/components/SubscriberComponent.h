#ifndef VSE_SUBSCRIBER_COMPONENT_H
#define VSE_SUBSCRIBER_COMPONENT_H

#include "core/ComponentBase.h"

namespace VSE {

/**
 * @brief Base class for subscriber components
 *
 * Subscriber components receive data from input pins and process it.
 * They typically have one or more input pins and no output pins.
 * Subscribers react to incoming data and perform actions based on it.
 */
class SubscriberComponent : public ComponentBase {
    Q_OBJECT

public:
    /**
     * @brief Construct a new Subscriber Component object
     * @param parent Parent QObject
     */
    explicit SubscriberComponent(QObject* parent = nullptr);

    virtual ~SubscriberComponent() = default;

    /**
     * @brief Get the component category
     * @return QString Always returns "Subscriber"
     */
    QString getCategory() const override { return "Subscriber"; }

    /**
     * @brief Get the component color
     * @return QColor Blue color for subscribers
     */
    QColor getColor() const override { return QColor(33, 150, 243); }

    /**
     * @brief Execute the component (processes input data)
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

    nlohmann::json serialize() const override;
    void deserialize(const nlohmann::json& json) override;

protected:
    /**
     * @brief Process incoming data
     *
     * Derived classes must implement this to handle received data.
     * This method is called when data arrives on any input pin.
     */
    virtual void processInputs() = 0;

    /**
     * @brief Called during initialization to set up input callbacks
     */
    void initialize() override;

private slots:
    /**
     * @brief Callback for input data changes
     * @param data New data value
     */
    void onInputDataChanged(const QVariant& data);

private:
    bool m_autoExecute; ///< Whether to execute automatically on input change
};

} // namespace VSE

#endif // VSE_SUBSCRIBER_COMPONENT_H

#ifndef VSE_PUBLISHER_COMPONENT_H
#define VSE_PUBLISHER_COMPONENT_H

#include "core/ComponentBase.h"
#include <QTimer>

namespace VSE {

/**
 * @brief Base class for publisher components
 *
 * Publisher components generate data and publish it to output pins.
 * They typically have no input pins and one or more output pins.
 * Publishers can operate periodically (timer-based) or on-demand (event-driven).
 */
class PublisherComponent : public ComponentBase {
    Q_OBJECT

public:
    /**
     * @brief Construct a new Publisher Component object
     * @param parent Parent QObject
     */
    explicit PublisherComponent(QObject* parent = nullptr);

    virtual ~PublisherComponent() = default;

    /**
     * @brief Get the component category
     * @return QString Always returns "Publisher"
     */
    QString getCategory() const override { return "Publisher"; }

    /**
     * @brief Get the component color
     * @return QColor Green color for publishers
     */
    QColor getColor() const override { return QColor(76, 175, 80); }

    /**
     * @brief Enable or disable periodic publishing
     * @param enabled True to enable periodic publishing
     */
    void setPeriodicPublishing(bool enabled);

    /**
     * @brief Check if periodic publishing is enabled
     * @return bool True if enabled
     */
    bool isPeriodicPublishing() const { return m_periodicPublishing; }

    /**
     * @brief Set the publishing interval (in milliseconds)
     * @param intervalMs Interval in milliseconds
     */
    void setPublishInterval(int intervalMs);

    /**
     * @brief Get the publishing interval
     * @return int Interval in milliseconds
     */
    int getPublishInterval() const { return m_publishInterval; }

    /**
     * @brief Start the publisher
     */
    virtual void start();

    /**
     * @brief Stop the publisher
     */
    virtual void stop();

    /**
     * @brief Check if the publisher is running
     * @return bool True if running
     */
    bool isRunning() const { return m_running; }

    /**
     * @brief Execute the component (triggers publishing)
     */
    void execute() override;

    nlohmann::json serialize() const override;
    void deserialize(const nlohmann::json& json) override;

protected:
    /**
     * @brief Publish data to outputs
     *
     * Derived classes must implement this to generate and publish data.
     */
    virtual void publish() = 0;

private slots:
    /**
     * @brief Timer callback for periodic publishing
     */
    void onTimerTimeout();

private:
    bool m_periodicPublishing;  ///< Whether periodic publishing is enabled
    int m_publishInterval;      ///< Publishing interval in milliseconds
    bool m_running;             ///< Whether the publisher is running
    QTimer* m_timer;            ///< Timer for periodic publishing
};

} // namespace VSE

#endif // VSE_PUBLISHER_COMPONENT_H

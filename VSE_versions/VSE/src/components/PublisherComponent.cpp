#include "components/PublisherComponent.h"

namespace VSE {

// ============================================================================
// PublisherComponent
// ============================================================================

PublisherComponent::PublisherComponent(QObject* parent)
    : ComponentBase(parent),
      m_periodicPublishing(false),
      m_publishInterval(1000),
      m_running(false),
      m_timer(new QTimer(this)) {

    // Connect timer to publishing callback
    connect(m_timer, &QTimer::timeout, this, &PublisherComponent::onTimerTimeout);
}

void PublisherComponent::setPeriodicPublishing(bool enabled) {
    m_periodicPublishing = enabled;

    // Update timer state if running
    if (m_running) {
        if (m_periodicPublishing) {
            m_timer->start(m_publishInterval);
        } else {
            m_timer->stop();
        }
    }
}

void PublisherComponent::setPublishInterval(int intervalMs) {
    m_publishInterval = std::max(1, intervalMs); // Minimum 1ms

    // Update timer interval if running
    if (m_running && m_periodicPublishing && m_timer->isActive()) {
        m_timer->setInterval(m_publishInterval);
    }
}

void PublisherComponent::start() {
    if (m_running) {
        return; // Already running
    }

    m_running = true;
    setState(ComponentState::Running);

    // Start periodic timer if enabled
    if (m_periodicPublishing) {
        m_timer->start(m_publishInterval);
    }

    // Publish initial data
    publish();
}

void PublisherComponent::stop() {
    if (!m_running) {
        return; // Already stopped
    }

    m_running = false;
    setState(ComponentState::Idle);

    // Stop timer
    if (m_timer->isActive()) {
        m_timer->stop();
    }
}

void PublisherComponent::execute() {
    if (!m_running) {
        start();
    } else {
        // Manual trigger - publish immediately
        publish();
    }
}

void PublisherComponent::onTimerTimeout() {
    if (m_running) {
        publish();
    }
}

nlohmann::json PublisherComponent::serialize() const {
    nlohmann::json j = ComponentBase::serialize();

    j["periodicPublishing"] = m_periodicPublishing;
    j["publishInterval"] = m_publishInterval;
    j["running"] = m_running;

    return j;
}

void PublisherComponent::deserialize(const nlohmann::json& json) {
    ComponentBase::deserialize(json);

    if (json.contains("periodicPublishing") && json["periodicPublishing"].is_boolean()) {
        m_periodicPublishing = json["periodicPublishing"].get<bool>();
    }

    if (json.contains("publishInterval") && json["publishInterval"].is_number_integer()) {
        m_publishInterval = json["publishInterval"].get<int>();
    }

    // Note: We don't automatically restore the running state
    // Components should be explicitly started after deserialization
}

} // namespace VSE

#include "components/SubscriberComponent.h"

namespace VSE {

// ============================================================================
// SubscriberComponent
// ============================================================================

SubscriberComponent::SubscriberComponent(QObject* parent)
    : ComponentBase(parent),
      m_autoExecute(true) {
}

void SubscriberComponent::execute() {
    setState(ComponentState::Running);

    try {
        processInputs();
        emit executionCompleted();
        setState(ComponentState::Idle);
    } catch (const std::exception& e) {
        reportError(QString("Execution error: %1").arg(e.what()));
    } catch (...) {
        reportError("Unknown execution error");
    }
}

void SubscriberComponent::initialize() {
    ComponentBase::initialize();

    // Set up callbacks for all input pins
    for (auto& inputPin : getInputPins()) {
        if (inputPin) {
            inputPin->setDataCallback([this](const QVariant& data) {
                this->onInputDataChanged(data);
            });
        }
    }
}

void SubscriberComponent::onInputDataChanged(const QVariant& data) {
    Q_UNUSED(data);

    // Automatically execute when input changes (if enabled)
    if (m_autoExecute && getState() != ComponentState::Disabled) {
        execute();
    }
}

nlohmann::json SubscriberComponent::serialize() const {
    nlohmann::json j = ComponentBase::serialize();
    j["autoExecute"] = m_autoExecute;
    return j;
}

void SubscriberComponent::deserialize(const nlohmann::json& json) {
    ComponentBase::deserialize(json);

    if (json.contains("autoExecute") && json["autoExecute"].is_boolean()) {
        m_autoExecute = json["autoExecute"].get<bool>();
    }
}

} // namespace VSE

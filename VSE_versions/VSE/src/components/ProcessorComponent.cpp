#include "components/ProcessorComponent.h"

namespace VSE {

// ============================================================================
// ProcessorComponent
// ============================================================================

ProcessorComponent::ProcessorComponent(QObject* parent)
    : ComponentBase(parent),
      m_autoExecute(true),
      m_passThrough(false) {
}

void ProcessorComponent::execute() {
    // Check if component is disabled
    if (getState() == ComponentState::Disabled) {
        if (m_passThrough) {
            // In pass-through mode, forward first input to first output
            const auto& inputs = getInputPins();
            const auto& outputs = getOutputPins();
            if (!inputs.empty() && !outputs.empty() && inputs[0] && outputs[0]) {
                outputs[0]->transmitData(inputs[0]->getData());
            }
        }
        return;
    }

    // Validate inputs before processing
    if (!validateInputs()) {
        reportError("Invalid or missing input data");
        return;
    }

    setState(ComponentState::Running);

    try {
        process();
        emit executionCompleted();
        setState(ComponentState::Idle);
    } catch (const std::exception& e) {
        reportError(QString("Processing error: %1").arg(e.what()));
    } catch (...) {
        reportError("Unknown processing error");
    }
}

void ProcessorComponent::initialize() {
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

bool ProcessorComponent::validateInputs() const {
    // Default implementation: check that all inputs have data
    for (const auto& inputPin : getInputPins()) {
        if (inputPin && inputPin->isConnected() && !inputPin->getData().isValid()) {
            return false;
        }
    }
    return true;
}

void ProcessorComponent::onInputDataChanged(const QVariant& data) {
    Q_UNUSED(data);

    // Automatically execute when input changes (if enabled)
    if (m_autoExecute && getState() != ComponentState::Disabled) {
        execute();
    }
}

nlohmann::json ProcessorComponent::serialize() const {
    nlohmann::json j = ComponentBase::serialize();
    j["autoExecute"] = m_autoExecute;
    j["passThrough"] = m_passThrough;
    return j;
}

void ProcessorComponent::deserialize(const nlohmann::json& json) {
    ComponentBase::deserialize(json);

    if (json.contains("autoExecute") && json["autoExecute"].is_boolean()) {
        m_autoExecute = json["autoExecute"].get<bool>();
    }

    if (json.contains("passThrough") && json["passThrough"].is_boolean()) {
        m_passThrough = json["passThrough"].get<bool>();
    }
}

} // namespace VSE

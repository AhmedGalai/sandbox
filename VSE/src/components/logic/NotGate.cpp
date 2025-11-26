/**
 * @file NotGate.cpp
 * @brief Implementation of NotGate component
 */

#include "components/logic/NotGate.h"
#include "registry/ComponentRegistry.h"

namespace VSE {
namespace Components {
namespace Logic {

// Register component with registry
namespace {
    static ComponentRegistrar<NotGate> registrar(
        "NotGate",
        "NOT Gate",
        "Logic",
        "Logical NOT operation (inverter). Outputs the inverse of the input value."
    );
}

NotGate::NotGate(const nlohmann::json& params)
    : ProcessorComponent("NotGate", "Logic")
{
    // Create input pin
    addInputPin("Input", DataType::Boolean);

    // Create output pin
    addOutputPin("Output", DataType::Boolean);

    // Deserialize if params provided
    if (!params.empty()) {
        deserialize(params);
    }
}

void NotGate::execute(Core::ExecutionContext* context) {
    // Get input value
    QVariant input = getInputValue("Input");

    // Check if input is valid
    if (!input.isValid()) {
        emitError("NotGate: Missing or invalid input value");
        return;
    }

    // Perform NOT operation
    bool value = input.toBool();
    bool result = !value;

    // Set output
    setOutputValue("Output", result);

    // Mark as executed
    m_hasExecuted = true;
}

nlohmann::json NotGate::serialize() const {
    return ProcessorComponent::serialize();
}

bool NotGate::deserialize(const nlohmann::json& json) {
    return ProcessorComponent::deserialize(json);
}

} // namespace Logic
} // namespace Components
} // namespace VSE

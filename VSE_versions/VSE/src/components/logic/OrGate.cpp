/**
 * @file OrGate.cpp
 * @brief Implementation of OrGate component
 */

#include "components/logic/OrGate.h"
#include "registry/ComponentRegistry.h"

namespace VSE {
namespace Components {
namespace Logic {

// Register component with registry
namespace {
    static ComponentRegistrar<OrGate> registrar(
        "OrGate",
        "OR Gate",
        "Logic",
        "Logical OR operation on two boolean inputs. Outputs true when at least one input is true."
    );
}

OrGate::OrGate(const nlohmann::json& params)
    : ProcessorComponent("OrGate", "Logic")
{
    // Create input pins
    addInputPin("A", DataType::Boolean);
    addInputPin("B", DataType::Boolean);

    // Create output pin
    addOutputPin("Output", DataType::Boolean);

    // Deserialize if params provided
    if (!params.empty()) {
        deserialize(params);
    }
}

void OrGate::execute() {
    // Get input values
    QVariant inputA = getInputValue("A");
    QVariant inputB = getInputValue("B");

    // Check if inputs are valid
    if (!inputA.isValid() || !inputB.isValid()) {
        emitError("OrGate: Missing or invalid input values");
        return;
    }

    // Perform OR operation
    bool a = inputA.toBool();
    bool b = inputB.toBool();
    bool result = a || b;

    // Set output
    setOutputValue("Output", result);

    // Mark as executed
    m_hasExecuted = true;
}

nlohmann::json OrGate::serialize() const {
    return ProcessorComponent::serialize();
}

void OrGate::deserialize(const nlohmann::jsonbool OrGate::deserialize(const nlohmann::json& json) json) {
    return ProcessorComponent::deserialize(json);
}

} // namespace Logic
} // namespace Components
} // namespace VSE

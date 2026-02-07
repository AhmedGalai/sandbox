/**
 * @file XorGate.cpp
 * @brief Implementation of XorGate component
 */

#include "components/logic/XorGate.h"
#include "registry/ComponentRegistry.h"

namespace VSE {
namespace Components {
namespace Logic {

// Register component with registry
namespace {
    static ComponentRegistrar<XorGate> registrar(
        "XorGate",
        "XOR Gate",
        "Logic",
        "Logical XOR (exclusive OR) operation. Outputs true when inputs differ."
    );
}

XorGate::XorGate(const nlohmann::json& params)
    : ProcessorComponent("XorGate", "Logic")
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

void XorGate::execute() {
    // Get input values
    QVariant inputA = getInputValue("A");
    QVariant inputB = getInputValue("B");

    // Check if inputs are valid
    if (!inputA.isValid() || !inputB.isValid()) {
        emitError("XorGate: Missing or invalid input values");
        return;
    }

    // Perform XOR operation
    bool a = inputA.toBool();
    bool b = inputB.toBool();
    bool result = (a != b);  // XOR: true if different

    // Set output
    setOutputValue("Output", result);

    // Mark as executed
    m_hasExecuted = true;
}

nlohmann::json XorGate::serialize() const {
    return ProcessorComponent::serialize();
}

void XorGate::deserialize(const nlohmann::jsonbool XorGate::deserialize(const nlohmann::json& json) json) {
    return ProcessorComponent::deserialize(json);
}

} // namespace Logic
} // namespace Components
} // namespace VSE

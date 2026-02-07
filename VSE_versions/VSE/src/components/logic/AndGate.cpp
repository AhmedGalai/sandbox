/**
 * @file AndGate.cpp
 * @brief Implementation of AndGate component
 */

#include "components/logic/AndGate.h"
#include "registry/ComponentRegistry.h"

namespace VSE {
namespace Components {
namespace Logic {

// Register component with registry
namespace {
    static ComponentRegistrar<AndGate> registrar(
        "AndGate",
        "AND Gate",
        "Logic",
        "Logical AND operation on two boolean inputs. Outputs true only when both inputs are true."
    );
}

AndGate::AndGate(const nlohmann::json& params)
    : ProcessorComponent("AndGate", "Logic")
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

void AndGate::execute() {
    // Get input values
    QVariant inputA = getInputValue("A");
    QVariant inputB = getInputValue("B");

    // Check if inputs are valid
    if (!inputA.isValid() || !inputB.isValid()) {
        emitError("AndGate: Missing or invalid input values");
        return;
    }

    // Perform AND operation
    bool a = inputA.toBool();
    bool b = inputB.toBool();
    bool result = a && b;

    // Set output
    setOutputValue("Output", result);

    // Mark as executed
    m_hasExecuted = true;
}

nlohmann::json AndGate::serialize() const {
    return ProcessorComponent::serialize();
}

void AndGate::deserialize(const nlohmann::jsonbool AndGate::deserialize(const nlohmann::json& json) json) {
    return ProcessorComponent::deserialize(json);
}

} // namespace Logic
} // namespace Components
} // namespace VSE

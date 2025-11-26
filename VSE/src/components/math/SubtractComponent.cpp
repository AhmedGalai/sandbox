/**
 * @file SubtractComponent.cpp
 * @brief Implementation of SubtractComponent
 */

#include "components/math/SubtractComponent.h"
#include "registry/ComponentRegistry.h"

namespace VSE {
namespace Components {
namespace Math {

// Register component with registry
namespace {
    static ComponentRegistrar<SubtractComponent> registrar(
        "SubtractComponent",
        "Subtract",
        "Math",
        "Subtracts two numeric inputs. Result = A - B"
    );
}

SubtractComponent::SubtractComponent(const nlohmann::json& params)
    : ProcessorComponent("SubtractComponent", "Math")
{
    // Create input pins
    addInputPin("A", DataType::Float);
    addInputPin("B", DataType::Float);

    // Create output pin
    addOutputPin("Result", DataType::Float);

    // Deserialize if params provided
    if (!params.empty()) {
        deserialize(params);
    }
}

void SubtractComponent::execute(Core::ExecutionContext* context) {
    // Get input values
    QVariant inputA = getInputValue("A");
    QVariant inputB = getInputValue("B");

    // Check if inputs are valid
    if (!inputA.isValid() || !inputB.isValid()) {
        emitError("SubtractComponent: Missing or invalid input values");
        return;
    }

    // Convert to double for arithmetic
    bool okA = false, okB = false;
    double a = inputA.toDouble(&okA);
    double b = inputB.toDouble(&okB);

    if (!okA || !okB) {
        emitError("SubtractComponent: Could not convert inputs to numeric values");
        return;
    }

    // Perform subtraction
    double result = a - b;

    // Set output
    setOutputValue("Result", result);

    // Mark as executed
    m_hasExecuted = true;
}

nlohmann::json SubtractComponent::serialize() const {
    return ProcessorComponent::serialize();
}

bool SubtractComponent::deserialize(const nlohmann::json& json) {
    return ProcessorComponent::deserialize(json);
}

} // namespace Math
} // namespace Components
} // namespace VSE

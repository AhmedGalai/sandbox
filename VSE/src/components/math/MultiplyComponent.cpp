/**
 * @file MultiplyComponent.cpp
 * @brief Implementation of MultiplyComponent
 */

#include "components/math/MultiplyComponent.h"
#include "registry/ComponentRegistry.h"

namespace VSE {
namespace Components {
namespace Math {

// Register component with registry
namespace {
    static ComponentRegistrar<MultiplyComponent> registrar(
        "MultiplyComponent",
        "Multiply",
        "Math",
        "Multiplies two numeric inputs. Result = A * B"
    );
}

MultiplyComponent::MultiplyComponent(const nlohmann::json& params)
    : ProcessorComponent("MultiplyComponent", "Math")
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

void MultiplyComponent::execute() {
    // Get input values
    QVariant inputA = getInputValue("A");
    QVariant inputB = getInputValue("B");

    // Check if inputs are valid
    if (!inputA.isValid() || !inputB.isValid()) {
        emitError("MultiplyComponent: Missing or invalid input values");
        return;
    }

    // Convert to double for arithmetic
    bool okA = false, okB = false;
    double a = inputA.toDouble(&okA);
    double b = inputB.toDouble(&okB);

    if (!okA || !okB) {
        emitError("MultiplyComponent: Could not convert inputs to numeric values");
        return;
    }

    // Perform multiplication
    double result = a * b;

    // Set output
    setOutputValue("Result", result);

    // Mark as executed
    m_hasExecuted = true;
}

nlohmann::json MultiplyComponent::serialize() const {
    return ProcessorComponent::serialize();
}

void MultiplyComponent::deserialize(const nlohmann::jsonbool MultiplyComponent::deserialize(const nlohmann::json& json) json) {
    return ProcessorComponent::deserialize(json);
}

} // namespace Math
} // namespace Components
} // namespace VSE

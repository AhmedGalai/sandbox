/**
 * @file AddComponent.cpp
 * @brief Implementation of AddComponent
 */

#include "components/math/AddComponent.h"
#include "registry/ComponentRegistry.h"

namespace VSE {
namespace Components {
namespace Math {

// Register component with registry
namespace {
    static ComponentRegistrar<AddComponent> registrar(
        "AddComponent",
        "Add",
        "Math",
        "Adds two numeric inputs. Result = A + B"
    );
}

AddComponent::AddComponent(const nlohmann::json& params)
    : ProcessorComponent("AddComponent", "Math")
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

void AddComponent::execute(Core::ExecutionContext* context) {
    // Get input values
    QVariant inputA = getInputValue("A");
    QVariant inputB = getInputValue("B");

    // Check if inputs are valid
    if (!inputA.isValid() || !inputB.isValid()) {
        emitError("AddComponent: Missing or invalid input values");
        return;
    }

    // Convert to double for arithmetic (handles int and float)
    bool okA = false, okB = false;
    double a = inputA.toDouble(&okA);
    double b = inputB.toDouble(&okB);

    if (!okA || !okB) {
        emitError("AddComponent: Could not convert inputs to numeric values");
        return;
    }

    // Perform addition
    double result = a + b;

    // Set output
    setOutputValue("Result", result);

    // Mark as executed
    m_hasExecuted = true;
}

nlohmann::json AddComponent::serialize() const {
    return ProcessorComponent::serialize();
}

bool AddComponent::deserialize(const nlohmann::json& json) {
    return ProcessorComponent::deserialize(json);
}

} // namespace Math
} // namespace Components
} // namespace VSE

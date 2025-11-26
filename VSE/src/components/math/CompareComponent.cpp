/**
 * @file CompareComponent.cpp
 * @brief Implementation of CompareComponent
 */

#include "components/math/CompareComponent.h"
#include "registry/ComponentRegistry.h"
#include <cmath>

namespace VSE {
namespace Components {
namespace Math {

// Register component with registry
namespace {
    static ComponentRegistrar<CompareComponent> registrar(
        "CompareComponent",
        "Compare",
        "Math",
        "Compares two numeric inputs. Supports GT, LT, EQ, GE, LE, NE operations."
    );
}

CompareComponent::CompareComponent(const nlohmann::json& params)
    : ProcessorComponent("CompareComponent", "Math")
{
    // Create input pins
    addInputPin("A", DataType::Float);
    addInputPin("B", DataType::Float);

    // Create output pin
    addOutputPin("Result", DataType::Boolean);

    // Add parameters
    auto modeParam = std::make_shared<IntParameter>("Mode", 0, 0, 5,
        "Comparison mode: 0=GT, 1=LT, 2=EQ, 3=GE, 4=LE, 5=NE");
    addParameter(modeParam);

    auto epsilonParam = std::make_shared<FloatParameter>("Epsilon", 1e-6f, 0.0f, 1.0f,
        "Tolerance for floating-point equality comparison");
    addParameter(epsilonParam);

    // Deserialize if params provided
    if (!params.empty()) {
        deserialize(params);
    }
}

void CompareComponent::execute(Core::ExecutionContext* context) {
    // Get input values
    QVariant inputA = getInputValue("A");
    QVariant inputB = getInputValue("B");

    // Check if inputs are valid
    if (!inputA.isValid() || !inputB.isValid()) {
        emitError("CompareComponent: Missing or invalid input values");
        return;
    }

    // Convert to double for comparison
    bool okA = false, okB = false;
    double a = inputA.toDouble(&okA);
    double b = inputB.toDouble(&okB);

    if (!okA || !okB) {
        emitError("CompareComponent: Could not convert inputs to numeric values");
        return;
    }

    // Get parameters
    CompareMode mode = getMode();
    double epsilon = getEpsilon();

    // Perform comparison
    bool result = performComparison(a, b, mode, epsilon);

    // Set output
    setOutputValue("Result", result);

    // Mark as executed
    m_hasExecuted = true;
}

CompareMode CompareComponent::getMode() const {
    auto modeParam = getParameter<IntParameter>("Mode");
    if (modeParam) {
        int modeValue = modeParam->getIntValue();
        return static_cast<CompareMode>(std::clamp(modeValue, 0, 5));
    }
    return CompareMode::GreaterThan;
}

void CompareComponent::setMode(CompareMode mode) {
    auto modeParam = getParameter<IntParameter>("Mode");
    if (modeParam) {
        modeParam->setIntValue(static_cast<int>(mode));
    }
}

double CompareComponent::getEpsilon() const {
    auto epsilonParam = getParameter<FloatParameter>("Epsilon");
    if (epsilonParam) {
        return epsilonParam->getFloatValue();
    }
    return 1e-6;
}

void CompareComponent::setEpsilon(double epsilon) {
    auto epsilonParam = getParameter<FloatParameter>("Epsilon");
    if (epsilonParam) {
        epsilonParam->setFloatValue(static_cast<float>(epsilon));
    }
}

bool CompareComponent::performComparison(double a, double b, CompareMode mode, double epsilon) const {
    switch (mode) {
        case CompareMode::GreaterThan:
            return a > b;

        case CompareMode::LessThan:
            return a < b;

        case CompareMode::Equal:
            return std::abs(a - b) <= epsilon;

        case CompareMode::GreaterOrEqual:
            return a >= b || std::abs(a - b) <= epsilon;

        case CompareMode::LessOrEqual:
            return a <= b || std::abs(a - b) <= epsilon;

        case CompareMode::NotEqual:
            return std::abs(a - b) > epsilon;

        default:
            return false;
    }
}

nlohmann::json CompareComponent::serialize() const {
    return ProcessorComponent::serialize();
}

bool CompareComponent::deserialize(const nlohmann::json& json) {
    return ProcessorComponent::deserialize(json);
}

} // namespace Math
} // namespace Components
} // namespace VSE

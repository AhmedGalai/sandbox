/**
 * @file SubtractComponent.h
 * @brief Subtraction math operation component
 */

#ifndef VSE_COMPONENTS_MATH_SUBTRACTCOMPONENT_H
#define VSE_COMPONENTS_MATH_SUBTRACTCOMPONENT_H

#include "core/ProcessorComponent.h"

namespace VSE {
namespace Components {
namespace Math {

/**
 * @class SubtractComponent
 * @brief Performs subtraction on two numeric inputs
 *
 * Subtracts the second input from the first and outputs the result.
 * Supports both integer and floating-point arithmetic.
 *
 * Inputs:
 * - A (Number): Minuend (value to subtract from)
 * - B (Number): Subtrahend (value to subtract)
 *
 * Outputs:
 * - Result (Number): A - B
 */
class SubtractComponent : public Core::ProcessorComponent {
    Q_OBJECT

public:
    /**
     * @brief Construct a new SubtractComponent
     * @param params Construction parameters (unused)
     */
    explicit SubtractComponent(const nlohmann::json& params = {});

    /**
     * @brief Execute subtraction operation
     * @param context Execution context
     */
    void execute(Core::ExecutionContext* context) override;

    /**
     * @brief Serialize component state
     * @return nlohmann::json Serialized state
     */
    nlohmann::json serialize() const override;

    /**
     * @brief Deserialize component state
     * @param json Serialized state
     * @return true if successful
     */
    bool deserialize(const nlohmann::json& json) override;
};

} // namespace Math
} // namespace Components
} // namespace VSE

#endif // VSE_COMPONENTS_MATH_SUBTRACTCOMPONENT_H

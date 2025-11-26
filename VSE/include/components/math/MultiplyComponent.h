/**
 * @file MultiplyComponent.h
 * @brief Multiplication math operation component
 */

#ifndef VSE_COMPONENTS_MATH_MULTIPLYCOMPONENT_H
#define VSE_COMPONENTS_MATH_MULTIPLYCOMPONENT_H

#include "core/ProcessorComponent.h"

namespace VSE {
namespace Components {
namespace Math {

/**
 * @class MultiplyComponent
 * @brief Performs multiplication on two numeric inputs
 *
 * Multiplies two numbers and outputs the result. Supports both integer
 * and floating-point arithmetic.
 *
 * Inputs:
 * - A (Number): First factor
 * - B (Number): Second factor
 *
 * Outputs:
 * - Result (Number): A * B
 */
class MultiplyComponent : public Core::ProcessorComponent {
    Q_OBJECT

public:
    /**
     * @brief Construct a new MultiplyComponent
     * @param params Construction parameters (unused)
     */
    explicit MultiplyComponent(const nlohmann::json& params = {});

    /**
     * @brief Execute multiplication operation
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

#endif // VSE_COMPONENTS_MATH_MULTIPLYCOMPONENT_H

/**
 * @file AddComponent.h
 * @brief Addition math operation component
 */

#ifndef VSE_COMPONENTS_MATH_ADDCOMPONENT_H
#define VSE_COMPONENTS_MATH_ADDCOMPONENT_H

#include "core/ProcessorComponent.h"

namespace VSE {
namespace Components {
namespace Math {

/**
 * @class AddComponent
 * @brief Performs addition on two numeric inputs
 *
 * Adds two numbers and outputs the result. Supports both integer and
 * floating-point arithmetic.
 *
 * Inputs:
 * - A (Number): First operand
 * - B (Number): Second operand
 *
 * Outputs:
 * - Result (Number): A + B
 */
class AddComponent : public Core::ProcessorComponent {
    Q_OBJECT

public:
    /**
     * @brief Construct a new AddComponent
     * @param params Construction parameters (unused)
     */
    explicit AddComponent(const nlohmann::json& params = {});

    /**
     * @brief Execute addition operation
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

#endif // VSE_COMPONENTS_MATH_ADDCOMPONENT_H

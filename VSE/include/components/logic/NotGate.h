/**
 * @file NotGate.h
 * @brief Logical NOT gate component
 */

#ifndef VSE_COMPONENTS_LOGIC_NOTGATE_H
#define VSE_COMPONENTS_LOGIC_NOTGATE_H

#include "components/ProcessorComponent.h"

namespace VSE {
namespace Components {
namespace Logic {

/**
 * @class NotGate
 * @brief Performs logical NOT (inversion) operation on a boolean input
 *
 * Outputs the inverse of the input.
 *
 * Truth table:
 * ```
 * Input | Output
 * ------|-------
 *   0   |   1
 *   1   |   0
 * ```
 *
 * Inputs:
 * - Input (Boolean): Input value
 *
 * Outputs:
 * - Output (Boolean): NOT Input
 */
class NotGate : public VSE::ProcessorComponent {
    Q_OBJECT

public:
    /**
     * @brief Construct a new NotGate component
     * @param params Construction parameters (unused)
     */
    explicit NotGate(const nlohmann::json& params = {});

    /**
     * @brief Execute logical NOT operation
     * @param context Execution context
     */
    void execute() override;

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
    void deserialize(const nlohmann::json& json) override;
};

} // namespace Logic
} // namespace Components
} // namespace VSE

#endif // VSE_COMPONENTS_LOGIC_NOTGATE_H

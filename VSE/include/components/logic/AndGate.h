/**
 * @file AndGate.h
 * @brief Logical AND gate component
 */

#ifndef VSE_COMPONENTS_LOGIC_ANDGATE_H
#define VSE_COMPONENTS_LOGIC_ANDGATE_H

#include "components/ProcessorComponent.h"

namespace VSE {
namespace Components {
namespace Logic {

/**
 * @class AndGate
 * @brief Performs logical AND operation on two boolean inputs
 *
 * Outputs true only when both inputs are true.
 *
 * Truth table:
 * ```
 * A | B | Output
 * --|---|-------
 * 0 | 0 |   0
 * 0 | 1 |   0
 * 1 | 0 |   0
 * 1 | 1 |   1
 * ```
 *
 * Inputs:
 * - A (Boolean): First input
 * - B (Boolean): Second input
 *
 * Outputs:
 * - Output (Boolean): A AND B
 */
class AndGate : public VSE::ProcessorComponent {
    Q_OBJECT

public:
    /**
     * @brief Construct a new AndGate component
     * @param params Construction parameters (unused)
     */
    explicit AndGate(const nlohmann::json& params = {});

    /**
     * @brief Execute logical AND operation
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

#endif // VSE_COMPONENTS_LOGIC_ANDGATE_H

/**
 * @file XorGate.h
 * @brief Logical XOR gate component
 */

#ifndef VSE_COMPONENTS_LOGIC_XORGATE_H
#define VSE_COMPONENTS_LOGIC_XORGATE_H

#include "core/ProcessorComponent.h"

namespace VSE {
namespace Components {
namespace Logic {

/**
 * @class XorGate
 * @brief Performs logical XOR (exclusive OR) operation on two boolean inputs
 *
 * Outputs true when inputs differ.
 *
 * Truth table:
 * ```
 * A | B | Output
 * --|---|-------
 * 0 | 0 |   0
 * 0 | 1 |   1
 * 1 | 0 |   1
 * 1 | 1 |   0
 * ```
 *
 * Inputs:
 * - A (Boolean): First input
 * - B (Boolean): Second input
 *
 * Outputs:
 * - Output (Boolean): A XOR B
 */
class XorGate : public Core::ProcessorComponent {
    Q_OBJECT

public:
    /**
     * @brief Construct a new XorGate component
     * @param params Construction parameters (unused)
     */
    explicit XorGate(const nlohmann::json& params = {});

    /**
     * @brief Execute logical XOR operation
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

} // namespace Logic
} // namespace Components
} // namespace VSE

#endif // VSE_COMPONENTS_LOGIC_XORGATE_H

/**
 * @file OrGate.h
 * @brief Logical OR gate component
 */

#ifndef VSE_COMPONENTS_LOGIC_ORGATE_H
#define VSE_COMPONENTS_LOGIC_ORGATE_H

#include "core/ProcessorComponent.h"

namespace VSE {
namespace Components {
namespace Logic {

/**
 * @class OrGate
 * @brief Performs logical OR operation on two boolean inputs
 *
 * Outputs true when at least one input is true.
 *
 * Truth table:
 * ```
 * A | B | Output
 * --|---|-------
 * 0 | 0 |   0
 * 0 | 1 |   1
 * 1 | 0 |   1
 * 1 | 1 |   1
 * ```
 *
 * Inputs:
 * - A (Boolean): First input
 * - B (Boolean): Second input
 *
 * Outputs:
 * - Output (Boolean): A OR B
 */
class OrGate : public Core::ProcessorComponent {
    Q_OBJECT

public:
    /**
     * @brief Construct a new OrGate component
     * @param params Construction parameters (unused)
     */
    explicit OrGate(const nlohmann::json& params = {});

    /**
     * @brief Execute logical OR operation
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

#endif // VSE_COMPONENTS_LOGIC_ORGATE_H

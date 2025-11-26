/**
 * @file CompareComponent.h
 * @brief Numeric comparison component
 */

#ifndef VSE_COMPONENTS_MATH_COMPARECOMPONENT_H
#define VSE_COMPONENTS_MATH_COMPARECOMPONENT_H

#include "core/ProcessorComponent.h"
#include "core/Parameter.h"

namespace VSE {
namespace Components {
namespace Math {

/**
 * @enum CompareMode
 * @brief Comparison operation modes
 */
enum class CompareMode {
    GreaterThan,    ///< A > B
    LessThan,       ///< A < B
    Equal,          ///< A == B
    GreaterOrEqual, ///< A >= B
    LessOrEqual,    ///< A <= B
    NotEqual        ///< A != B
};

/**
 * @class CompareComponent
 * @brief Compares two numeric inputs and outputs boolean result
 *
 * Supports multiple comparison modes: GT, LT, EQ, GE, LE, NE
 *
 * Inputs:
 * - A (Number): First value
 * - B (Number): Second value
 *
 * Outputs:
 * - Result (Boolean): Comparison result
 *
 * Parameters:
 * - Mode (Int): Comparison mode (0=GT, 1=LT, 2=EQ, 3=GE, 4=LE, 5=NE)
 * - Epsilon (Float): Tolerance for floating-point equality (default: 1e-6)
 */
class CompareComponent : public Core::ProcessorComponent {
    Q_OBJECT

public:
    /**
     * @brief Construct a new CompareComponent
     * @param params Construction parameters
     */
    explicit CompareComponent(const nlohmann::json& params = {});

    /**
     * @brief Execute comparison operation
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

    /**
     * @brief Get current comparison mode
     * @return CompareMode Current mode
     */
    CompareMode getMode() const;

    /**
     * @brief Set comparison mode
     * @param mode New mode
     */
    void setMode(CompareMode mode);

    /**
     * @brief Get epsilon tolerance
     * @return double Epsilon value
     */
    double getEpsilon() const;

    /**
     * @brief Set epsilon tolerance
     * @param epsilon New epsilon value
     */
    void setEpsilon(double epsilon);

private:
    /**
     * @brief Perform the comparison
     * @param a First value
     * @param b Second value
     * @param mode Comparison mode
     * @param epsilon Tolerance for equality
     * @return bool Comparison result
     */
    bool performComparison(double a, double b, CompareMode mode, double epsilon) const;
};

} // namespace Math
} // namespace Components
} // namespace VSE

#endif // VSE_COMPONENTS_MATH_COMPARECOMPONENT_H

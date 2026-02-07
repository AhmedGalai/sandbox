/**
 * @file DataVariant.h
 * @brief Type-safe generic data container for VSE data bus system
 *
 * Provides a variant-based container supporting multiple data types with
 * type-safe access and conversion methods. Used for transmitting data
 * through topics and between component pins.
 */

#ifndef VSE_CORE_DATAVARIANT_H
#define VSE_CORE_DATAVARIANT_H

#include <variant>
#include <string>
#include <stdexcept>
#include <nlohmann/json.hpp>

namespace VSE {
namespace Core {

/**
 * @enum DataType
 * @brief Enumeration of supported data types in DataVariant
 */
enum class DataType {
    Null,       ///< Empty/uninitialized value
    Bool,       ///< Boolean value
    Int,        ///< Integer value
    Float,      ///< Single-precision floating point
    Double,     ///< Double-precision floating point
    String,     ///< String value
    Json        ///< JSON object/array
};

/**
 * @class DataVariant
 * @brief Generic type-safe container for component pin data
 *
 * Provides a variant-based storage mechanism supporting bool, int, float,
 * double, string, and JSON types. Includes type checking, conversion, and
 * serialization capabilities.
 *
 * Example usage:
 * @code
 * DataVariant value(42);
 * if (value.is<int>()) {
 *     int num = value.getInt();
 * }
 * @endcode
 */
class DataVariant {
public:
    /**
     * @brief Default constructor - creates null variant
     */
    DataVariant();

    /**
     * @brief Construct from boolean
     */
    explicit DataVariant(bool value);

    /**
     * @brief Construct from integer
     */
    explicit DataVariant(int value);

    /**
     * @brief Construct from float
     */
    explicit DataVariant(float value);

    /**
     * @brief Construct from double
     */
    explicit DataVariant(double value);

    /**
     * @brief Construct from string
     */
    explicit DataVariant(const std::string& value);

    /**
     * @brief Construct from C-string
     */
    explicit DataVariant(const char* value);

    /**
     * @brief Construct from JSON
     */
    explicit DataVariant(const nlohmann::json& value);

    /**
     * @brief Copy constructor
     */
    DataVariant(const DataVariant& other) = default;

    /**
     * @brief Move constructor
     */
    DataVariant(DataVariant&& other) noexcept = default;

    /**
     * @brief Copy assignment
     */
    DataVariant& operator=(const DataVariant& other) = default;

    /**
     * @brief Move assignment
     */
    DataVariant& operator=(DataVariant&& other) noexcept = default;

    /**
     * @brief Get the current type of stored data
     * @return DataType enumeration value
     */
    DataType getType() const;

    /**
     * @brief Get type as string for debugging
     * @return String representation of current type
     */
    std::string getTypeString() const;

    /**
     * @brief Check if variant holds specific type
     * @tparam T Type to check for
     * @return true if variant holds type T
     */
    template<typename T>
    bool is() const;

    /**
     * @brief Check if variant is null/empty
     * @return true if null
     */
    bool isNull() const;

    /**
     * @brief Get boolean value
     * @return Boolean value
     * @throws std::runtime_error if not a boolean
     */
    bool getBool() const;

    /**
     * @brief Get integer value
     * @return Integer value
     * @throws std::runtime_error if not an integer
     */
    int getInt() const;

    /**
     * @brief Get float value
     * @return Float value
     * @throws std::runtime_error if not a float
     */
    float getFloat() const;

    /**
     * @brief Get double value
     * @return Double value
     * @throws std::runtime_error if not a double
     */
    double getDouble() const;

    /**
     * @brief Get string value
     * @return String value
     * @throws std::runtime_error if not a string
     */
    std::string getString() const;

    /**
     * @brief Get JSON value
     * @return JSON object/array
     * @throws std::runtime_error if not JSON
     */
    nlohmann::json getJson() const;

    /**
     * @brief Try to convert to boolean with sensible defaults
     * @param defaultValue Value to return on conversion failure
     * @return Boolean representation or default
     */
    bool toBool(bool defaultValue = false) const;

    /**
     * @brief Try to convert to integer with sensible defaults
     * @param defaultValue Value to return on conversion failure
     * @return Integer representation or default
     */
    int toInt(int defaultValue = 0) const;

    /**
     * @brief Try to convert to float with sensible defaults
     * @param defaultValue Value to return on conversion failure
     * @return Float representation or default
     */
    float toFloat(float defaultValue = 0.0f) const;

    /**
     * @brief Try to convert to double with sensible defaults
     * @param defaultValue Value to return on conversion failure
     * @return Double representation or default
     */
    double toDouble(double defaultValue = 0.0) const;

    /**
     * @brief Try to convert to string representation
     * @return String representation of value
     */
    std::string toString() const;

    /**
     * @brief Serialize to JSON
     * @return JSON representation with type information
     */
    nlohmann::json toJson() const;

    /**
     * @brief Deserialize from JSON
     * @param j JSON object with type and value fields
     * @return DataVariant constructed from JSON
     * @throws std::runtime_error on invalid JSON structure
     */
    static DataVariant fromJson(const nlohmann::json& j);

    /**
     * @brief Equality comparison
     */
    bool operator==(const DataVariant& other) const;

    /**
     * @brief Inequality comparison
     */
    bool operator!=(const DataVariant& other) const;

private:
    /// Internal storage using std::variant
    using VariantType = std::variant<
        std::monostate,     // Null
        bool,               // Bool
        int,                // Int
        float,              // Float
        double,             // Double
        std::string,        // String
        nlohmann::json      // Json
    >;

    VariantType m_data;

    /**
     * @brief Helper to get variant index for type
     */
    DataType indexToType(size_t index) const;
};

// Template specializations for is<T>()
template<> bool DataVariant::is<bool>() const;
template<> bool DataVariant::is<int>() const;
template<> bool DataVariant::is<float>() const;
template<> bool DataVariant::is<double>() const;
template<> bool DataVariant::is<std::string>() const;
template<> bool DataVariant::is<nlohmann::json>() const;

} // namespace Core
} // namespace VSE

#endif // VSE_CORE_DATAVARIANT_H

/**
 * @file TypeConverter.h
 * @brief Type conversion utilities between VSE DataVariant and Pin DataType
 *
 * Provides conversion functions to bridge the existing Pin system with the
 * new topic-based DataVariant system.
 */

#ifndef VSE_CORE_TYPECONVERTER_H
#define VSE_CORE_TYPECONVERTER_H

#include "core/DataVariant.h"
#include "core/Pin.h"
#include <QVariant>

namespace VSE {
namespace Core {

/**
 * @class TypeConverter
 * @brief Static utility class for type conversions
 *
 * Provides conversions between:
 * - VSE::DataType (Pin system) and VSE::Core::DataType (Topic system)
 * - QVariant and DataVariant
 * - Various type compatibility checks
 */
class TypeConverter {
public:
    /**
     * @brief Convert Pin DataType to Topic DataType
     * @param pinType Pin system data type
     * @return Core::DataType Topic system data type
     */
    static Core::DataType pinToTopicType(VSE::DataType pinType);

    /**
     * @brief Convert Topic DataType to Pin DataType
     * @param topicType Topic system data type
     * @return VSE::DataType Pin system data type
     */
    static VSE::DataType topicToPinType(Core::DataType topicType);

    /**
     * @brief Convert QVariant to DataVariant
     * @param qvar QVariant value
     * @return DataVariant Converted value
     */
    static DataVariant qvariantToDataVariant(const QVariant& qvar);

    /**
     * @brief Convert DataVariant to QVariant
     * @param dvar DataVariant value
     * @return QVariant Converted value
     */
    static QVariant dataVariantToQVariant(const DataVariant& dvar);

    /**
     * @brief Check if pin type is compatible with topic type
     * @param pinType Pin data type
     * @param topicType Topic data type
     * @return true if compatible
     */
    static bool areTypesCompatible(VSE::DataType pinType, Core::DataType topicType);

    /**
     * @brief Check if two topic types are compatible
     * @param type1 First type
     * @param type2 Second type
     * @return true if compatible
     */
    static bool areTopicTypesCompatible(Core::DataType type1, Core::DataType type2);

    /**
     * @brief Get string representation of topic DataType
     * @param type Topic data type
     * @return String representation
     */
    static std::string topicTypeToString(Core::DataType type);

    /**
     * @brief Parse string to topic DataType
     * @param str String representation
     * @return Core::DataType Parsed type or Null on failure
     */
    static Core::DataType stringToTopicType(const std::string& str);

private:
    TypeConverter() = delete; // Static class, no instances
};

} // namespace Core
} // namespace VSE

#endif // VSE_CORE_TYPECONVERTER_H

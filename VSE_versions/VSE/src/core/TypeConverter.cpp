/**
 * @file TypeConverter.cpp
 * @brief Implementation of type conversion utilities
 */

#include "core/TypeConverter.h"
#include <QString>

namespace VSE {
namespace Core {

Core::DataType TypeConverter::pinToTopicType(VSE::DataType pinType) {
    switch (pinType) {
        case VSE::DataType::Boolean:
            return Core::DataType::Bool;
        case VSE::DataType::Integer:
            return Core::DataType::Int;
        case VSE::DataType::Float:
            return Core::DataType::Double; // Use Double for compatibility
        case VSE::DataType::String:
            return Core::DataType::String;
        case VSE::DataType::Json:
            return Core::DataType::Json;
        case VSE::DataType::Any:
        default:
            return Core::DataType::Null; // Null represents "any" type
    }
}

VSE::DataType TypeConverter::topicToPinType(Core::DataType topicType) {
    switch (topicType) {
        case Core::DataType::Bool:
            return VSE::DataType::Boolean;
        case Core::DataType::Int:
            return VSE::DataType::Integer;
        case Core::DataType::Float:
        case Core::DataType::Double:
            return VSE::DataType::Float; // Map both float and double to Float
        case Core::DataType::String:
            return VSE::DataType::String;
        case Core::DataType::Json:
            return VSE::DataType::Json;
        case Core::DataType::Null:
        default:
            return VSE::DataType::Any; // Null maps to "any" type
    }
}

DataVariant TypeConverter::qvariantToDataVariant(const QVariant& qvar) {
    if (qvar.isNull() || !qvar.isValid()) {
        return DataVariant();
    }

    switch (qvar.typeId()) {
        case QMetaType::Bool:
            return DataVariant(qvar.toBool());

        case QMetaType::Int:
        case QMetaType::LongLong:
        case QMetaType::UInt:
        case QMetaType::ULongLong:
            return DataVariant(qvar.toInt());

        case QMetaType::Float:
            return DataVariant(qvar.toFloat());

        case QMetaType::Double:
            return DataVariant(qvar.toDouble());

        case QMetaType::QString:
            return DataVariant(qvar.toString().toStdString());

        default:
            // Try to convert to JSON for complex types
            if (qvar.canConvert<QString>()) {
                QString str = qvar.toString();
                try {
                    nlohmann::json j = nlohmann::json::parse(str.toStdString());
                    return DataVariant(j);
                } catch (...) {
                    // If JSON parsing fails, store as string
                    return DataVariant(str.toStdString());
                }
            }
            return DataVariant(); // Return null for unknown types
    }
}

QVariant TypeConverter::dataVariantToQVariant(const DataVariant& dvar) {
    switch (dvar.getType()) {
        case Core::DataType::Bool:
            return QVariant(dvar.getBool());

        case Core::DataType::Int:
            return QVariant(dvar.getInt());

        case Core::DataType::Float:
            return QVariant(dvar.getFloat());

        case Core::DataType::Double:
            return QVariant(dvar.getDouble());

        case Core::DataType::String:
            return QVariant(QString::fromStdString(dvar.getString()));

        case Core::DataType::Json:
            // Convert JSON to QString for QVariant storage
            return QVariant(QString::fromStdString(dvar.getJson().dump()));

        case Core::DataType::Null:
        default:
            return QVariant();
    }
}

bool TypeConverter::areTypesCompatible(VSE::DataType pinType, Core::DataType topicType) {
    // "Any" pin type is compatible with everything
    if (pinType == VSE::DataType::Any) {
        return true;
    }

    // Null topic type (untyped) is compatible with everything
    if (topicType == Core::DataType::Null) {
        return true;
    }

    // Convert pin type to topic type and compare
    Core::DataType convertedPinType = pinToTopicType(pinType);

    // Direct match
    if (convertedPinType == topicType) {
        return true;
    }

    // Allow numeric conversions (Int, Float, Double are compatible)
    if ((convertedPinType == Core::DataType::Int ||
         convertedPinType == Core::DataType::Float ||
         convertedPinType == Core::DataType::Double) &&
        (topicType == Core::DataType::Int ||
         topicType == Core::DataType::Float ||
         topicType == Core::DataType::Double)) {
        return true;
    }

    return false;
}

bool TypeConverter::areTopicTypesCompatible(Core::DataType type1, Core::DataType type2) {
    // Null (untyped) is compatible with everything
    if (type1 == Core::DataType::Null || type2 == Core::DataType::Null) {
        return true;
    }

    // Direct match
    if (type1 == type2) {
        return true;
    }

    // Numeric types are compatible with each other
    if ((type1 == Core::DataType::Int ||
         type1 == Core::DataType::Float ||
         type1 == Core::DataType::Double) &&
        (type2 == Core::DataType::Int ||
         type2 == Core::DataType::Float ||
         type2 == Core::DataType::Double)) {
        return true;
    }

    return false;
}

std::string TypeConverter::topicTypeToString(Core::DataType type) {
    switch (type) {
        case Core::DataType::Null:    return "Null";
        case Core::DataType::Bool:    return "Bool";
        case Core::DataType::Int:     return "Int";
        case Core::DataType::Float:   return "Float";
        case Core::DataType::Double:  return "Double";
        case Core::DataType::String:  return "String";
        case Core::DataType::Json:    return "Json";
        default:                      return "Unknown";
    }
}

Core::DataType TypeConverter::stringToTopicType(const std::string& str) {
    if (str == "Null" || str == "Any") return Core::DataType::Null;
    if (str == "Bool" || str == "Boolean") return Core::DataType::Bool;
    if (str == "Int" || str == "Integer") return Core::DataType::Int;
    if (str == "Float") return Core::DataType::Float;
    if (str == "Double") return Core::DataType::Double;
    if (str == "String") return Core::DataType::String;
    if (str == "Json") return Core::DataType::Json;
    return Core::DataType::Null; // Default to Null for unknown types
}

} // namespace Core
} // namespace VSE

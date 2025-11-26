/**
 * @file DataVariant.cpp
 * @brief Implementation of type-safe generic data container
 */

#include "core/DataVariant.h"
#include <sstream>
#include <cmath>

namespace VSE {
namespace Core {

// Constructors
DataVariant::DataVariant() : m_data(std::monostate{}) {}

DataVariant::DataVariant(bool value) : m_data(value) {}

DataVariant::DataVariant(int value) : m_data(value) {}

DataVariant::DataVariant(float value) : m_data(value) {}

DataVariant::DataVariant(double value) : m_data(value) {}

DataVariant::DataVariant(const std::string& value) : m_data(value) {}

DataVariant::DataVariant(const char* value) : m_data(std::string(value)) {}

DataVariant::DataVariant(const nlohmann::json& value) : m_data(value) {}

// Type information
DataType DataVariant::getType() const {
    return indexToType(m_data.index());
}

DataType DataVariant::indexToType(size_t index) const {
    switch (index) {
        case 0: return DataType::Null;
        case 1: return DataType::Bool;
        case 2: return DataType::Int;
        case 3: return DataType::Float;
        case 4: return DataType::Double;
        case 5: return DataType::String;
        case 6: return DataType::Json;
        default: return DataType::Null;
    }
}

std::string DataVariant::getTypeString() const {
    switch (getType()) {
        case DataType::Null:    return "Null";
        case DataType::Bool:    return "Bool";
        case DataType::Int:     return "Int";
        case DataType::Float:   return "Float";
        case DataType::Double:  return "Double";
        case DataType::String:  return "String";
        case DataType::Json:    return "Json";
        default:                return "Unknown";
    }
}

bool DataVariant::isNull() const {
    return std::holds_alternative<std::monostate>(m_data);
}

// Template specializations for is<T>()
template<>
bool DataVariant::is<bool>() const {
    return std::holds_alternative<bool>(m_data);
}

template<>
bool DataVariant::is<int>() const {
    return std::holds_alternative<int>(m_data);
}

template<>
bool DataVariant::is<float>() const {
    return std::holds_alternative<float>(m_data);
}

template<>
bool DataVariant::is<double>() const {
    return std::holds_alternative<double>(m_data);
}

template<>
bool DataVariant::is<std::string>() const {
    return std::holds_alternative<std::string>(m_data);
}

template<>
bool DataVariant::is<nlohmann::json>() const {
    return std::holds_alternative<nlohmann::json>(m_data);
}

// Type-safe getters
bool DataVariant::getBool() const {
    if (!is<bool>()) {
        throw std::runtime_error("DataVariant: Type mismatch - expected Bool, got " + getTypeString());
    }
    return std::get<bool>(m_data);
}

int DataVariant::getInt() const {
    if (!is<int>()) {
        throw std::runtime_error("DataVariant: Type mismatch - expected Int, got " + getTypeString());
    }
    return std::get<int>(m_data);
}

float DataVariant::getFloat() const {
    if (!is<float>()) {
        throw std::runtime_error("DataVariant: Type mismatch - expected Float, got " + getTypeString());
    }
    return std::get<float>(m_data);
}

double DataVariant::getDouble() const {
    if (!is<double>()) {
        throw std::runtime_error("DataVariant: Type mismatch - expected Double, got " + getTypeString());
    }
    return std::get<double>(m_data);
}

std::string DataVariant::getString() const {
    if (!is<std::string>()) {
        throw std::runtime_error("DataVariant: Type mismatch - expected String, got " + getTypeString());
    }
    return std::get<std::string>(m_data);
}

nlohmann::json DataVariant::getJson() const {
    if (!is<nlohmann::json>()) {
        throw std::runtime_error("DataVariant: Type mismatch - expected Json, got " + getTypeString());
    }
    return std::get<nlohmann::json>(m_data);
}

// Conversion methods with defaults
bool DataVariant::toBool(bool defaultValue) const {
    switch (getType()) {
        case DataType::Bool:
            return getBool();
        case DataType::Int:
            return getInt() != 0;
        case DataType::Float:
            return std::abs(getFloat()) > 1e-6f;
        case DataType::Double:
            return std::abs(getDouble()) > 1e-9;
        case DataType::String: {
            const auto& str = getString();
            return str == "true" || str == "1" || str == "yes";
        }
        case DataType::Json:
            return !getJson().is_null() && (getJson().is_boolean() ? getJson().get<bool>() : !getJson().empty());
        default:
            return defaultValue;
    }
}

int DataVariant::toInt(int defaultValue) const {
    switch (getType()) {
        case DataType::Int:
            return getInt();
        case DataType::Bool:
            return getBool() ? 1 : 0;
        case DataType::Float:
            return static_cast<int>(getFloat());
        case DataType::Double:
            return static_cast<int>(getDouble());
        case DataType::String:
            try {
                return std::stoi(getString());
            } catch (...) {
                return defaultValue;
            }
        case DataType::Json:
            if (getJson().is_number_integer()) {
                return getJson().get<int>();
            }
            return defaultValue;
        default:
            return defaultValue;
    }
}

float DataVariant::toFloat(float defaultValue) const {
    switch (getType()) {
        case DataType::Float:
            return getFloat();
        case DataType::Int:
            return static_cast<float>(getInt());
        case DataType::Double:
            return static_cast<float>(getDouble());
        case DataType::Bool:
            return getBool() ? 1.0f : 0.0f;
        case DataType::String:
            try {
                return std::stof(getString());
            } catch (...) {
                return defaultValue;
            }
        case DataType::Json:
            if (getJson().is_number()) {
                return getJson().get<float>();
            }
            return defaultValue;
        default:
            return defaultValue;
    }
}

double DataVariant::toDouble(double defaultValue) const {
    switch (getType()) {
        case DataType::Double:
            return getDouble();
        case DataType::Float:
            return static_cast<double>(getFloat());
        case DataType::Int:
            return static_cast<double>(getInt());
        case DataType::Bool:
            return getBool() ? 1.0 : 0.0;
        case DataType::String:
            try {
                return std::stod(getString());
            } catch (...) {
                return defaultValue;
            }
        case DataType::Json:
            if (getJson().is_number()) {
                return getJson().get<double>();
            }
            return defaultValue;
        default:
            return defaultValue;
    }
}

std::string DataVariant::toString() const {
    switch (getType()) {
        case DataType::String:
            return getString();
        case DataType::Bool:
            return getBool() ? "true" : "false";
        case DataType::Int:
            return std::to_string(getInt());
        case DataType::Float:
            return std::to_string(getFloat());
        case DataType::Double:
            return std::to_string(getDouble());
        case DataType::Json:
            return getJson().dump();
        case DataType::Null:
        default:
            return "";
    }
}

// Serialization
nlohmann::json DataVariant::toJson() const {
    nlohmann::json j;
    j["type"] = getTypeString();

    switch (getType()) {
        case DataType::Null:
            j["value"] = nullptr;
            break;
        case DataType::Bool:
            j["value"] = getBool();
            break;
        case DataType::Int:
            j["value"] = getInt();
            break;
        case DataType::Float:
            j["value"] = getFloat();
            break;
        case DataType::Double:
            j["value"] = getDouble();
            break;
        case DataType::String:
            j["value"] = getString();
            break;
        case DataType::Json:
            j["value"] = getJson();
            break;
    }

    return j;
}

DataVariant DataVariant::fromJson(const nlohmann::json& j) {
    if (!j.contains("type") || !j.contains("value")) {
        throw std::runtime_error("DataVariant::fromJson: Invalid JSON format - missing type or value");
    }

    std::string typeStr = j["type"].get<std::string>();
    const auto& value = j["value"];

    if (typeStr == "Null") {
        return DataVariant();
    } else if (typeStr == "Bool") {
        return DataVariant(value.get<bool>());
    } else if (typeStr == "Int") {
        return DataVariant(value.get<int>());
    } else if (typeStr == "Float") {
        return DataVariant(value.get<float>());
    } else if (typeStr == "Double") {
        return DataVariant(value.get<double>());
    } else if (typeStr == "String") {
        return DataVariant(value.get<std::string>());
    } else if (typeStr == "Json") {
        return DataVariant(value);
    } else {
        throw std::runtime_error("DataVariant::fromJson: Unknown type '" + typeStr + "'");
    }
}

// Comparison operators
bool DataVariant::operator==(const DataVariant& other) const {
    if (getType() != other.getType()) {
        return false;
    }

    switch (getType()) {
        case DataType::Null:
            return true;
        case DataType::Bool:
            return getBool() == other.getBool();
        case DataType::Int:
            return getInt() == other.getInt();
        case DataType::Float:
            return std::abs(getFloat() - other.getFloat()) < 1e-6f;
        case DataType::Double:
            return std::abs(getDouble() - other.getDouble()) < 1e-9;
        case DataType::String:
            return getString() == other.getString();
        case DataType::Json:
            return getJson() == other.getJson();
        default:
            return false;
    }
}

bool DataVariant::operator!=(const DataVariant& other) const {
    return !(*this == other);
}

} // namespace Core
} // namespace VSE

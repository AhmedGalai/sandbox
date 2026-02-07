#include "core/Parameter.h"
#include <algorithm>

namespace VSE {

// ============================================================================
// Parameter Base Class
// ============================================================================

Parameter::Parameter(const QString& name, const QString& description)
    : m_name(name), m_description(description) {
}

// ============================================================================
// IntParameter
// ============================================================================

IntParameter::IntParameter(const QString& name, int defaultValue,
                           int minValue, int maxValue,
                           const QString& description)
    : Parameter(name, description),
      m_value(defaultValue),
      m_minValue(minValue),
      m_maxValue(maxValue) {
    // Clamp default value to range
    m_value = std::clamp(m_value, m_minValue, m_maxValue);
}

QVariant IntParameter::getValue() const {
    return QVariant(m_value);
}

void IntParameter::setValue(const QVariant& value) {
    bool ok;
    int intValue = value.toInt(&ok);
    if (ok) {
        setIntValue(intValue);
    }
}

void IntParameter::setIntValue(int value) {
    m_value = std::clamp(value, m_minValue, m_maxValue);
}

nlohmann::json IntParameter::toJson() const {
    nlohmann::json j;
    j["name"] = m_name.toStdString();
    j["description"] = m_description.toStdString();
    j["type"] = "int";
    j["value"] = m_value;
    j["min"] = m_minValue;
    j["max"] = m_maxValue;
    return j;
}

void IntParameter::fromJson(const nlohmann::json& json) {
    if (json.contains("value") && json["value"].is_number_integer()) {
        setIntValue(json["value"].get<int>());
    }
    if (json.contains("description") && json["description"].is_string()) {
        m_description = QString::fromStdString(json["description"].get<std::string>());
    }
}

// ============================================================================
// FloatParameter
// ============================================================================

FloatParameter::FloatParameter(const QString& name, float defaultValue,
                               float minValue, float maxValue,
                               const QString& description)
    : Parameter(name, description),
      m_value(defaultValue),
      m_minValue(minValue),
      m_maxValue(maxValue) {
    // Clamp default value to range
    m_value = std::clamp(m_value, m_minValue, m_maxValue);
}

QVariant FloatParameter::getValue() const {
    return QVariant(m_value);
}

void FloatParameter::setValue(const QVariant& value) {
    bool ok;
    float floatValue = value.toFloat(&ok);
    if (ok) {
        setFloatValue(floatValue);
    }
}

void FloatParameter::setFloatValue(float value) {
    m_value = std::clamp(value, m_minValue, m_maxValue);
}

nlohmann::json FloatParameter::toJson() const {
    nlohmann::json j;
    j["name"] = m_name.toStdString();
    j["description"] = m_description.toStdString();
    j["type"] = "float";
    j["value"] = m_value;
    j["min"] = m_minValue;
    j["max"] = m_maxValue;
    return j;
}

void FloatParameter::fromJson(const nlohmann::json& json) {
    if (json.contains("value") && json["value"].is_number()) {
        setFloatValue(json["value"].get<float>());
    }
    if (json.contains("description") && json["description"].is_string()) {
        m_description = QString::fromStdString(json["description"].get<std::string>());
    }
}

// ============================================================================
// StringParameter
// ============================================================================

StringParameter::StringParameter(const QString& name, const QString& defaultValue,
                                 const QString& description)
    : Parameter(name, description),
      m_value(defaultValue) {
}

QVariant StringParameter::getValue() const {
    return QVariant(m_value);
}

void StringParameter::setValue(const QVariant& value) {
    m_value = value.toString();
}

nlohmann::json StringParameter::toJson() const {
    nlohmann::json j;
    j["name"] = m_name.toStdString();
    j["description"] = m_description.toStdString();
    j["type"] = "string";
    j["value"] = m_value.toStdString();
    return j;
}

void StringParameter::fromJson(const nlohmann::json& json) {
    if (json.contains("value") && json["value"].is_string()) {
        m_value = QString::fromStdString(json["value"].get<std::string>());
    }
    if (json.contains("description") && json["description"].is_string()) {
        m_description = QString::fromStdString(json["description"].get<std::string>());
    }
}

// ============================================================================
// BoolParameter
// ============================================================================

BoolParameter::BoolParameter(const QString& name, bool defaultValue,
                             const QString& description)
    : Parameter(name, description),
      m_value(defaultValue) {
}

QVariant BoolParameter::getValue() const {
    return QVariant(m_value);
}

void BoolParameter::setValue(const QVariant& value) {
    m_value = value.toBool();
}

nlohmann::json BoolParameter::toJson() const {
    nlohmann::json j;
    j["name"] = m_name.toStdString();
    j["description"] = m_description.toStdString();
    j["type"] = "bool";
    j["value"] = m_value;
    return j;
}

void BoolParameter::fromJson(const nlohmann::json& json) {
    if (json.contains("value") && json["value"].is_boolean()) {
        m_value = json["value"].get<bool>();
    }
    if (json.contains("description") && json["description"].is_string()) {
        m_description = QString::fromStdString(json["description"].get<std::string>());
    }
}

// ============================================================================
// FilePathParameter
// ============================================================================

FilePathParameter::FilePathParameter(const QString& name, const QString& defaultPath,
                                     const QString& filter, const QString& description)
    : Parameter(name, description),
      m_path(defaultPath),
      m_filter(filter) {
}

QVariant FilePathParameter::getValue() const {
    return QVariant(m_path);
}

void FilePathParameter::setValue(const QVariant& value) {
    m_path = value.toString();
}

nlohmann::json FilePathParameter::toJson() const {
    nlohmann::json j;
    j["name"] = m_name.toStdString();
    j["description"] = m_description.toStdString();
    j["type"] = "filepath";
    j["value"] = m_path.toStdString();
    j["filter"] = m_filter.toStdString();
    return j;
}

void FilePathParameter::fromJson(const nlohmann::json& json) {
    if (json.contains("value") && json["value"].is_string()) {
        m_path = QString::fromStdString(json["value"].get<std::string>());
    }
    if (json.contains("filter") && json["filter"].is_string()) {
        m_filter = QString::fromStdString(json["filter"].get<std::string>());
    }
    if (json.contains("description") && json["description"].is_string()) {
        m_description = QString::fromStdString(json["description"].get<std::string>());
    }
}

// ============================================================================
// ColorParameter
// ============================================================================

ColorParameter::ColorParameter(const QString& name, const QColor& defaultColor,
                               const QString& description)
    : Parameter(name, description),
      m_color(defaultColor) {
}

QVariant ColorParameter::getValue() const {
    return QVariant(m_color);
}

void ColorParameter::setValue(const QVariant& value) {
    if (value.canConvert<QColor>()) {
        m_color = value.value<QColor>();
    }
}

nlohmann::json ColorParameter::toJson() const {
    nlohmann::json j;
    j["name"] = m_name.toStdString();
    j["description"] = m_description.toStdString();
    j["type"] = "color";
    j["r"] = m_color.red();
    j["g"] = m_color.green();
    j["b"] = m_color.blue();
    j["a"] = m_color.alpha();
    return j;
}

void ColorParameter::fromJson(const nlohmann::json& json) {
    if (json.contains("r") && json.contains("g") &&
        json.contains("b") && json.contains("a")) {
        int r = json["r"].get<int>();
        int g = json["g"].get<int>();
        int b = json["b"].get<int>();
        int a = json["a"].get<int>();
        m_color = QColor(r, g, b, a);
    }
    if (json.contains("description") && json["description"].is_string()) {
        m_description = QString::fromStdString(json["description"].get<std::string>());
    }
}

} // namespace VSE

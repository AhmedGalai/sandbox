#ifndef VSE_PARAMETER_H
#define VSE_PARAMETER_H

#include <QString>
#include <QVariant>
#include <QColor>
#include <memory>
#include <string>
#include <nlohmann/json.hpp>

namespace VSE {

/**
 * @brief Base class for component parameters
 *
 * Provides a common interface for all parameter types used in components.
 * Parameters can be exposed in the inspector for user configuration.
 */
class Parameter {
public:
    /**
     * @brief Construct a new Parameter object
     * @param name Parameter name (used as identifier)
     * @param description Human-readable description
     */
    Parameter(const QString& name, const QString& description = "");

    virtual ~Parameter() = default;

    /**
     * @brief Get the parameter name
     * @return const QString& Parameter name
     */
    const QString& getName() const { return m_name; }

    /**
     * @brief Get the parameter description
     * @return const QString& Parameter description
     */
    const QString& getDescription() const { return m_description; }

    /**
     * @brief Set the parameter description
     * @param description New description
     */
    void setDescription(const QString& description) { m_description = description; }

    /**
     * @brief Get the parameter value as QVariant
     * @return QVariant Parameter value
     */
    virtual QVariant getValue() const = 0;

    /**
     * @brief Set the parameter value from QVariant
     * @param value New value
     */
    virtual void setValue(const QVariant& value) = 0;

    /**
     * @brief Serialize parameter to JSON
     * @return nlohmann::json JSON representation
     */
    virtual nlohmann::json toJson() const = 0;

    /**
     * @brief Deserialize parameter from JSON
     * @param json JSON data
     */
    virtual void fromJson(const nlohmann::json& json) = 0;

    /**
     * @brief Get the type name of the parameter
     * @return std::string Type name
     */
    virtual std::string getTypeName() const = 0;

protected:
    QString m_name;        ///< Parameter name
    QString m_description; ///< Parameter description
};

/**
 * @brief Integer parameter type
 */
class IntParameter : public Parameter {
public:
    IntParameter(const QString& name, int defaultValue = 0,
                 int minValue = std::numeric_limits<int>::min(),
                 int maxValue = std::numeric_limits<int>::max(),
                 const QString& description = "");

    QVariant getValue() const override;
    void setValue(const QVariant& value) override;

    int getIntValue() const { return m_value; }
    void setIntValue(int value);

    int getMinValue() const { return m_minValue; }
    int getMaxValue() const { return m_maxValue; }

    nlohmann::json toJson() const override;
    void fromJson(const nlohmann::json& json) override;
    std::string getTypeName() const override { return "int"; }

private:
    int m_value;
    int m_minValue;
    int m_maxValue;
};

/**
 * @brief Float parameter type
 */
class FloatParameter : public Parameter {
public:
    FloatParameter(const QString& name, float defaultValue = 0.0f,
                   float minValue = std::numeric_limits<float>::lowest(),
                   float maxValue = std::numeric_limits<float>::max(),
                   const QString& description = "");

    QVariant getValue() const override;
    void setValue(const QVariant& value) override;

    float getFloatValue() const { return m_value; }
    void setFloatValue(float value);

    float getMinValue() const { return m_minValue; }
    float getMaxValue() const { return m_maxValue; }

    nlohmann::json toJson() const override;
    void fromJson(const nlohmann::json& json) override;
    std::string getTypeName() const override { return "float"; }

private:
    float m_value;
    float m_minValue;
    float m_maxValue;
};

/**
 * @brief String parameter type
 */
class StringParameter : public Parameter {
public:
    StringParameter(const QString& name, const QString& defaultValue = "",
                    const QString& description = "");

    QVariant getValue() const override;
    void setValue(const QVariant& value) override;

    QString getStringValue() const { return m_value; }
    void setStringValue(const QString& value) { m_value = value; }

    nlohmann::json toJson() const override;
    void fromJson(const nlohmann::json& json) override;
    std::string getTypeName() const override { return "string"; }

private:
    QString m_value;
};

/**
 * @brief Boolean parameter type
 */
class BoolParameter : public Parameter {
public:
    BoolParameter(const QString& name, bool defaultValue = false,
                  const QString& description = "");

    QVariant getValue() const override;
    void setValue(const QVariant& value) override;

    bool getBoolValue() const { return m_value; }
    void setBoolValue(bool value) { m_value = value; }

    nlohmann::json toJson() const override;
    void fromJson(const nlohmann::json& json) override;
    std::string getTypeName() const override { return "bool"; }

private:
    bool m_value;
};

/**
 * @brief File path parameter type
 */
class FilePathParameter : public Parameter {
public:
    FilePathParameter(const QString& name, const QString& defaultPath = "",
                      const QString& filter = "All Files (*.*)",
                      const QString& description = "");

    QVariant getValue() const override;
    void setValue(const QVariant& value) override;

    QString getPath() const { return m_path; }
    void setPath(const QString& path) { m_path = path; }

    QString getFilter() const { return m_filter; }
    void setFilter(const QString& filter) { m_filter = filter; }

    nlohmann::json toJson() const override;
    void fromJson(const nlohmann::json& json) override;
    std::string getTypeName() const override { return "filepath"; }

private:
    QString m_path;
    QString m_filter;
};

/**
 * @brief Color parameter type
 */
class ColorParameter : public Parameter {
public:
    ColorParameter(const QString& name, const QColor& defaultColor = QColor(255, 255, 255),
                   const QString& description = "");

    QVariant getValue() const override;
    void setValue(const QVariant& value) override;

    QColor getColorValue() const { return m_color; }
    void setColorValue(const QColor& color) { m_color = color; }

    nlohmann::json toJson() const override;
    void fromJson(const nlohmann::json& json) override;
    std::string getTypeName() const override { return "color"; }

private:
    QColor m_color;
};

} // namespace VSE

#endif // VSE_PARAMETER_H

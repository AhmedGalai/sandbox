/**
 * @file Component.cpp
 * @brief Implementation of Component base class
 */

#include "core/Component.h"
#include <QUuid>
#include <algorithm>

namespace VSE {
namespace Core {

Component::Component(const QString& name, const QString& category, QObject* parent)
    : QObject(parent)
    , m_name(name)
    , m_category(category)
    , m_id(QUuid::createUuid().toString(QUuid::WithoutBraces))
    , m_hasExecuted(false)
{
}

Component::~Component() {
}

QString Component::getDisplayName() const {
    return m_displayName.isEmpty() ? m_name : m_displayName;
}

std::shared_ptr<InputPin> Component::addInputPin(const QString& name, DataType dataType) {
    auto pin = std::make_shared<InputPin>(name, dataType);
    pin->setId(m_id + "_in_" + name);
    m_inputPins.push_back(pin);
    return pin;
}

std::shared_ptr<OutputPin> Component::addOutputPin(const QString& name, DataType dataType) {
    auto pin = std::make_shared<OutputPin>(name, dataType);
    pin->setId(m_id + "_out_" + name);
    m_outputPins.push_back(pin);
    return pin;
}

std::shared_ptr<InputPin> Component::getInputPin(const QString& name) const {
    auto it = std::find_if(m_inputPins.begin(), m_inputPins.end(),
        [&name](const auto& pin) { return pin->getName() == name; });
    return it != m_inputPins.end() ? *it : nullptr;
}

std::shared_ptr<OutputPin> Component::getOutputPin(const QString& name) const {
    auto it = std::find_if(m_outputPins.begin(), m_outputPins.end(),
        [&name](const auto& pin) { return pin->getName() == name; });
    return it != m_outputPins.end() ? *it : nullptr;
}

void Component::addParameter(std::shared_ptr<Parameter> parameter) {
    m_parameters.push_back(parameter);
}

std::shared_ptr<Parameter> Component::getParameter(const QString& name) const {
    auto it = std::find_if(m_parameters.begin(), m_parameters.end(),
        [&name](const auto& param) { return param->getName() == name; });
    return it != m_parameters.end() ? *it : nullptr;
}

void Component::resetExecutionState() {
    m_hasExecuted = false;
}

QVariant Component::getInputValue(const QString& pinName) const {
    auto pin = getInputPin(pinName);
    return pin ? pin->getData() : QVariant();
}

bool Component::setOutputValue(const QString& pinName, const QVariant& value) {
    auto pin = getOutputPin(pinName);
    if (pin) {
        pin->transmitData(value);
        return true;
    }
    return false;
}

void Component::emitError(const QString& message) {
    emit executionError(message);
}

nlohmann::json Component::serialize() const {
    nlohmann::json j;

    j["type"] = m_name.toStdString();
    j["id"] = m_id.toStdString();
    j["category"] = m_category.toStdString();
    j["displayName"] = m_displayName.toStdString();

    // Serialize parameters
    nlohmann::json params = nlohmann::json::array();
    for (const auto& param : m_parameters) {
        params.push_back(param->toJson());
    }
    j["parameters"] = params;

    // Serialize pin metadata (connections are handled at graph level)
    nlohmann::json inputPins = nlohmann::json::array();
    for (const auto& pin : m_inputPins) {
        inputPins.push_back(pin->toJson());
    }
    j["inputPins"] = inputPins;

    nlohmann::json outputPins = nlohmann::json::array();
    for (const auto& pin : m_outputPins) {
        outputPins.push_back(pin->toJson());
    }
    j["outputPins"] = outputPins;

    return j;
}

bool Component::deserialize(const nlohmann::json& json) {
    try {
        if (json.contains("id")) {
            m_id = QString::fromStdString(json["id"].get<std::string>());
        }

        if (json.contains("displayName")) {
            m_displayName = QString::fromStdString(json["displayName"].get<std::string>());
        }

        // Deserialize parameters
        if (json.contains("parameters") && json["parameters"].is_array()) {
            for (size_t i = 0; i < json["parameters"].size() && i < m_parameters.size(); ++i) {
                m_parameters[i]->fromJson(json["parameters"][i]);
            }
        }

        return true;
    } catch (const std::exception& e) {
        emitError(QString("Deserialization error: %1").arg(e.what()));
        return false;
    }
}

} // namespace Core
} // namespace VSE

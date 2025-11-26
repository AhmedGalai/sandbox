#include "core/ComponentBase.h"
#include <QUuid>
#include <algorithm>

namespace VSE {

// ============================================================================
// ComponentBase
// ============================================================================

ComponentBase::ComponentBase(QObject* parent)
    : QObject(parent),
      m_id(QUuid::createUuid().toString(QUuid::WithoutBraces)),
      m_state(ComponentState::Idle) {
}

void ComponentBase::setState(ComponentState state) {
    if (m_state != state) {
        m_state = state;
        emit stateChanged(state);
    }
}

std::shared_ptr<InputPin> ComponentBase::getInputPin(const QString& name) const {
    auto it = std::find_if(m_inputPins.begin(), m_inputPins.end(),
                          [&name](const std::shared_ptr<InputPin>& pin) {
                              return pin->getName() == name;
                          });
    return (it != m_inputPins.end()) ? *it : nullptr;
}

std::shared_ptr<OutputPin> ComponentBase::getOutputPin(const QString& name) const {
    auto it = std::find_if(m_outputPins.begin(), m_outputPins.end(),
                          [&name](const std::shared_ptr<OutputPin>& pin) {
                              return pin->getName() == name;
                          });
    return (it != m_outputPins.end()) ? *it : nullptr;
}

std::shared_ptr<Parameter> ComponentBase::getParameter(const QString& name) const {
    auto it = std::find_if(m_parameters.begin(), m_parameters.end(),
                          [&name](const std::shared_ptr<Parameter>& param) {
                              return param->getName() == name;
                          });
    return (it != m_parameters.end()) ? *it : nullptr;
}

nlohmann::json ComponentBase::serialize() const {
    nlohmann::json j;

    // Basic component info
    j["id"] = m_id.toStdString();
    j["type"] = getName().toStdString();
    j["category"] = getCategory().toStdString();

    // Serialize input pins
    nlohmann::json inputPins = nlohmann::json::array();
    for (const auto& pin : m_inputPins) {
        if (pin) {
            inputPins.push_back(pin->toJson());
        }
    }
    j["inputPins"] = inputPins;

    // Serialize output pins
    nlohmann::json outputPins = nlohmann::json::array();
    for (const auto& pin : m_outputPins) {
        if (pin) {
            outputPins.push_back(pin->toJson());
        }
    }
    j["outputPins"] = outputPins;

    // Serialize parameters
    nlohmann::json parameters = nlohmann::json::array();
    for (const auto& param : m_parameters) {
        if (param) {
            parameters.push_back(param->toJson());
        }
    }
    j["parameters"] = parameters;

    return j;
}

void ComponentBase::deserialize(const nlohmann::json& json) {
    // Restore component ID
    if (json.contains("id") && json["id"].is_string()) {
        m_id = QString::fromStdString(json["id"].get<std::string>());
    }

    // Restore input pins
    if (json.contains("inputPins") && json["inputPins"].is_array()) {
        for (size_t i = 0; i < json["inputPins"].size() && i < m_inputPins.size(); ++i) {
            if (m_inputPins[i]) {
                m_inputPins[i]->fromJson(json["inputPins"][i]);
            }
        }
    }

    // Restore output pins
    if (json.contains("outputPins") && json["outputPins"].is_array()) {
        for (size_t i = 0; i < json["outputPins"].size() && i < m_outputPins.size(); ++i) {
            if (m_outputPins[i]) {
                m_outputPins[i]->fromJson(json["outputPins"][i]);
            }
        }
    }

    // Restore parameters
    if (json.contains("parameters") && json["parameters"].is_array()) {
        for (size_t i = 0; i < json["parameters"].size() && i < m_parameters.size(); ++i) {
            if (m_parameters[i]) {
                m_parameters[i]->fromJson(json["parameters"][i]);
            }
        }
    }
}

std::shared_ptr<InputPin> ComponentBase::addInputPin(const QString& name, DataType dataType) {
    auto pin = std::make_shared<InputPin>(name, dataType);
    m_inputPins.push_back(pin);
    return pin;
}

std::shared_ptr<OutputPin> ComponentBase::addOutputPin(const QString& name, DataType dataType) {
    auto pin = std::make_shared<OutputPin>(name, dataType);
    m_outputPins.push_back(pin);
    return pin;
}

void ComponentBase::addParameter(std::shared_ptr<Parameter> parameter) {
    if (parameter) {
        m_parameters.push_back(parameter);
    }
}

void ComponentBase::reportError(const QString& message) {
    setState(ComponentState::Error);
    emit errorOccurred(message);
}

} // namespace VSE

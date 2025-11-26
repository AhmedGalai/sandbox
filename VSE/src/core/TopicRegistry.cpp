/**
 * @file TopicRegistry.cpp
 * @brief Implementation of topic registry and topic management
 */

#include "core/TopicRegistry.h"
#include <algorithm>

namespace VSE {
namespace Core {

// ============================================================================
// Topic Implementation
// ============================================================================

Topic::Topic(const std::string& name, DataType expectedType)
    : m_name(name)
    , m_expectedType(expectedType)
    , m_nextSubscriptionId(1)
    , m_publishCount(0)
{
}

bool Topic::publish(const DataVariant& data) {
    std::lock_guard<std::mutex> lock(m_mutex);

    // Type checking if topic is typed
    if (isTyped() && data.getType() != m_expectedType) {
        // Allow publishing if data is convertible or if we're lenient
        // For strict mode, return false here
        // For now, we'll be strict
        return false;
    }

    // Cache the value
    m_lastValue = data;
    m_publishCount++;

    // Create a copy of subscribers to avoid holding lock during callbacks
    auto subscribersCopy = m_subscribers;

    // Release lock before calling callbacks to prevent deadlocks
    lock.~lock_guard();

    // Notify all subscribers
    for (const auto& [id, callback] : subscribersCopy) {
        try {
            if (callback) {
                callback(m_name, data);
            }
        } catch (const std::exception& e) {
            // Silently catch exceptions from callbacks to prevent one bad
            // subscriber from breaking others
            // In production, could log this error
        }
    }

    return true;
}

uint64_t Topic::subscribe(TopicCallback callback) {
    std::lock_guard<std::mutex> lock(m_mutex);

    if (!callback) {
        return 0; // Invalid callback
    }

    uint64_t id = m_nextSubscriptionId++;
    m_subscribers[id] = std::move(callback);

    return id;
}

bool Topic::unsubscribe(uint64_t subscriptionId) {
    std::lock_guard<std::mutex> lock(m_mutex);

    auto it = m_subscribers.find(subscriptionId);
    if (it == m_subscribers.end()) {
        return false;
    }

    m_subscribers.erase(it);
    return true;
}

void Topic::clearValue() {
    std::lock_guard<std::mutex> lock(m_mutex);
    m_lastValue.reset();
}

// ============================================================================
// TopicRegistry Implementation
// ============================================================================

TopicRegistry& TopicRegistry::instance() {
    static TopicRegistry instance;
    return instance;
}

bool TopicRegistry::createTopic(const std::string& name, DataType expectedType) {
    std::lock_guard<std::mutex> lock(m_mutex);

    if (name.empty()) {
        return false;
    }

    // Check if topic already exists
    if (m_topics.find(name) != m_topics.end()) {
        return false;
    }

    // Create new topic
    m_topics[name] = std::make_shared<Topic>(name, expectedType);
    return true;
}

bool TopicRegistry::deleteTopic(const std::string& name) {
    std::lock_guard<std::mutex> lock(m_mutex);

    auto it = m_topics.find(name);
    if (it == m_topics.end()) {
        return false;
    }

    m_topics.erase(it);
    return true;
}

bool TopicRegistry::hasTopic(const std::string& name) const {
    std::lock_guard<std::mutex> lock(m_mutex);
    return m_topics.find(name) != m_topics.end();
}

DataType TopicRegistry::getTopicType(const std::string& name) const {
    auto topic = getTopic(name);
    if (!topic) {
        return DataType::Null;
    }
    return topic->getExpectedType();
}

bool TopicRegistry::setTopicType(const std::string& name, DataType type) {
    auto topic = getTopic(name);
    if (!topic) {
        return false;
    }
    topic->setExpectedType(type);
    return true;
}

bool TopicRegistry::publish(const std::string& name, const DataVariant& data) {
    auto topic = getTopic(name);
    if (!topic) {
        return false;
    }
    return topic->publish(data);
}

uint64_t TopicRegistry::subscribe(const std::string& name, TopicCallback callback) {
    auto topic = getTopic(name);
    if (!topic) {
        return 0;
    }
    return topic->subscribe(std::move(callback));
}

bool TopicRegistry::unsubscribe(const std::string& name, uint64_t subscriptionId) {
    auto topic = getTopic(name);
    if (!topic) {
        return false;
    }
    return topic->unsubscribe(subscriptionId);
}

std::optional<DataVariant> TopicRegistry::getLastValue(const std::string& name) const {
    auto topic = getTopic(name);
    if (!topic) {
        return std::nullopt;
    }
    return topic->getLastValue();
}

std::vector<std::string> TopicRegistry::getTopicNames() const {
    std::lock_guard<std::mutex> lock(m_mutex);

    std::vector<std::string> names;
    names.reserve(m_topics.size());

    for (const auto& [name, topic] : m_topics) {
        names.push_back(name);
    }

    return names;
}

size_t TopicRegistry::getSubscriberCount(const std::string& name) const {
    auto topic = getTopic(name);
    if (!topic) {
        return 0;
    }
    return topic->getSubscriberCount();
}

void TopicRegistry::clear() {
    std::lock_guard<std::mutex> lock(m_mutex);
    m_topics.clear();
}

size_t TopicRegistry::getTopicCount() const {
    std::lock_guard<std::mutex> lock(m_mutex);
    return m_topics.size();
}

nlohmann::json TopicRegistry::getTopicStats(const std::string& name) const {
    auto topic = getTopic(name);
    if (!topic) {
        return nullptr;
    }

    nlohmann::json stats;
    stats["name"] = topic->getName();
    stats["type"] = topic->getExpectedType() == DataType::Null ? "any" :
                    DataVariant().getTypeString(); // Would need proper type to string conversion
    stats["subscribers"] = topic->getSubscriberCount();
    stats["publishCount"] = topic->getPublishCount();
    stats["hasValue"] = topic->hasValue();

    if (topic->hasValue()) {
        stats["lastValue"] = topic->getLastValue()->toJson();
    }

    return stats;
}

nlohmann::json TopicRegistry::exportToJson() const {
    std::lock_guard<std::mutex> lock(m_mutex);

    nlohmann::json j;
    j["topicCount"] = m_topics.size();
    j["topics"] = nlohmann::json::array();

    for (const auto& [name, topic] : m_topics) {
        nlohmann::json topicJson;
        topicJson["name"] = topic->getName();

        // Convert DataType to string
        std::string typeStr;
        switch (topic->getExpectedType()) {
            case DataType::Null:    typeStr = "any"; break;
            case DataType::Bool:    typeStr = "Bool"; break;
            case DataType::Int:     typeStr = "Int"; break;
            case DataType::Float:   typeStr = "Float"; break;
            case DataType::Double:  typeStr = "Double"; break;
            case DataType::String:  typeStr = "String"; break;
            case DataType::Json:    typeStr = "Json"; break;
        }
        topicJson["type"] = typeStr;

        topicJson["subscribers"] = topic->getSubscriberCount();
        topicJson["publishCount"] = topic->getPublishCount();
        topicJson["hasValue"] = topic->hasValue();

        if (topic->hasValue()) {
            topicJson["lastValue"] = topic->getLastValue()->toJson();
        }

        j["topics"].push_back(topicJson);
    }

    return j;
}

std::shared_ptr<Topic> TopicRegistry::getTopic(const std::string& name) const {
    std::lock_guard<std::mutex> lock(m_mutex);

    auto it = m_topics.find(name);
    if (it == m_topics.end()) {
        return nullptr;
    }

    return it->second;
}

} // namespace Core
} // namespace VSE

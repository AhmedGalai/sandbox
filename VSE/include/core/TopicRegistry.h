/**
 * @file TopicRegistry.h
 * @brief Central registry for managing data topics (data buses) in VSE
 *
 * Provides a thread-safe singleton registry for creating, managing, and
 * routing data through named topics. Topics act as data buses that components
 * can publish to and subscribe from.
 */

#ifndef VSE_CORE_TOPICREGISTRY_H
#define VSE_CORE_TOPICREGISTRY_H

#include "core/DataVariant.h"
#include <string>
#include <map>
#include <vector>
#include <functional>
#include <memory>
#include <mutex>
#include <optional>

namespace VSE {
namespace Core {

/**
 * @brief Callback function type for topic subscribers
 * @param topicName Name of the topic that published data
 * @param data The published data
 */
using TopicCallback = std::function<void(const std::string& topicName, const DataVariant& data)>;

/**
 * @class Topic
 * @brief Internal representation of a data topic/bus
 *
 * A topic represents a named communication channel that supports typed data
 * transmission. Components can publish data to a topic and subscribe to receive
 * updates when new data is published.
 */
class Topic {
public:
    /**
     * @brief Construct a new topic
     * @param name Unique name for this topic
     * @param expectedType Expected data type (Null = any type)
     */
    explicit Topic(const std::string& name, DataType expectedType = DataType::Null);

    /**
     * @brief Get topic name
     */
    const std::string& getName() const { return m_name; }

    /**
     * @brief Get expected data type
     */
    DataType getExpectedType() const { return m_expectedType; }

    /**
     * @brief Set expected data type
     * @param type New expected type
     */
    void setExpectedType(DataType type) { m_expectedType = type; }

    /**
     * @brief Check if topic has specific type requirement
     */
    bool isTyped() const { return m_expectedType != DataType::Null; }

    /**
     * @brief Publish data to this topic
     * @param data Data to publish
     * @return true if successful, false if type mismatch
     */
    bool publish(const DataVariant& data);

    /**
     * @brief Subscribe to topic updates
     * @param callback Function to call when data is published
     * @return Subscription ID for later unsubscription
     */
    uint64_t subscribe(TopicCallback callback);

    /**
     * @brief Unsubscribe from topic
     * @param subscriptionId ID returned from subscribe()
     * @return true if unsubscribed, false if ID not found
     */
    bool unsubscribe(uint64_t subscriptionId);

    /**
     * @brief Get number of active subscribers
     */
    size_t getSubscriberCount() const { return m_subscribers.size(); }

    /**
     * @brief Get last published value (if any)
     * @return Last value or std::nullopt if nothing published yet
     */
    std::optional<DataVariant> getLastValue() const { return m_lastValue; }

    /**
     * @brief Check if topic has cached value
     */
    bool hasValue() const { return m_lastValue.has_value(); }

    /**
     * @brief Clear cached value
     */
    void clearValue();

    /**
     * @brief Get publish count for statistics
     */
    uint64_t getPublishCount() const { return m_publishCount; }

private:
    std::string m_name;
    DataType m_expectedType;
    std::optional<DataVariant> m_lastValue;
    std::map<uint64_t, TopicCallback> m_subscribers;
    uint64_t m_nextSubscriptionId;
    uint64_t m_publishCount;
    mutable std::mutex m_mutex;
};

/**
 * @class TopicRegistry
 * @brief Singleton registry managing all topics in the VSE system
 *
 * Thread-safe singleton that manages topic creation, deletion, and data routing.
 * Provides publish/subscribe functionality for inter-component communication.
 *
 * Example usage:
 * @code
 * auto& registry = TopicRegistry::instance();
 * registry.createTopic("sensors/temperature", DataType::Float);
 * registry.subscribe("sensors/temperature", [](const auto& name, const auto& data) {
 *     std::cout << "Temperature: " << data.toFloat() << std::endl;
 * });
 * registry.publish("sensors/temperature", DataVariant(25.5f));
 * @endcode
 */
class TopicRegistry {
public:
    /**
     * @brief Get singleton instance
     * @return Reference to the global TopicRegistry
     */
    static TopicRegistry& instance();

    /**
     * @brief Create a new topic
     * @param name Unique topic name
     * @param expectedType Expected data type (Null = any type)
     * @return true if created, false if topic already exists
     */
    bool createTopic(const std::string& name, DataType expectedType = DataType::Null);

    /**
     * @brief Delete a topic
     * @param name Topic name to delete
     * @return true if deleted, false if not found
     */
    bool deleteTopic(const std::string& name);

    /**
     * @brief Check if topic exists
     * @param name Topic name
     * @return true if topic exists
     */
    bool hasTopic(const std::string& name) const;

    /**
     * @brief Get topic expected type
     * @param name Topic name
     * @return Expected type or Null if topic doesn't exist
     */
    DataType getTopicType(const std::string& name) const;

    /**
     * @brief Set topic expected type
     * @param name Topic name
     * @param type New expected type
     * @return true if successful, false if topic not found
     */
    bool setTopicType(const std::string& name, DataType type);

    /**
     * @brief Publish data to a topic
     * @param name Topic name
     * @param data Data to publish
     * @return true if published successfully, false if topic not found or type mismatch
     */
    bool publish(const std::string& name, const DataVariant& data);

    /**
     * @brief Subscribe to a topic
     * @param name Topic name
     * @param callback Function to call on data updates
     * @return Subscription ID (0 if topic not found)
     */
    uint64_t subscribe(const std::string& name, TopicCallback callback);

    /**
     * @brief Unsubscribe from a topic
     * @param name Topic name
     * @param subscriptionId ID returned from subscribe()
     * @return true if unsubscribed, false if topic or subscription not found
     */
    bool unsubscribe(const std::string& name, uint64_t subscriptionId);

    /**
     * @brief Get last published value from a topic
     * @param name Topic name
     * @return Last value or std::nullopt if topic not found or no value published
     */
    std::optional<DataVariant> getLastValue(const std::string& name) const;

    /**
     * @brief Get all topic names
     * @return Vector of all registered topic names
     */
    std::vector<std::string> getTopicNames() const;

    /**
     * @brief Get number of subscribers for a topic
     * @param name Topic name
     * @return Subscriber count (0 if topic not found)
     */
    size_t getSubscriberCount(const std::string& name) const;

    /**
     * @brief Clear all topics
     * @warning This will break all active connections
     */
    void clear();

    /**
     * @brief Get total number of topics
     */
    size_t getTopicCount() const;

    /**
     * @brief Get statistics for a topic
     * @param name Topic name
     * @return JSON object with topic statistics or null if not found
     */
    nlohmann::json getTopicStats(const std::string& name) const;

    /**
     * @brief Export all topics to JSON
     * @return JSON representation of all topics and their states
     */
    nlohmann::json exportToJson() const;

    // Delete copy and move constructors/operators
    TopicRegistry(const TopicRegistry&) = delete;
    TopicRegistry& operator=(const TopicRegistry&) = delete;
    TopicRegistry(TopicRegistry&&) = delete;
    TopicRegistry& operator=(TopicRegistry&&) = delete;

private:
    /**
     * @brief Private constructor for singleton
     */
    TopicRegistry() = default;

    /**
     * @brief Get topic by name (thread-safe)
     * @param name Topic name
     * @return Shared pointer to topic or nullptr if not found
     */
    std::shared_ptr<Topic> getTopic(const std::string& name) const;

    mutable std::mutex m_mutex;
    std::map<std::string, std::shared_ptr<Topic>> m_topics;
};

} // namespace Core
} // namespace VSE

#endif // VSE_CORE_TOPICREGISTRY_H

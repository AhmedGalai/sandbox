#include "registry/ComponentRegistry.h"
#include <algorithm>
#include <cctype>

namespace VSE {

ComponentRegistry& ComponentRegistry::instance() {
    static ComponentRegistry instance;
    return instance;
}

bool ComponentRegistry::registerComponent(const ComponentMetadata& metadata,
                                          ComponentFactory factory) {
    if (metadata.typeName.empty() || !factory) {
        return false;
    }

    std::lock_guard<std::mutex> lock(mutex_);

    ComponentRegistration registration;
    registration.metadata = metadata;
    registration.factory = factory;

    components_[metadata.typeName] = registration;
    return true;
}

bool ComponentRegistry::unregisterComponent(const std::string& typeName) {
    std::lock_guard<std::mutex> lock(mutex_);

    auto it = components_.find(typeName);
    if (it == components_.end()) {
        return false;
    }

    components_.erase(it);
    return true;
}

std::shared_ptr<Component> ComponentRegistry::createComponent(const std::string& typeName,
                                                              const nlohmann::json& parameters) {
    std::lock_guard<std::mutex> lock(mutex_);

    auto it = components_.find(typeName);
    if (it == components_.end()) {
        return nullptr; // Component type not found
    }

    try {
        return it->second.factory(parameters);
    } catch (const std::exception& e) {
        // Factory threw exception
        // Could log error here
        return nullptr;
    }
}

bool ComponentRegistry::isRegistered(const std::string& typeName) const {
    std::lock_guard<std::mutex> lock(mutex_);
    return components_.find(typeName) != components_.end();
}

const ComponentMetadata* ComponentRegistry::getMetadata(const std::string& typeName) const {
    std::lock_guard<std::mutex> lock(mutex_);

    auto it = components_.find(typeName);
    if (it == components_.end()) {
        return nullptr;
    }

    return &(it->second.metadata);
}

std::vector<std::string> ComponentRegistry::getAllTypes() const {
    std::lock_guard<std::mutex> lock(mutex_);

    std::vector<std::string> types;
    types.reserve(components_.size());

    for (const auto& pair : components_) {
        types.push_back(pair.first);
    }

    return types;
}

std::vector<std::string> ComponentRegistry::getComponentsByCategory(const std::string& category) const {
    std::lock_guard<std::mutex> lock(mutex_);

    std::vector<std::string> result;

    for (const auto& pair : components_) {
        if (pair.second.metadata.category == category) {
            result.push_back(pair.first);
        }
    }

    return result;
}

std::vector<std::string> ComponentRegistry::getAllCategories() const {
    std::lock_guard<std::mutex> lock(mutex_);

    std::vector<std::string> categories;

    for (const auto& pair : components_) {
        const std::string& category = pair.second.metadata.category;

        // Only add if not already in list
        if (std::find(categories.begin(), categories.end(), category) == categories.end()) {
            categories.push_back(category);
        }
    }

    // Sort alphabetically
    std::sort(categories.begin(), categories.end());

    return categories;
}

std::vector<std::string> ComponentRegistry::searchComponents(const std::string& query) const {
    if (query.empty()) {
        return getAllTypes();
    }

    std::lock_guard<std::mutex> lock(mutex_);

    // Convert query to lowercase for case-insensitive search
    std::string lowerQuery = query;
    std::transform(lowerQuery.begin(), lowerQuery.end(), lowerQuery.begin(),
                   [](unsigned char c) { return std::tolower(c); });

    std::vector<std::string> results;

    for (const auto& pair : components_) {
        const ComponentMetadata& meta = pair.second.metadata;

        // Helper to check if string contains query (case-insensitive)
        auto containsQuery = [&lowerQuery](const std::string& str) {
            std::string lowerStr = str;
            std::transform(lowerStr.begin(), lowerStr.end(), lowerStr.begin(),
                          [](unsigned char c) { return std::tolower(c); });
            return lowerStr.find(lowerQuery) != std::string::npos;
        };

        // Search in type name
        if (containsQuery(meta.typeName)) {
            results.push_back(pair.first);
            continue;
        }

        // Search in display name
        if (containsQuery(meta.displayName)) {
            results.push_back(pair.first);
            continue;
        }

        // Search in description
        if (containsQuery(meta.description)) {
            results.push_back(pair.first);
            continue;
        }

        // Search in tags
        bool foundInTags = false;
        for (const auto& tag : meta.tags) {
            if (containsQuery(tag)) {
                foundInTags = true;
                break;
            }
        }

        if (foundInTags) {
            results.push_back(pair.first);
        }
    }

    return results;
}

const ComponentRegistration* ComponentRegistry::getRegistration(const std::string& typeName) const {
    std::lock_guard<std::mutex> lock(mutex_);

    auto it = components_.find(typeName);
    if (it == components_.end()) {
        return nullptr;
    }

    return &(it->second);
}

void ComponentRegistry::clear() {
    std::lock_guard<std::mutex> lock(mutex_);
    components_.clear();
}

size_t ComponentRegistry::size() const {
    std::lock_guard<std::mutex> lock(mutex_);
    return components_.size();
}

} // namespace VSE

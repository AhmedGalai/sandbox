#ifndef VSE_COMPONENT_REGISTRY_H
#define VSE_COMPONENT_REGISTRY_H

#include <string>
#include <memory>
#include <functional>
#include <map>
#include <vector>
#include <mutex>
#include <nlohmann/json.hpp>

namespace VSE {

// Forward declaration
class Component;

/**
 * @brief Metadata describing a component type
 */
struct ComponentMetadata {
    std::string typeName;           ///< Unique type identifier
    std::string displayName;        ///< Human-readable name
    std::string category;           ///< Category for organization (e.g., "Logic", "Math", "I/O")
    std::string description;        ///< Brief description of functionality
    std::string iconPath;           ///< Path to icon resource
    std::vector<std::string> tags;  ///< Search tags
    int version = 1;                ///< Component version for compatibility
};

/**
 * @brief Factory function type for creating components
 *
 * Factory functions take component parameters as JSON and return a new component instance.
 */
using ComponentFactory = std::function<std::shared_ptr<Component>(const nlohmann::json&)>;

/**
 * @brief Registration entry combining metadata and factory
 */
struct ComponentRegistration {
    ComponentMetadata metadata;
    ComponentFactory factory;
};

/**
 * @brief Singleton registry for component types
 *
 * The ComponentRegistry manages all available component types in the VSE system.
 * It provides component instantiation, metadata queries, and auto-registration support.
 *
 * Features:
 * - Singleton pattern for global access
 * - Thread-safe registration and queries
 * - Factory pattern for component creation
 * - Category-based organization
 * - Auto-registration via static initializers
 * - Component palette support
 *
 * Usage:
 * @code
 * // Register a component type
 * ComponentRegistry::instance().registerComponent(
 *     metadata,
 *     [](const nlohmann::json& params) {
 *         return std::make_shared<MyComponent>(params);
 *     }
 * );
 *
 * // Create a component instance
 * auto component = ComponentRegistry::instance().createComponent("MyComponent", params);
 *
 * // Query components by category
 * auto mathComponents = ComponentRegistry::instance().getComponentsByCategory("Math");
 * @endcode
 *
 * Auto-registration:
 * @code
 * // In a component's .cpp file
 * static ComponentRegistrar<MyComponent> myComponentRegistrar(
 *     "MyComponent",
 *     "My Component",
 *     "Category",
 *     "Description"
 * );
 * @endcode
 */
class ComponentRegistry {
public:
    /**
     * @brief Get the singleton instance
     *
     * @return ComponentRegistry& The global registry instance
     */
    static ComponentRegistry& instance();

    /**
     * @brief Register a new component type
     *
     * Registers a component type with its metadata and factory function.
     * If a component with the same type name already exists, it will be replaced.
     *
     * @param metadata Component metadata (type name, category, etc.)
     * @param factory Factory function to create component instances
     * @return true if registration succeeded
     * @return false if registration failed (e.g., empty type name)
     *
     * @code
     * ComponentMetadata meta;
     * meta.typeName = "AndGate";
     * meta.displayName = "AND Gate";
     * meta.category = "Logic";
     * meta.description = "Logical AND operation";
     * meta.iconPath = ":/icons/logic/and.png";
     *
     * ComponentRegistry::instance().registerComponent(
     *     meta,
     *     [](const nlohmann::json& params) {
     *         return std::make_shared<AndGate>(params);
     *     }
     * );
     * @endcode
     */
    bool registerComponent(const ComponentMetadata& metadata,
                          ComponentFactory factory);

    /**
     * @brief Unregister a component type
     *
     * Removes a component type from the registry.
     *
     * @param typeName Type name to unregister
     * @return true if component was found and removed
     * @return false if component type was not registered
     */
    bool unregisterComponent(const std::string& typeName);

    /**
     * @brief Create a new component instance
     *
     * Instantiates a component of the specified type using its registered factory.
     *
     * @param typeName Type name of the component to create
     * @param parameters Component-specific parameters (JSON)
     * @return std::shared_ptr<Component> New component instance, or nullptr if type not found
     *
     * @code
     * nlohmann::json params;
     * params["initialValue"] = 42;
     * auto component = ComponentRegistry::instance().createComponent("Constant", params);
     * if (component) {
     *     // Use component
     * } else {
     *     // Type not found
     * }
     * @endcode
     */
    std::shared_ptr<Component> createComponent(const std::string& typeName,
                                               const nlohmann::json& parameters = {});

    /**
     * @brief Check if a component type is registered
     *
     * @param typeName Type name to check
     * @return true if type is registered
     * @return false if type is not registered
     */
    bool isRegistered(const std::string& typeName) const;

    /**
     * @brief Get metadata for a component type
     *
     * @param typeName Type name to query
     * @return const ComponentMetadata* Pointer to metadata, or nullptr if not found
     */
    const ComponentMetadata* getMetadata(const std::string& typeName) const;

    /**
     * @brief Get all registered component types
     *
     * @return std::vector<std::string> List of all registered type names
     */
    std::vector<std::string> getAllTypes() const;

    /**
     * @brief Get all components in a specific category
     *
     * @param category Category name (e.g., "Logic", "Math", "I/O")
     * @return std::vector<std::string> List of type names in the category
     *
     * @code
     * auto logicComponents = ComponentRegistry::instance().getComponentsByCategory("Logic");
     * for (const auto& typeName : logicComponents) {
     *     auto meta = ComponentRegistry::instance().getMetadata(typeName);
     *     // Display in component palette
     * }
     * @endcode
     */
    std::vector<std::string> getComponentsByCategory(const std::string& category) const;

    /**
     * @brief Get all unique categories
     *
     * @return std::vector<std::string> List of all registered categories
     */
    std::vector<std::string> getAllCategories() const;

    /**
     * @brief Search components by name or tags
     *
     * Performs case-insensitive search in type names, display names, and tags.
     *
     * @param query Search query string
     * @return std::vector<std::string> List of matching type names
     *
     * @code
     * auto results = ComponentRegistry::instance().searchComponents("gate");
     * // Returns: ["AndGate", "OrGate", "NotGate", ...]
     * @endcode
     */
    std::vector<std::string> searchComponents(const std::string& query) const;

    /**
     * @brief Get complete registration for a component type
     *
     * Returns both metadata and factory for advanced use cases.
     *
     * @param typeName Type name to query
     * @return const ComponentRegistration* Pointer to registration, or nullptr if not found
     */
    const ComponentRegistration* getRegistration(const std::string& typeName) const;

    /**
     * @brief Clear all registered components
     *
     * Primarily used for testing. Use with caution.
     */
    void clear();

    /**
     * @brief Get number of registered components
     *
     * @return size_t Count of registered component types
     */
    size_t size() const;

private:
    // Private constructor for singleton
    ComponentRegistry() = default;

    // Delete copy constructor and assignment
    ComponentRegistry(const ComponentRegistry&) = delete;
    ComponentRegistry& operator=(const ComponentRegistry&) = delete;

    // Component registry storage
    std::map<std::string, ComponentRegistration> components_;

    // Thread safety
    mutable std::mutex mutex_;
};

/**
 * @brief Helper class for auto-registration of component types
 *
 * Create a static instance of this class to automatically register
 * a component type when the program starts.
 *
 * @tparam T Component class type
 *
 * Example usage:
 * @code
 * // In MyComponent.cpp
 * #include "registry/ComponentRegistry.h"
 * #include "components/MyComponent.h"
 *
 * namespace {
 *     static VSE::ComponentRegistrar<MyComponent> registrar(
 *         "MyComponent",           // typeName
 *         "My Component",          // displayName
 *         "Custom",                // category
 *         "Does something cool",   // description
 *         ":/icons/my_icon.png",   // iconPath
 *         {"custom", "example"}    // tags
 *     );
 * }
 * @endcode
 */
template<typename T>
class ComponentRegistrar {
public:
    /**
     * @brief Construct and auto-register a component type
     *
     * @param typeName Unique type identifier
     * @param displayName Human-readable name
     * @param category Component category
     * @param description Brief description
     * @param iconPath Path to icon resource (optional)
     * @param tags Search tags (optional)
     * @param version Component version (optional)
     */
    ComponentRegistrar(const std::string& typeName,
                      const std::string& displayName,
                      const std::string& category,
                      const std::string& description,
                      const std::string& iconPath = "",
                      const std::vector<std::string>& tags = {},
                      int version = 1) {
        ComponentMetadata metadata;
        metadata.typeName = typeName;
        metadata.displayName = displayName;
        metadata.category = category;
        metadata.description = description;
        metadata.iconPath = iconPath;
        metadata.tags = tags;
        metadata.version = version;

        ComponentRegistry::instance().registerComponent(
            metadata,
            [](const nlohmann::json& params) -> std::shared_ptr<Component> {
                return std::make_shared<T>(params);
            }
        );
    }
};

/**
 * @brief Macro for convenient component registration
 *
 * Usage:
 * @code
 * REGISTER_COMPONENT(MyComponent, "My Component", "Category", "Description")
 * @endcode
 */
#define REGISTER_COMPONENT(CLASS, DISPLAY_NAME, CATEGORY, DESCRIPTION) \
    static VSE::ComponentRegistrar<CLASS> _registrar_##CLASS( \
        #CLASS, DISPLAY_NAME, CATEGORY, DESCRIPTION)

/**
 * @brief Macro for component registration with full metadata
 *
 * Usage:
 * @code
 * REGISTER_COMPONENT_EX(MyComponent, "My Component", "Category", "Description",
 *                       ":/icons/my.png", {"tag1", "tag2"}, 1)
 * @endcode
 */
#define REGISTER_COMPONENT_EX(CLASS, DISPLAY_NAME, CATEGORY, DESCRIPTION, ICON, TAGS, VERSION) \
    static VSE::ComponentRegistrar<CLASS> _registrar_##CLASS( \
        #CLASS, DISPLAY_NAME, CATEGORY, DESCRIPTION, ICON, TAGS, VERSION)

} // namespace VSE

#endif // VSE_COMPONENT_REGISTRY_H

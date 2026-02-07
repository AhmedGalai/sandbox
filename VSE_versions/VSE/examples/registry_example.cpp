/**
 * @file registry_example.cpp
 * @brief Example demonstrating VSE Component Registry usage
 *
 * This example shows how to:
 * - Register component types
 * - Create components from the registry
 * - Query components by category
 * - Search components
 * - Use auto-registration
 */

#include "registry/ComponentRegistry.h"
#include <iostream>
#include <memory>

// Mock Component base class for demonstration
// (In real VSE, this would be the actual Component class)
namespace VSE {
class Component {
public:
    virtual ~Component() = default;
    virtual std::string getType() const = 0;
    virtual void process() = 0;
};
}

// Example component implementations
class AndGate : public VSE::Component {
public:
    explicit AndGate(const nlohmann::json& params) {
        inputCount_ = params.value("inputCount", 2);
    }

    std::string getType() const override { return "AndGate"; }

    void process() override {
        std::cout << "AndGate processing with " << inputCount_ << " inputs" << std::endl;
    }

private:
    int inputCount_;
};

class OrGate : public VSE::Component {
public:
    explicit OrGate(const nlohmann::json& params) {
        inputCount_ = params.value("inputCount", 2);
    }

    std::string getType() const override { return "OrGate"; }

    void process() override {
        std::cout << "OrGate processing with " << inputCount_ << " inputs" << std::endl;
    }

private:
    int inputCount_;
};

class NotGate : public VSE::Component {
public:
    explicit NotGate(const nlohmann::json&) {}

    std::string getType() const override { return "NotGate"; }

    void process() override {
        std::cout << "NotGate processing" << std::endl;
    }
};

class AddNode : public VSE::Component {
public:
    explicit AddNode(const nlohmann::json&) {}

    std::string getType() const override { return "AddNode"; }

    void process() override {
        std::cout << "AddNode processing" << std::endl;
    }
};

// Auto-registration examples
namespace {
    static VSE::ComponentRegistrar<AndGate> andGateReg(
        "AndGate",
        "AND Gate",
        "Logic",
        "Logical AND operation on multiple inputs",
        ":/icons/logic/and.png",
        {"logic", "gate", "boolean"}
    );

    static VSE::ComponentRegistrar<OrGate> orGateReg(
        "OrGate",
        "OR Gate",
        "Logic",
        "Logical OR operation on multiple inputs",
        ":/icons/logic/or.png",
        {"logic", "gate", "boolean"}
    );

    static VSE::ComponentRegistrar<NotGate> notGateReg(
        "NotGate",
        "NOT Gate",
        "Logic",
        "Logical NOT operation (inverter)",
        ":/icons/logic/not.png",
        {"logic", "gate", "boolean", "inverter"}
    );

    static VSE::ComponentRegistrar<AddNode> addNodeReg(
        "AddNode",
        "Add",
        "Math",
        "Addition operation",
        ":/icons/math/add.png",
        {"math", "arithmetic", "add"}
    );
}

void printSeparator() {
    std::cout << std::string(60, '=') << std::endl;
}

void example1_ManualRegistration() {
    printSeparator();
    std::cout << "Example 1: Manual Component Registration" << std::endl;
    printSeparator();

    VSE::ComponentMetadata metadata;
    metadata.typeName = "CustomComponent";
    metadata.displayName = "Custom Component";
    metadata.category = "Custom";
    metadata.description = "A manually registered component";
    metadata.iconPath = ":/icons/custom.png";
    metadata.tags = {"custom", "example"};

    bool success = VSE::ComponentRegistry::instance().registerComponent(
        metadata,
        [](const nlohmann::json& params) -> std::shared_ptr<VSE::Component> {
            // Factory function
            return std::make_shared<AndGate>(params);  // Just for demo
        }
    );

    std::cout << "Registration "
              << (success ? "succeeded" : "failed") << std::endl;
    std::cout << std::endl;
}

void example2_CreateComponents() {
    printSeparator();
    std::cout << "Example 2: Creating Components" << std::endl;
    printSeparator();

    auto& registry = VSE::ComponentRegistry::instance();

    // Create an AND gate with parameters
    nlohmann::json params;
    params["inputCount"] = 3;

    auto andGate = registry.createComponent("AndGate", params);
    if (andGate) {
        std::cout << "Created: " << andGate->getType() << std::endl;
        andGate->process();
    } else {
        std::cout << "Failed to create AndGate" << std::endl;
    }

    // Create an OR gate
    auto orGate = registry.createComponent("OrGate");
    if (orGate) {
        std::cout << "Created: " << orGate->getType() << std::endl;
        orGate->process();
    }

    // Try to create non-existent component
    auto unknown = registry.createComponent("UnknownComponent");
    if (!unknown) {
        std::cout << "Unknown component type correctly returned nullptr" << std::endl;
    }

    std::cout << std::endl;
}

void example3_QueryByCategory() {
    printSeparator();
    std::cout << "Example 3: Query Components by Category" << std::endl;
    printSeparator();

    auto& registry = VSE::ComponentRegistry::instance();

    // Get all categories
    auto categories = registry.getAllCategories();
    std::cout << "Available categories:" << std::endl;
    for (const auto& category : categories) {
        std::cout << "  - " << category << std::endl;
    }
    std::cout << std::endl;

    // Get components in Logic category
    auto logicComponents = registry.getComponentsByCategory("Logic");
    std::cout << "Logic components (" << logicComponents.size() << "):" << std::endl;
    for (const auto& typeName : logicComponents) {
        auto* meta = registry.getMetadata(typeName);
        if (meta) {
            std::cout << "  - " << meta->displayName
                      << " (" << typeName << ")" << std::endl;
            std::cout << "    " << meta->description << std::endl;
        }
    }
    std::cout << std::endl;

    // Get components in Math category
    auto mathComponents = registry.getComponentsByCategory("Math");
    std::cout << "Math components (" << mathComponents.size() << "):" << std::endl;
    for (const auto& typeName : mathComponents) {
        auto* meta = registry.getMetadata(typeName);
        if (meta) {
            std::cout << "  - " << meta->displayName
                      << " (" << typeName << ")" << std::endl;
        }
    }
    std::cout << std::endl;
}

void example4_SearchComponents() {
    printSeparator();
    std::cout << "Example 4: Search Components" << std::endl;
    printSeparator();

    auto& registry = VSE::ComponentRegistry::instance();

    // Search for "gate"
    std::cout << "Search results for 'gate':" << std::endl;
    auto results1 = registry.searchComponents("gate");
    for (const auto& typeName : results1) {
        auto* meta = registry.getMetadata(typeName);
        if (meta) {
            std::cout << "  - " << meta->displayName << std::endl;
        }
    }
    std::cout << std::endl;

    // Search for "math"
    std::cout << "Search results for 'math':" << std::endl;
    auto results2 = registry.searchComponents("math");
    for (const auto& typeName : results2) {
        auto* meta = registry.getMetadata(typeName);
        if (meta) {
            std::cout << "  - " << meta->displayName << std::endl;
        }
    }
    std::cout << std::endl;

    // Search for "inverter" (tag search)
    std::cout << "Search results for 'inverter':" << std::endl;
    auto results3 = registry.searchComponents("inverter");
    for (const auto& typeName : results3) {
        auto* meta = registry.getMetadata(typeName);
        if (meta) {
            std::cout << "  - " << meta->displayName << std::endl;
        }
    }
    std::cout << std::endl;
}

void example5_ComponentMetadata() {
    printSeparator();
    std::cout << "Example 5: Accessing Component Metadata" << std::endl;
    printSeparator();

    auto& registry = VSE::ComponentRegistry::instance();

    const auto* meta = registry.getMetadata("AndGate");
    if (meta) {
        std::cout << "AndGate Metadata:" << std::endl;
        std::cout << "  Type Name: " << meta->typeName << std::endl;
        std::cout << "  Display Name: " << meta->displayName << std::endl;
        std::cout << "  Category: " << meta->category << std::endl;
        std::cout << "  Description: " << meta->description << std::endl;
        std::cout << "  Icon Path: " << meta->iconPath << std::endl;
        std::cout << "  Version: " << meta->version << std::endl;
        std::cout << "  Tags: ";
        for (size_t i = 0; i < meta->tags.size(); ++i) {
            std::cout << meta->tags[i];
            if (i < meta->tags.size() - 1) std::cout << ", ";
        }
        std::cout << std::endl;
    }

    std::cout << std::endl;
}

void example6_RegistryStats() {
    printSeparator();
    std::cout << "Example 6: Registry Statistics" << std::endl;
    printSeparator();

    auto& registry = VSE::ComponentRegistry::instance();

    std::cout << "Total registered components: " << registry.size() << std::endl;
    std::cout << "Total categories: " << registry.getAllCategories().size() << std::endl;
    std::cout << std::endl;

    std::cout << "All registered types:" << std::endl;
    auto allTypes = registry.getAllTypes();
    for (const auto& typeName : allTypes) {
        std::cout << "  - " << typeName << std::endl;
    }

    std::cout << std::endl;
}

int main() {
    std::cout << std::endl;
    std::cout << "VSE Component Registry Examples" << std::endl;
    std::cout << std::endl;

    // Note: Auto-registration happens before main() via static initializers

    example1_ManualRegistration();
    example2_CreateComponents();
    example3_QueryByCategory();
    example4_SearchComponents();
    example5_ComponentMetadata();
    example6_RegistryStats();

    printSeparator();
    std::cout << "All examples completed!" << std::endl;
    printSeparator();

    return 0;
}

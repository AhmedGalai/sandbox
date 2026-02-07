/**
 * @file test_registry.cpp
 * @brief Unit tests for ComponentRegistry
 */

#include "registry/ComponentRegistry.h"
#include <gtest/gtest.h>

// Mock Component class for testing
namespace VSE {
class Component {
public:
    virtual ~Component() = default;
    virtual std::string getType() const = 0;
};
}

// Test component types
class TestComponentA : public VSE::Component {
public:
    explicit TestComponentA(const nlohmann::json& params) {
        value_ = params.value("value", 0);
    }

    std::string getType() const override { return "TestComponentA"; }

    int getValue() const { return value_; }

private:
    int value_;
};

class TestComponentB : public VSE::Component {
public:
    explicit TestComponentB(const nlohmann::json&) {}

    std::string getType() const override { return "TestComponentB"; }
};

class ComponentRegistryTest : public ::testing::Test {
protected:
    void SetUp() override {
        // Clear registry before each test
        VSE::ComponentRegistry::instance().clear();
    }

    void TearDown() override {
        // Clean up after each test
        VSE::ComponentRegistry::instance().clear();
    }

    VSE::ComponentMetadata createTestMetadata(const std::string& typeName,
                                              const std::string& category = "Test") {
        VSE::ComponentMetadata meta;
        meta.typeName = typeName;
        meta.displayName = typeName + " Display";
        meta.category = category;
        meta.description = "Test component";
        meta.iconPath = ":/icons/test.png";
        meta.tags = {"test", "example"};
        return meta;
    }
};

TEST_F(ComponentRegistryTest, Singleton) {
    auto& instance1 = VSE::ComponentRegistry::instance();
    auto& instance2 = VSE::ComponentRegistry::instance();
    EXPECT_EQ(&instance1, &instance2);
}

TEST_F(ComponentRegistryTest, RegisterComponent) {
    auto& registry = VSE::ComponentRegistry::instance();
    auto meta = createTestMetadata("TestA");

    bool result = registry.registerComponent(
        meta,
        [](const nlohmann::json& params) -> std::shared_ptr<VSE::Component> {
            return std::make_shared<TestComponentA>(params);
        }
    );

    EXPECT_TRUE(result);
    EXPECT_TRUE(registry.isRegistered("TestA"));
    EXPECT_EQ(registry.size(), 1);
}

TEST_F(ComponentRegistryTest, RegisterEmptyTypeName) {
    auto& registry = VSE::ComponentRegistry::instance();
    auto meta = createTestMetadata("");

    bool result = registry.registerComponent(
        meta,
        [](const nlohmann::json& params) -> std::shared_ptr<VSE::Component> {
            return std::make_shared<TestComponentA>(params);
        }
    );

    EXPECT_FALSE(result);
}

TEST_F(ComponentRegistryTest, RegisterMultipleComponents) {
    auto& registry = VSE::ComponentRegistry::instance();

    auto metaA = createTestMetadata("TestA");
    auto metaB = createTestMetadata("TestB");

    registry.registerComponent(
        metaA,
        [](const nlohmann::json& p) { return std::make_shared<TestComponentA>(p); }
    );

    registry.registerComponent(
        metaB,
        [](const nlohmann::json& p) { return std::make_shared<TestComponentB>(p); }
    );

    EXPECT_EQ(registry.size(), 2);
    EXPECT_TRUE(registry.isRegistered("TestA"));
    EXPECT_TRUE(registry.isRegistered("TestB"));
}

TEST_F(ComponentRegistryTest, UnregisterComponent) {
    auto& registry = VSE::ComponentRegistry::instance();
    auto meta = createTestMetadata("TestA");

    registry.registerComponent(
        meta,
        [](const nlohmann::json& p) { return std::make_shared<TestComponentA>(p); }
    );

    EXPECT_TRUE(registry.isRegistered("TestA"));

    bool result = registry.unregisterComponent("TestA");
    EXPECT_TRUE(result);
    EXPECT_FALSE(registry.isRegistered("TestA"));
    EXPECT_EQ(registry.size(), 0);
}

TEST_F(ComponentRegistryTest, UnregisterNonExistent) {
    auto& registry = VSE::ComponentRegistry::instance();
    bool result = registry.unregisterComponent("NonExistent");
    EXPECT_FALSE(result);
}

TEST_F(ComponentRegistryTest, CreateComponent) {
    auto& registry = VSE::ComponentRegistry::instance();
    auto meta = createTestMetadata("TestA");

    registry.registerComponent(
        meta,
        [](const nlohmann::json& p) { return std::make_shared<TestComponentA>(p); }
    );

    nlohmann::json params;
    params["value"] = 42;

    auto component = registry.createComponent("TestA", params);
    ASSERT_NE(component, nullptr);
    EXPECT_EQ(component->getType(), "TestComponentA");

    auto* testComp = dynamic_cast<TestComponentA*>(component.get());
    ASSERT_NE(testComp, nullptr);
    EXPECT_EQ(testComp->getValue(), 42);
}

TEST_F(ComponentRegistryTest, CreateNonExistentComponent) {
    auto& registry = VSE::ComponentRegistry::instance();
    auto component = registry.createComponent("NonExistent");
    EXPECT_EQ(component, nullptr);
}

TEST_F(ComponentRegistryTest, GetMetadata) {
    auto& registry = VSE::ComponentRegistry::instance();
    auto meta = createTestMetadata("TestA", "Logic");
    meta.description = "Custom description";

    registry.registerComponent(
        meta,
        [](const nlohmann::json& p) { return std::make_shared<TestComponentA>(p); }
    );

    const auto* retrieved = registry.getMetadata("TestA");
    ASSERT_NE(retrieved, nullptr);
    EXPECT_EQ(retrieved->typeName, "TestA");
    EXPECT_EQ(retrieved->displayName, "TestA Display");
    EXPECT_EQ(retrieved->category, "Logic");
    EXPECT_EQ(retrieved->description, "Custom description");
}

TEST_F(ComponentRegistryTest, GetNonExistentMetadata) {
    auto& registry = VSE::ComponentRegistry::instance();
    const auto* meta = registry.getMetadata("NonExistent");
    EXPECT_EQ(meta, nullptr);
}

TEST_F(ComponentRegistryTest, GetAllTypes) {
    auto& registry = VSE::ComponentRegistry::instance();

    registry.registerComponent(
        createTestMetadata("TypeA"),
        [](const nlohmann::json& p) { return std::make_shared<TestComponentA>(p); }
    );

    registry.registerComponent(
        createTestMetadata("TypeB"),
        [](const nlohmann::json& p) { return std::make_shared<TestComponentB>(p); }
    );

    auto types = registry.getAllTypes();
    EXPECT_EQ(types.size(), 2);
    EXPECT_TRUE(std::find(types.begin(), types.end(), "TypeA") != types.end());
    EXPECT_TRUE(std::find(types.begin(), types.end(), "TypeB") != types.end());
}

TEST_F(ComponentRegistryTest, GetComponentsByCategory) {
    auto& registry = VSE::ComponentRegistry::instance();

    registry.registerComponent(
        createTestMetadata("LogicA", "Logic"),
        [](const nlohmann::json& p) { return std::make_shared<TestComponentA>(p); }
    );

    registry.registerComponent(
        createTestMetadata("LogicB", "Logic"),
        [](const nlohmann::json& p) { return std::make_shared<TestComponentB>(p); }
    );

    registry.registerComponent(
        createTestMetadata("MathA", "Math"),
        [](const nlohmann::json& p) { return std::make_shared<TestComponentA>(p); }
    );

    auto logicComps = registry.getComponentsByCategory("Logic");
    EXPECT_EQ(logicComps.size(), 2);

    auto mathComps = registry.getComponentsByCategory("Math");
    EXPECT_EQ(mathComps.size(), 1);

    auto emptyComps = registry.getComponentsByCategory("NonExistent");
    EXPECT_EQ(emptyComps.size(), 0);
}

TEST_F(ComponentRegistryTest, GetAllCategories) {
    auto& registry = VSE::ComponentRegistry::instance();

    registry.registerComponent(
        createTestMetadata("LogicA", "Logic"),
        [](const nlohmann::json& p) { return std::make_shared<TestComponentA>(p); }
    );

    registry.registerComponent(
        createTestMetadata("MathA", "Math"),
        [](const nlohmann::json& p) { return std::make_shared<TestComponentA>(p); }
    );

    registry.registerComponent(
        createTestMetadata("IOA", "I/O"),
        [](const nlohmann::json& p) { return std::make_shared<TestComponentA>(p); }
    );

    auto categories = registry.getAllCategories();
    EXPECT_EQ(categories.size(), 3);
    EXPECT_TRUE(std::find(categories.begin(), categories.end(), "Logic") != categories.end());
    EXPECT_TRUE(std::find(categories.begin(), categories.end(), "Math") != categories.end());
    EXPECT_TRUE(std::find(categories.begin(), categories.end(), "I/O") != categories.end());
}

TEST_F(ComponentRegistryTest, SearchComponents) {
    auto& registry = VSE::ComponentRegistry::instance();

    auto metaGate = createTestMetadata("AndGate", "Logic");
    metaGate.displayName = "AND Gate";
    metaGate.tags = {"logic", "gate", "boolean"};

    auto metaAdd = createTestMetadata("AddNode", "Math");
    metaAdd.displayName = "Add";
    metaAdd.tags = {"math", "arithmetic"};

    registry.registerComponent(
        metaGate,
        [](const nlohmann::json& p) { return std::make_shared<TestComponentA>(p); }
    );

    registry.registerComponent(
        metaAdd,
        [](const nlohmann::json& p) { return std::make_shared<TestComponentA>(p); }
    );

    // Search by type name
    auto results1 = registry.searchComponents("gate");
    EXPECT_EQ(results1.size(), 1);
    EXPECT_EQ(results1[0], "AndGate");

    // Search by tag
    auto results2 = registry.searchComponents("arithmetic");
    EXPECT_EQ(results2.size(), 1);
    EXPECT_EQ(results2[0], "AddNode");

    // Search by display name
    auto results3 = registry.searchComponents("ADD");  // Case-insensitive
    EXPECT_EQ(results3.size(), 1);
}

TEST_F(ComponentRegistryTest, SearchEmptyQuery) {
    auto& registry = VSE::ComponentRegistry::instance();

    registry.registerComponent(
        createTestMetadata("TestA"),
        [](const nlohmann::json& p) { return std::make_shared<TestComponentA>(p); }
    );

    registry.registerComponent(
        createTestMetadata("TestB"),
        [](const nlohmann::json& p) { return std::make_shared<TestComponentB>(p); }
    );

    auto results = registry.searchComponents("");
    EXPECT_EQ(results.size(), 2);  // Empty query returns all
}

TEST_F(ComponentRegistryTest, Clear) {
    auto& registry = VSE::ComponentRegistry::instance();

    registry.registerComponent(
        createTestMetadata("TestA"),
        [](const nlohmann::json& p) { return std::make_shared<TestComponentA>(p); }
    );

    registry.registerComponent(
        createTestMetadata("TestB"),
        [](const nlohmann::json& p) { return std::make_shared<TestComponentB>(p); }
    );

    EXPECT_EQ(registry.size(), 2);

    registry.clear();

    EXPECT_EQ(registry.size(), 0);
    EXPECT_FALSE(registry.isRegistered("TestA"));
    EXPECT_FALSE(registry.isRegistered("TestB"));
}

TEST_F(ComponentRegistryTest, AutoRegistration) {
    // Test the ComponentRegistrar template
    auto& registry = VSE::ComponentRegistry::instance();

    {
        VSE::ComponentRegistrar<TestComponentA> registrar(
            "AutoComponent",
            "Auto Component",
            "Test",
            "Auto-registered component"
        );

        EXPECT_TRUE(registry.isRegistered("AutoComponent"));
        const auto* meta = registry.getMetadata("AutoComponent");
        ASSERT_NE(meta, nullptr);
        EXPECT_EQ(meta->displayName, "Auto Component");
    }

    // Component should still be registered after registrar goes out of scope
    EXPECT_TRUE(registry.isRegistered("AutoComponent"));
}

int main(int argc, char** argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}

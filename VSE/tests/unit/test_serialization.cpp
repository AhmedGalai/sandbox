/**
 * @file test_serialization.cpp
 * @brief Unit tests for ProjectSerializer
 */

#include "serialization/ProjectSerializer.h"
#include <gtest/gtest.h>
#include <fstream>
#include <filesystem>

namespace fs = std::filesystem;

class ProjectSerializerTest : public ::testing::Test {
protected:
    void SetUp() override {
        // Create temp directory for test files
        testDir_ = fs::temp_directory_path() / "vse_test";
        fs::create_directories(testDir_);
    }

    void TearDown() override {
        // Clean up test files
        if (fs::exists(testDir_)) {
            fs::remove_all(testDir_);
        }
    }

    fs::path getTestFilePath(const std::string& filename) {
        return testDir_ / filename;
    }

    VSE::ProjectData createSampleProject() {
        VSE::ProjectData project;
        project.version = "1.0";
        project.metadata.name = "Test Project";
        project.metadata.created = "2025-11-26T12:00:00Z";
        project.metadata.modified = "2025-11-26T12:00:00Z";
        project.metadata.description = "Test description";
        project.metadata.author = "Test Author";

        project.canvas.zoom = 1.5;
        project.canvas.panX = 100.0;
        project.canvas.panY = 200.0;

        VSE::ComponentData comp;
        comp.id = "comp-001";
        comp.type = "TestComponent";
        comp.posX = 10.0;
        comp.posY = 20.0;
        comp.parameters = {{"value", 42}};
        project.components.push_back(comp);

        VSE::ConnectionData conn;
        conn.id = "conn-001";
        conn.sourceComponentId = "comp-001";
        conn.sourcePinName = "output";
        conn.destinationComponentId = "comp-002";
        conn.destinationPinName = "input";
        conn.topic = "/test/topic";
        project.connections.push_back(conn);

        return project;
    }

    fs::path testDir_;
};

TEST_F(ProjectSerializerTest, SaveAndLoadProject) {
    VSE::ProjectSerializer serializer;
    VSE::ProjectData original = createSampleProject();

    // Save project
    auto filePath = getTestFilePath("test.vse").string();
    auto saveResult = serializer.saveProject(filePath, original);
    ASSERT_TRUE(saveResult.success) << saveResult.error;

    // Verify file exists
    ASSERT_TRUE(fs::exists(filePath));

    // Load project
    auto loadResult = serializer.loadProject(filePath);
    ASSERT_TRUE(loadResult.success) << loadResult.error;

    // Verify data matches
    const VSE::ProjectData& loaded = loadResult.data;
    EXPECT_EQ(loaded.version, original.version);
    EXPECT_EQ(loaded.metadata.name, original.metadata.name);
    EXPECT_EQ(loaded.metadata.description, original.metadata.description);
    EXPECT_EQ(loaded.metadata.author, original.metadata.author);
    EXPECT_DOUBLE_EQ(loaded.canvas.zoom, original.canvas.zoom);
    EXPECT_DOUBLE_EQ(loaded.canvas.panX, original.canvas.panX);
    EXPECT_DOUBLE_EQ(loaded.canvas.panY, original.canvas.panY);
    EXPECT_EQ(loaded.components.size(), original.components.size());
    EXPECT_EQ(loaded.connections.size(), original.connections.size());

    if (!loaded.components.empty()) {
        EXPECT_EQ(loaded.components[0].id, original.components[0].id);
        EXPECT_EQ(loaded.components[0].type, original.components[0].type);
        EXPECT_DOUBLE_EQ(loaded.components[0].posX, original.components[0].posX);
        EXPECT_DOUBLE_EQ(loaded.components[0].posY, original.components[0].posY);
    }

    if (!loaded.connections.empty()) {
        EXPECT_EQ(loaded.connections[0].id, original.connections[0].id);
        EXPECT_EQ(loaded.connections[0].topic, original.connections[0].topic);
    }
}

TEST_F(ProjectSerializerTest, LoadNonExistentFile) {
    VSE::ProjectSerializer serializer;
    auto result = serializer.loadProject("/nonexistent/path/file.vse");
    EXPECT_FALSE(result.success);
    EXPECT_FALSE(result.error.empty());
}

TEST_F(ProjectSerializerTest, LoadInvalidJson) {
    VSE::ProjectSerializer serializer;

    // Create file with invalid JSON
    auto filePath = getTestFilePath("invalid.vse").string();
    std::ofstream file(filePath);
    file << "{ invalid json content }";
    file.close();

    auto result = serializer.loadProject(filePath);
    EXPECT_FALSE(result.success);
    EXPECT_FALSE(result.error.empty());
}

TEST_F(ProjectSerializerTest, LoadIncompleteProject) {
    VSE::ProjectSerializer serializer;

    // Create file with incomplete project structure
    auto filePath = getTestFilePath("incomplete.vse").string();
    std::ofstream file(filePath);
    file << R"({
        "version": "1.0",
        "metadata": {
            "name": "Test"
        }
    })";
    file.close();

    auto result = serializer.loadProject(filePath);
    EXPECT_FALSE(result.success);
}

TEST_F(ProjectSerializerTest, ExportAndImportJson) {
    VSE::ProjectSerializer serializer;
    VSE::ProjectData original = createSampleProject();

    // Export to JSON string
    auto exportResult = serializer.exportToJson(original, true);
    ASSERT_TRUE(exportResult.success) << exportResult.error;
    EXPECT_FALSE(exportResult.data.empty());

    // Import from JSON string
    auto importResult = serializer.importFromJson(exportResult.data);
    ASSERT_TRUE(importResult.success) << importResult.error;

    // Verify data matches
    const VSE::ProjectData& imported = importResult.data;
    EXPECT_EQ(imported.metadata.name, original.metadata.name);
    EXPECT_EQ(imported.components.size(), original.components.size());
    EXPECT_EQ(imported.connections.size(), original.connections.size());
}

TEST_F(ProjectSerializerTest, ValidateValidProject) {
    VSE::ProjectSerializer serializer;
    VSE::ProjectData project = createSampleProject();

    auto exportResult = serializer.exportToJson(project);
    ASSERT_TRUE(exportResult.success);

    nlohmann::json json = nlohmann::json::parse(exportResult.data);
    auto validationResult = serializer.validateProjectJson(json);
    EXPECT_TRUE(validationResult.success) << validationResult.error;
}

TEST_F(ProjectSerializerTest, ValidateInvalidProject) {
    VSE::ProjectSerializer serializer;

    nlohmann::json json = {
        {"version", "1.0"},
        {"metadata", {{"name", "Test"}}}
        // Missing canvas, components, connections
    };

    auto validationResult = serializer.validateProjectJson(json);
    EXPECT_FALSE(validationResult.success);
}

TEST_F(ProjectSerializerTest, EmptyProject) {
    VSE::ProjectSerializer serializer;
    VSE::ProjectData project;
    project.metadata.name = "Empty Project";
    project.metadata.created = "2025-11-26T12:00:00Z";
    project.metadata.modified = "2025-11-26T12:00:00Z";

    // Save and load empty project
    auto filePath = getTestFilePath("empty.vse").string();
    auto saveResult = serializer.saveProject(filePath, project);
    ASSERT_TRUE(saveResult.success);

    auto loadResult = serializer.loadProject(filePath);
    ASSERT_TRUE(loadResult.success);

    EXPECT_EQ(loadResult.data.components.size(), 0);
    EXPECT_EQ(loadResult.data.connections.size(), 0);
}

TEST_F(ProjectSerializerTest, ComplexParameters) {
    VSE::ProjectSerializer serializer;
    VSE::ProjectData project = createSampleProject();

    // Add component with complex parameters
    VSE::ComponentData comp;
    comp.id = "comp-complex";
    comp.type = "ComplexComponent";
    comp.parameters = {
        {"string", "value"},
        {"number", 123},
        {"float", 3.14},
        {"bool", true},
        {"array", {1, 2, 3}},
        {"nested", {
            {"inner", "value"},
            {"count", 5}
        }}
    };
    project.components.push_back(comp);

    // Save and load
    auto filePath = getTestFilePath("complex.vse").string();
    auto saveResult = serializer.saveProject(filePath, project);
    ASSERT_TRUE(saveResult.success);

    auto loadResult = serializer.loadProject(filePath);
    ASSERT_TRUE(loadResult.success);

    // Verify complex parameters preserved
    bool found = false;
    for (const auto& c : loadResult.data.components) {
        if (c.id == "comp-complex") {
            found = true;
            EXPECT_EQ(c.parameters["string"], "value");
            EXPECT_EQ(c.parameters["number"], 123);
            EXPECT_DOUBLE_EQ(c.parameters["float"], 3.14);
            EXPECT_EQ(c.parameters["bool"], true);
            EXPECT_EQ(c.parameters["array"].size(), 3);
            EXPECT_EQ(c.parameters["nested"]["inner"], "value");
        }
    }
    EXPECT_TRUE(found);
}

TEST_F(ProjectSerializerTest, CurrentVersion) {
    std::string version = VSE::ProjectSerializer::getCurrentVersion();
    EXPECT_FALSE(version.empty());
    EXPECT_EQ(version, "1.0");
}

TEST_F(ProjectSerializerTest, SupportedVersion) {
    EXPECT_TRUE(VSE::ProjectSerializer::isSupportedVersion("1.0"));
    EXPECT_FALSE(VSE::ProjectSerializer::isSupportedVersion("99.0"));
    EXPECT_FALSE(VSE::ProjectSerializer::isSupportedVersion(""));
}

int main(int argc, char** argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}

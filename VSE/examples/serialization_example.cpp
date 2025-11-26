/**
 * @file serialization_example.cpp
 * @brief Example demonstrating VSE project serialization
 *
 * This example shows how to:
 * - Create a project with components and connections
 * - Save the project to a .vse file
 * - Load the project from a .vse file
 * - Handle errors during save/load
 */

#include "serialization/ProjectSerializer.h"
#include "registry/ComponentRegistry.h"
#include <iostream>
#include <iomanip>

void printSeparator() {
    std::cout << std::string(60, '=') << std::endl;
}

void example1_CreateAndSaveProject() {
    printSeparator();
    std::cout << "Example 1: Creating and Saving a Project" << std::endl;
    printSeparator();

    VSE::ProjectData project;

    // Set metadata
    project.version = "1.0";
    project.metadata.name = "Logic Gate Demo";
    project.metadata.created = "2025-11-26T12:00:00Z";
    project.metadata.modified = "2025-11-26T12:00:00Z";
    project.metadata.description = "A simple logic gate circuit demonstration";
    project.metadata.author = "VSE User";

    // Set canvas state
    project.canvas.zoom = 1.0;
    project.canvas.panX = 0.0;
    project.canvas.panY = 0.0;

    // Add components
    VSE::ComponentData andGate;
    andGate.id = "comp-001";
    andGate.type = "AndGate";
    andGate.posX = 100.0;
    andGate.posY = 200.0;
    andGate.parameters = {
        {"inputCount", 2},
        {"outputInverted", false}
    };
    project.components.push_back(andGate);

    VSE::ComponentData orGate;
    orGate.id = "comp-002";
    orGate.type = "OrGate";
    orGate.posX = 300.0;
    orGate.posY = 200.0;
    orGate.parameters = {
        {"inputCount", 2},
        {"outputInverted", false}
    };
    project.components.push_back(orGate);

    VSE::ComponentData output;
    output.id = "comp-003";
    output.type = "OutputPin";
    output.posX = 500.0;
    output.posY = 200.0;
    output.parameters = {
        {"label", "Result"},
        {"dataType", "bool"}
    };
    project.components.push_back(output);

    // Add connections
    VSE::ConnectionData conn1;
    conn1.id = "conn-001";
    conn1.sourceComponentId = "comp-001";
    conn1.sourcePinName = "output";
    conn1.destinationComponentId = "comp-002";
    conn1.destinationPinName = "input_0";
    conn1.topic = "/gates/and_to_or";
    project.connections.push_back(conn1);

    VSE::ConnectionData conn2;
    conn2.id = "conn-002";
    conn2.sourceComponentId = "comp-002";
    conn2.sourcePinName = "output";
    conn2.destinationComponentId = "comp-003";
    conn2.destinationPinName = "input";
    conn2.topic = "/gates/or_to_output";
    project.connections.push_back(conn2);

    // Save the project
    VSE::ProjectSerializer serializer;
    auto result = serializer.saveProject("/tmp/logic_demo.vse", project);

    if (result.success) {
        std::cout << "Project saved successfully to /tmp/logic_demo.vse" << std::endl;
        std::cout << "Components: " << project.components.size() << std::endl;
        std::cout << "Connections: " << project.connections.size() << std::endl;
    } else {
        std::cout << "Failed to save project: " << result.error << std::endl;
    }

    std::cout << std::endl;
}

void example2_LoadProject() {
    printSeparator();
    std::cout << "Example 2: Loading a Project" << std::endl;
    printSeparator();

    VSE::ProjectSerializer serializer;
    auto result = serializer.loadProject("/tmp/logic_demo.vse");

    if (result.success) {
        const VSE::ProjectData& project = result.data;

        std::cout << "Project loaded successfully!" << std::endl;
        std::cout << std::endl;

        std::cout << "Metadata:" << std::endl;
        std::cout << "  Name: " << project.metadata.name << std::endl;
        std::cout << "  Author: " << project.metadata.author << std::endl;
        std::cout << "  Description: " << project.metadata.description << std::endl;
        std::cout << "  Created: " << project.metadata.created << std::endl;
        std::cout << "  Modified: " << project.metadata.modified << std::endl;
        std::cout << std::endl;

        std::cout << "Canvas State:" << std::endl;
        std::cout << "  Zoom: " << project.canvas.zoom << std::endl;
        std::cout << "  Pan: (" << project.canvas.panX << ", "
                  << project.canvas.panY << ")" << std::endl;
        std::cout << std::endl;

        std::cout << "Components (" << project.components.size() << "):" << std::endl;
        for (const auto& comp : project.components) {
            std::cout << "  - " << comp.type << " [" << comp.id << "]" << std::endl;
            std::cout << "    Position: (" << comp.posX << ", " << comp.posY << ")" << std::endl;
            std::cout << "    Parameters: " << comp.parameters.dump() << std::endl;
        }
        std::cout << std::endl;

        std::cout << "Connections (" << project.connections.size() << "):" << std::endl;
        for (const auto& conn : project.connections) {
            std::cout << "  - " << conn.id << std::endl;
            std::cout << "    From: " << conn.sourceComponentId
                      << "." << conn.sourcePinName << std::endl;
            std::cout << "    To: " << conn.destinationComponentId
                      << "." << conn.destinationPinName << std::endl;
            std::cout << "    Topic: " << conn.topic << std::endl;
        }

    } else {
        std::cout << "Failed to load project: " << result.error << std::endl;
    }

    std::cout << std::endl;
}

void example3_ExportImportJson() {
    printSeparator();
    std::cout << "Example 3: Export/Import JSON String" << std::endl;
    printSeparator();

    // Create a simple project
    VSE::ProjectData project;
    project.metadata.name = "JSON Export Test";
    project.metadata.created = "2025-11-26T12:00:00Z";
    project.metadata.modified = "2025-11-26T12:00:00Z";

    VSE::ComponentData comp;
    comp.id = "comp-001";
    comp.type = "TestComponent";
    comp.posX = 100.0;
    comp.posY = 100.0;
    comp.parameters = {{"value", 42}};
    project.components.push_back(comp);

    // Export to JSON string
    VSE::ProjectSerializer serializer;
    auto exportResult = serializer.exportToJson(project, true);

    if (exportResult.success) {
        std::cout << "Exported JSON:" << std::endl;
        std::cout << exportResult.data << std::endl;
        std::cout << std::endl;

        // Import back from JSON string
        auto importResult = serializer.importFromJson(exportResult.data);

        if (importResult.success) {
            std::cout << "Successfully imported from JSON string" << std::endl;
            std::cout << "Project name: " << importResult.data.metadata.name << std::endl;
            std::cout << "Components: " << importResult.data.components.size() << std::endl;
        } else {
            std::cout << "Import failed: " << importResult.error << std::endl;
        }
    } else {
        std::cout << "Export failed: " << exportResult.error << std::endl;
    }

    std::cout << std::endl;
}

void example4_ErrorHandling() {
    printSeparator();
    std::cout << "Example 4: Error Handling" << std::endl;
    printSeparator();

    VSE::ProjectSerializer serializer;

    // Try to load non-existent file
    std::cout << "Loading non-existent file..." << std::endl;
    auto result1 = serializer.loadProject("/tmp/nonexistent.vse");
    std::cout << "Result: " << (result1.success ? "Success" : "Failed") << std::endl;
    if (!result1.success) {
        std::cout << "Error: " << result1.error << std::endl;
    }
    std::cout << std::endl;

    // Try to import invalid JSON
    std::cout << "Importing invalid JSON..." << std::endl;
    auto result2 = serializer.importFromJson("{ invalid json }");
    std::cout << "Result: " << (result2.success ? "Success" : "Failed") << std::endl;
    if (!result2.success) {
        std::cout << "Error: " << result2.error << std::endl;
    }
    std::cout << std::endl;

    // Try to import incomplete project JSON
    std::cout << "Importing incomplete project JSON..." << std::endl;
    std::string incompleteJson = R"({
        "version": "1.0",
        "metadata": {
            "name": "Test"
        }
    })";
    auto result3 = serializer.importFromJson(incompleteJson);
    std::cout << "Result: " << (result3.success ? "Success" : "Failed") << std::endl;
    if (!result3.success) {
        std::cout << "Error: " << result3.error << std::endl;
    }
    std::cout << std::endl;
}

int main() {
    std::cout << std::endl;
    std::cout << "VSE Project Serialization Examples" << std::endl;
    std::cout << std::endl;

    example1_CreateAndSaveProject();
    example2_LoadProject();
    example3_ExportImportJson();
    example4_ErrorHandling();

    printSeparator();
    std::cout << "All examples completed!" << std::endl;
    printSeparator();

    return 0;
}

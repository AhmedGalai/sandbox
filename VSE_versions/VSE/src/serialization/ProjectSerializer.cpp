#include "serialization/ProjectSerializer.h"
#include <fstream>
#include <sstream>
#include <iomanip>
#include <chrono>
#include <ctime>

namespace VSE {

// Static version information
static const std::string CURRENT_VERSION = "1.0";
static const std::vector<std::string> SUPPORTED_VERSIONS = {"1.0"};

ProjectSerializer::ProjectSerializer() = default;

ProjectSerializer::~ProjectSerializer() = default;

std::string ProjectSerializer::getCurrentVersion() {
    return CURRENT_VERSION;
}

bool ProjectSerializer::isSupportedVersion(const std::string& version) {
    return std::find(SUPPORTED_VERSIONS.begin(), SUPPORTED_VERSIONS.end(), version)
           != SUPPORTED_VERSIONS.end();
}

std::string ProjectSerializer::generateTimestamp() {
    auto now = std::chrono::system_clock::now();
    auto time_t_now = std::chrono::system_clock::to_time_t(now);

    std::stringstream ss;
    ss << std::put_time(std::gmtime(&time_t_now), "%Y-%m-%dT%H:%M:%SZ");
    return ss.str();
}

SerializationResult<bool> ProjectSerializer::saveProject(const std::string& filePath,
                                                          const ProjectData& project) {
    try {
        // Serialize to JSON
        nlohmann::json json = serializeProject(project);

        // Convert to pretty-printed string
        std::string jsonString = json.dump(2); // 2-space indentation

        // Write to file
        return writeFileContents(filePath, jsonString);

    } catch (const std::exception& e) {
        return SerializationResult<bool>::Error(
            std::string("Failed to save project: ") + e.what());
    }
}

SerializationResult<ProjectData> ProjectSerializer::loadProject(const std::string& filePath) {
    try {
        // Read file contents
        auto readResult = readFileContents(filePath);
        if (!readResult.success) {
            return SerializationResult<ProjectData>::Error(readResult.error);
        }

        // Parse JSON
        nlohmann::json json;
        try {
            json = nlohmann::json::parse(readResult.data);
        } catch (const nlohmann::json::parse_error& e) {
            return SerializationResult<ProjectData>::Error(
                std::string("JSON parse error: ") + e.what());
        }

        // Validate structure
        auto validationResult = validateProjectJson(json);
        if (!validationResult.success) {
            return SerializationResult<ProjectData>::Error(validationResult.error);
        }

        // Check version and migrate if necessary
        std::string version = json.value("version", "1.0");
        if (!isSupportedVersion(version)) {
            return SerializationResult<ProjectData>::Error(
                "Unsupported file format version: " + version);
        }

        if (version != CURRENT_VERSION) {
            json = migrateVersion(json, version);
        }

        // Deserialize
        ProjectData project = deserializeProject(json);

        return SerializationResult<ProjectData>::Success(std::move(project));

    } catch (const std::exception& e) {
        return SerializationResult<ProjectData>::Error(
            std::string("Failed to load project: ") + e.what());
    }
}

SerializationResult<bool> ProjectSerializer::validateProjectJson(const nlohmann::json& json) {
    try {
        // Check root-level required fields
        std::vector<std::string> rootFields = {"version", "metadata", "canvas", "components", "connections"};
        if (!validateRequiredFields(json, rootFields)) {
            return SerializationResult<bool>::Error("Missing required root fields");
        }

        // Validate metadata
        const auto& metadata = json["metadata"];
        std::vector<std::string> metadataFields = {"name", "created", "modified"};
        if (!validateRequiredFields(metadata, metadataFields)) {
            return SerializationResult<bool>::Error("Missing required metadata fields");
        }

        // Validate canvas
        const auto& canvas = json["canvas"];
        if (!canvas.contains("zoom") || !canvas.contains("pan")) {
            return SerializationResult<bool>::Error("Invalid canvas state structure");
        }

        const auto& pan = canvas["pan"];
        if (!pan.contains("x") || !pan.contains("y")) {
            return SerializationResult<bool>::Error("Invalid pan structure in canvas");
        }

        // Validate components array
        if (!json["components"].is_array()) {
            return SerializationResult<bool>::Error("Components must be an array");
        }

        for (size_t i = 0; i < json["components"].size(); ++i) {
            if (!validateComponentData(json["components"][i])) {
                return SerializationResult<bool>::Error(
                    "Invalid component data at index " + std::to_string(i));
            }
        }

        // Validate connections array
        if (!json["connections"].is_array()) {
            return SerializationResult<bool>::Error("Connections must be an array");
        }

        for (size_t i = 0; i < json["connections"].size(); ++i) {
            if (!validateConnectionData(json["connections"][i])) {
                return SerializationResult<bool>::Error(
                    "Invalid connection data at index " + std::to_string(i));
            }
        }

        return SerializationResult<bool>::Success(true);

    } catch (const std::exception& e) {
        return SerializationResult<bool>::Error(
            std::string("Validation error: ") + e.what());
    }
}

SerializationResult<std::string> ProjectSerializer::exportToJson(const ProjectData& project,
                                                                  bool prettyPrint) {
    try {
        nlohmann::json json = serializeProject(project);
        std::string jsonString = prettyPrint ? json.dump(2) : json.dump();
        return SerializationResult<std::string>::Success(std::move(jsonString));
    } catch (const std::exception& e) {
        return SerializationResult<std::string>::Error(
            std::string("Export failed: ") + e.what());
    }
}

SerializationResult<ProjectData> ProjectSerializer::importFromJson(const std::string& jsonString) {
    try {
        nlohmann::json json = nlohmann::json::parse(jsonString);

        auto validationResult = validateProjectJson(json);
        if (!validationResult.success) {
            return SerializationResult<ProjectData>::Error(validationResult.error);
        }

        ProjectData project = deserializeProject(json);
        return SerializationResult<ProjectData>::Success(std::move(project));

    } catch (const nlohmann::json::parse_error& e) {
        return SerializationResult<ProjectData>::Error(
            std::string("JSON parse error: ") + e.what());
    } catch (const std::exception& e) {
        return SerializationResult<ProjectData>::Error(
            std::string("Import failed: ") + e.what());
    }
}

nlohmann::json ProjectSerializer::serializeProject(const ProjectData& project) {
    nlohmann::json json;

    // Version
    json["version"] = project.version;

    // Metadata
    json["metadata"] = {
        {"name", project.metadata.name},
        {"created", project.metadata.created},
        {"modified", project.metadata.modified},
        {"description", project.metadata.description},
        {"author", project.metadata.author}
    };

    // Canvas state
    json["canvas"] = {
        {"zoom", project.canvas.zoom},
        {"pan", {
            {"x", project.canvas.panX},
            {"y", project.canvas.panY}
        }}
    };

    // Components
    json["components"] = nlohmann::json::array();
    for (const auto& comp : project.components) {
        nlohmann::json compJson = {
            {"id", comp.id},
            {"type", comp.type},
            {"position", {
                {"x", comp.posX},
                {"y", comp.posY}
            }},
            {"parameters", comp.parameters}
        };
        json["components"].push_back(compJson);
    }

    // Connections
    json["connections"] = nlohmann::json::array();
    for (const auto& conn : project.connections) {
        nlohmann::json connJson = {
            {"id", conn.id},
            {"source", {
                {"componentId", conn.sourceComponentId},
                {"pinName", conn.sourcePinName}
            }},
            {"destination", {
                {"componentId", conn.destinationComponentId},
                {"pinName", conn.destinationPinName}
            }},
            {"topic", conn.topic}
        };
        json["connections"].push_back(connJson);
    }

    return json;
}

ProjectData ProjectSerializer::deserializeProject(const nlohmann::json& json) {
    ProjectData project;

    // Version
    project.version = json.value("version", "1.0");

    // Metadata
    const auto& metadata = json["metadata"];
    project.metadata.name = metadata.value("name", "Untitled");
    project.metadata.created = metadata.value("created", "");
    project.metadata.modified = metadata.value("modified", "");
    project.metadata.description = metadata.value("description", "");
    project.metadata.author = metadata.value("author", "");

    // Canvas state
    const auto& canvas = json["canvas"];
    project.canvas.zoom = canvas.value("zoom", 1.0);
    project.canvas.panX = canvas["pan"].value("x", 0.0);
    project.canvas.panY = canvas["pan"].value("y", 0.0);

    // Components
    for (const auto& compJson : json["components"]) {
        ComponentData comp;
        comp.id = compJson.value("id", "");
        comp.type = compJson.value("type", "");

        if (compJson.contains("position")) {
            comp.posX = compJson["position"].value("x", 0.0);
            comp.posY = compJson["position"].value("y", 0.0);
        }

        comp.parameters = compJson.value("parameters", nlohmann::json::object());

        project.components.push_back(comp);
    }

    // Connections
    for (const auto& connJson : json["connections"]) {
        ConnectionData conn;
        conn.id = connJson.value("id", "");
        conn.topic = connJson.value("topic", "");

        if (connJson.contains("source")) {
            conn.sourceComponentId = connJson["source"].value("componentId", "");
            conn.sourcePinName = connJson["source"].value("pinName", "");
        }

        if (connJson.contains("destination")) {
            conn.destinationComponentId = connJson["destination"].value("componentId", "");
            conn.destinationPinName = connJson["destination"].value("pinName", "");
        }

        project.connections.push_back(conn);
    }

    return project;
}

nlohmann::json ProjectSerializer::migrateVersion(const nlohmann::json& json,
                                                  const std::string& fromVersion) {
    // Future version migration logic goes here
    // For now, since we only support 1.0, just return as-is

    // Example for future versions:
    // if (fromVersion == "1.0") {
    //     // Migrate 1.0 -> 1.1
    //     nlohmann::json migrated = json;
    //     // Add new fields, transform data, etc.
    //     return migrated;
    // }

    return json;
}

SerializationResult<std::string> ProjectSerializer::readFileContents(const std::string& filePath) {
    std::ifstream file(filePath);
    if (!file.is_open()) {
        return SerializationResult<std::string>::Error(
            "Failed to open file: " + filePath);
    }

    std::stringstream buffer;
    buffer << file.rdbuf();

    if (file.bad()) {
        return SerializationResult<std::string>::Error(
            "Error reading file: " + filePath);
    }

    return SerializationResult<std::string>::Success(buffer.str());
}

SerializationResult<bool> ProjectSerializer::writeFileContents(const std::string& filePath,
                                                                const std::string& contents) {
    std::ofstream file(filePath);
    if (!file.is_open()) {
        return SerializationResult<bool>::Error(
            "Failed to open file for writing: " + filePath);
    }

    file << contents;

    if (file.bad()) {
        return SerializationResult<bool>::Error(
            "Error writing to file: " + filePath);
    }

    return SerializationResult<bool>::Success(true);
}

bool ProjectSerializer::validateRequiredFields(const nlohmann::json& json,
                                               const std::vector<std::string>& requiredFields) {
    for (const auto& field : requiredFields) {
        if (!json.contains(field)) {
            return false;
        }
    }
    return true;
}

bool ProjectSerializer::validateComponentData(const nlohmann::json& componentJson) {
    // Check required fields
    if (!componentJson.contains("id") || !componentJson.contains("type")) {
        return false;
    }

    // Check position structure
    if (componentJson.contains("position")) {
        const auto& pos = componentJson["position"];
        if (!pos.contains("x") || !pos.contains("y")) {
            return false;
        }
    }

    // Parameters can be optional or empty
    return true;
}

bool ProjectSerializer::validateConnectionData(const nlohmann::json& connectionJson) {
    // Check required fields
    std::vector<std::string> required = {"id", "source", "destination", "topic"};
    if (!validateRequiredFields(connectionJson, required)) {
        return false;
    }

    // Validate source structure
    const auto& source = connectionJson["source"];
    if (!source.contains("componentId") || !source.contains("pinName")) {
        return false;
    }

    // Validate destination structure
    const auto& destination = connectionJson["destination"];
    if (!destination.contains("componentId") || !destination.contains("pinName")) {
        return false;
    }

    return true;
}

} // namespace VSE

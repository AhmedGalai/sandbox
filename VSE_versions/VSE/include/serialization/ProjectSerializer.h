#ifndef VSE_PROJECT_SERIALIZER_H
#define VSE_PROJECT_SERIALIZER_H

#include <string>
#include <memory>
#include <vector>
#include <optional>
#include <nlohmann/json.hpp>

namespace VSE {

// Forward declarations
class Component;
class Connection;

/**
 * @brief Metadata information about a VSE project
 */
struct ProjectMetadata {
    std::string name;           ///< Project name
    std::string created;        ///< Creation timestamp (ISO 8601)
    std::string modified;       ///< Last modification timestamp (ISO 8601)
    std::string description;    ///< Optional project description
    std::string author;         ///< Optional project author
};

/**
 * @brief Canvas view state for preserving zoom and pan
 */
struct CanvasState {
    double zoom = 1.0;          ///< Zoom level (1.0 = 100%)
    double panX = 0.0;          ///< Horizontal pan offset
    double panY = 0.0;          ///< Vertical pan offset
};

/**
 * @brief Component data for serialization
 */
struct ComponentData {
    std::string id;                     ///< Unique component identifier (UUID)
    std::string type;                   ///< Component type name
    double posX = 0.0;                  ///< X position on canvas
    double posY = 0.0;                  ///< Y position on canvas
    nlohmann::json parameters;          ///< Component-specific parameters
};

/**
 * @brief Connection data for serialization
 */
struct ConnectionData {
    std::string id;                     ///< Unique connection identifier (UUID)
    std::string sourceComponentId;      ///< Source component UUID
    std::string sourcePinName;          ///< Source pin name
    std::string destinationComponentId; ///< Destination component UUID
    std::string destinationPinName;     ///< Destination pin name
    std::string topic;                  ///< ROS2-like topic name
};

/**
 * @brief Complete project data structure
 */
struct ProjectData {
    std::string version = "1.0";        ///< File format version
    ProjectMetadata metadata;           ///< Project metadata
    CanvasState canvas;                 ///< Canvas state
    std::vector<ComponentData> components;      ///< All components
    std::vector<ConnectionData> connections;    ///< All connections
};

/**
 * @brief Result type for serialization operations
 */
template<typename T>
struct SerializationResult {
    bool success = false;
    std::string error;
    T data;

    static SerializationResult<T> Success(T&& value) {
        SerializationResult<T> result;
        result.success = true;
        result.data = std::forward<T>(value);
        return result;
    }

    static SerializationResult<T> Error(const std::string& errorMsg) {
        SerializationResult<T> result;
        result.success = false;
        result.error = errorMsg;
        return result;
    }
};

/**
 * @brief Handles serialization and deserialization of VSE projects
 *
 * The ProjectSerializer class provides functionality to save and load VSE projects
 * in JSON format (.vse files). It handles versioning, validation, and error reporting.
 *
 * Features:
 * - JSON-based file format for human readability
 * - Version migration support for backward compatibility
 * - Comprehensive validation on load
 * - Graceful handling of missing component types
 * - Detailed error reporting
 *
 * File Format:
 * - Extension: .vse
 * - Encoding: UTF-8
 * - Format: JSON with pretty printing
 *
 * @see ProjectData for the complete schema
 */
class ProjectSerializer {
public:
    /**
     * @brief Construct a new Project Serializer
     */
    ProjectSerializer();

    /**
     * @brief Destroy the Project Serializer
     */
    ~ProjectSerializer();

    /**
     * @brief Save a project to a .vse file
     *
     * Serializes the complete project state including components, connections,
     * canvas state, and metadata to a JSON file with .vse extension.
     *
     * @param filePath Path to the output .vse file
     * @param project Project data to serialize
     * @return SerializationResult<bool> Success status with error message if failed
     *
     * @code
     * ProjectData project;
     * project.metadata.name = "My Project";
     * ProjectSerializer serializer;
     * auto result = serializer.saveProject("/path/to/project.vse", project);
     * if (!result.success) {
     *     std::cerr << "Save failed: " << result.error << std::endl;
     * }
     * @endcode
     */
    SerializationResult<bool> saveProject(const std::string& filePath,
                                          const ProjectData& project);

    /**
     * @brief Load a project from a .vse file
     *
     * Deserializes a project from a JSON .vse file with full validation.
     * Handles version migration if the file format is from an older version.
     *
     * @param filePath Path to the .vse file to load
     * @return SerializationResult<ProjectData> Loaded project data or error
     *
     * @code
     * ProjectSerializer serializer;
     * auto result = serializer.loadProject("/path/to/project.vse");
     * if (result.success) {
     *     ProjectData project = result.data;
     *     // Use project data
     * } else {
     *     std::cerr << "Load failed: " << result.error << std::endl;
     * }
     * @endcode
     */
    SerializationResult<ProjectData> loadProject(const std::string& filePath);

    /**
     * @brief Validate project JSON structure
     *
     * Performs schema validation on a parsed JSON object to ensure it
     * contains all required fields with correct types.
     *
     * @param json JSON object to validate
     * @return SerializationResult<bool> Validation result with error details
     */
    SerializationResult<bool> validateProjectJson(const nlohmann::json& json);

    /**
     * @brief Export project to JSON string
     *
     * Useful for debugging, network transmission, or clipboard operations.
     *
     * @param project Project data to serialize
     * @param prettyPrint If true, format with indentation for readability
     * @return SerializationResult<std::string> JSON string or error
     */
    SerializationResult<std::string> exportToJson(const ProjectData& project,
                                                   bool prettyPrint = true);

    /**
     * @brief Import project from JSON string
     *
     * Useful for network reception, clipboard paste, or testing.
     *
     * @param jsonString JSON string to parse
     * @return SerializationResult<ProjectData> Parsed project data or error
     */
    SerializationResult<ProjectData> importFromJson(const std::string& jsonString);

    /**
     * @brief Get current file format version
     *
     * @return std::string Current version string (e.g., "1.0")
     */
    static std::string getCurrentVersion();

    /**
     * @brief Check if a file format version is supported
     *
     * @param version Version string to check
     * @return true if version can be loaded (with migration if needed)
     * @return false if version is unsupported
     */
    static bool isSupportedVersion(const std::string& version);

private:
    /**
     * @brief Convert ProjectData to JSON
     */
    nlohmann::json serializeProject(const ProjectData& project);

    /**
     * @brief Convert JSON to ProjectData
     */
    ProjectData deserializeProject(const nlohmann::json& json);

    /**
     * @brief Migrate older file format versions to current version
     */
    nlohmann::json migrateVersion(const nlohmann::json& json,
                                  const std::string& fromVersion);

    /**
     * @brief Generate ISO 8601 timestamp for current time
     */
    std::string generateTimestamp();

    /**
     * @brief Read file contents into string
     */
    SerializationResult<std::string> readFileContents(const std::string& filePath);

    /**
     * @brief Write string contents to file
     */
    SerializationResult<bool> writeFileContents(const std::string& filePath,
                                                 const std::string& contents);

    /**
     * @brief Validate required fields exist in JSON
     */
    bool validateRequiredFields(const nlohmann::json& json,
                               const std::vector<std::string>& requiredFields);

    /**
     * @brief Validate component data structure
     */
    bool validateComponentData(const nlohmann::json& componentJson);

    /**
     * @brief Validate connection data structure
     */
    bool validateConnectionData(const nlohmann::json& connectionJson);
};

} // namespace VSE

#endif // VSE_PROJECT_SERIALIZER_H

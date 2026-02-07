#ifndef VSE_PIN_H
#define VSE_PIN_H

#include <QString>
#include <QVariant>
#include <memory>
#include <vector>
#include <functional>
#include <nlohmann/json.hpp>

namespace VSE {

// Forward declarations
class Pin;
class InputPin;
class OutputPin;

/**
 * @brief Pin type enumeration
 */
enum class PinType {
    Input,  ///< Input pin (receives data)
    Output  ///< Output pin (transmits data)
};

/**
 * @brief Data type enumeration for pins
 */
enum class DataType {
    Boolean,  ///< Boolean data type
    Integer,  ///< Integer data type
    Float,    ///< Floating point data type
    String,   ///< String data type
    Json,     ///< JSON object data type
    Any       ///< Any data type (accepts all)
};

/**
 * @brief Convert DataType to string
 * @param type Data type
 * @return std::string String representation
 */
std::string dataTypeToString(DataType type);

/**
 * @brief Convert string to DataType
 * @param str String representation
 * @return DataType Data type
 */
DataType stringToDataType(const std::string& str);

/**
 * @brief Base class for component pins
 *
 * Pins represent connection points on components. They can be either
 * input pins (receiving data) or output pins (transmitting data).
 */
class Pin {
public:
    /**
     * @brief Construct a new Pin object
     * @param name Pin name
     * @param type Pin type (Input or Output)
     * @param dataType Data type this pin accepts/produces
     */
    Pin(const QString& name, PinType type, DataType dataType);

    virtual ~Pin() = default;

    /**
     * @brief Get the pin name
     * @return const QString& Pin name
     */
    const QString& getName() const { return m_name; }

    /**
     * @brief Get the pin type
     * @return PinType Pin type
     */
    PinType getType() const { return m_type; }

    /**
     * @brief Get the data type
     * @return DataType Data type
     */
    DataType getDataType() const { return m_dataType; }

    /**
     * @brief Check if pin is connected
     * @return bool True if connected
     */
    virtual bool isConnected() const = 0;

    /**
     * @brief Get the unique ID of this pin
     * @return const QString& Pin ID
     */
    const QString& getId() const { return m_id; }

    /**
     * @brief Set the pin ID
     * @param id Unique ID
     */
    void setId(const QString& id) { m_id = id; }

    /**
     * @brief Serialize pin to JSON
     * @return nlohmann::json JSON representation
     */
    virtual nlohmann::json toJson() const;

    /**
     * @brief Deserialize pin from JSON
     * @param json JSON data
     */
    virtual void fromJson(const nlohmann::json& json);

protected:
    QString m_name;       ///< Pin name
    QString m_id;         ///< Unique pin ID
    PinType m_type;       ///< Pin type
    DataType m_dataType;  ///< Data type
};

/**
 * @brief Input pin class
 *
 * Input pins receive data from a single connected output pin.
 * They support data reception callbacks for reactive processing.
 */
class InputPin : public Pin {
public:
    using DataCallback = std::function<void(const QVariant&)>;

    /**
     * @brief Construct a new Input Pin object
     * @param name Pin name
     * @param dataType Data type this pin accepts
     */
    InputPin(const QString& name, DataType dataType);

    /**
     * @brief Check if pin is connected
     * @return bool True if connected to an output pin
     */
    bool isConnected() const override;

    /**
     * @brief Connect to an output pin
     * @param outputPin Output pin to connect to
     * @return bool True if connection successful
     */
    bool connectTo(std::shared_ptr<OutputPin> outputPin);

    /**
     * @brief Disconnect from the connected output pin
     */
    void disconnect();

    /**
     * @brief Get the connected output pin
     * @return std::shared_ptr<OutputPin> Connected output pin (or nullptr)
     */
    std::shared_ptr<OutputPin> getConnectedPin() const { return m_connectedPin; }

    /**
     * @brief Receive data on this input pin
     * @param data Data to receive
     */
    void receiveData(const QVariant& data);

    /**
     * @brief Get the current data value
     * @return const QVariant& Current data
     */
    const QVariant& getData() const { return m_data; }

    /**
     * @brief Set the data reception callback
     * @param callback Callback function
     */
    void setDataCallback(DataCallback callback) { m_dataCallback = callback; }

    /**
     * @brief Check if data type is compatible
     * @param otherType Data type to check
     * @return bool True if compatible
     */
    bool isCompatible(DataType otherType) const;

    nlohmann::json toJson() const override;
    void fromJson(const nlohmann::json& json) override;

private:
    std::shared_ptr<OutputPin> m_connectedPin; ///< Connected output pin
    QVariant m_data;                           ///< Current data value
    DataCallback m_dataCallback;               ///< Data reception callback
};

/**
 * @brief Output pin class
 *
 * Output pins transmit data to multiple connected input pins.
 * They support broadcasting data to all connected inputs.
 */
class OutputPin : public Pin {
public:
    /**
     * @brief Construct a new Output Pin object
     * @param name Pin name
     * @param dataType Data type this pin produces
     */
    OutputPin(const QString& name, DataType dataType);

    /**
     * @brief Check if pin is connected
     * @return bool True if connected to any input pins
     */
    bool isConnected() const override;

    /**
     * @brief Add a connection to an input pin
     * @param inputPin Input pin to connect to
     * @return bool True if connection successful
     */
    bool addConnection(std::shared_ptr<InputPin> inputPin);

    /**
     * @brief Remove a connection to an input pin
     * @param inputPin Input pin to disconnect from
     */
    void removeConnection(std::shared_ptr<InputPin> inputPin);

    /**
     * @brief Disconnect from all input pins
     */
    void disconnectAll();

    /**
     * @brief Get all connected input pins
     * @return const std::vector<std::shared_ptr<InputPin>>& Connected input pins
     */
    const std::vector<std::shared_ptr<InputPin>>& getConnectedPins() const {
        return m_connectedPins;
    }

    /**
     * @brief Transmit data to all connected input pins
     * @param data Data to transmit
     */
    void transmitData(const QVariant& data);

    /**
     * @brief Get the current data value
     * @return const QVariant& Current data
     */
    const QVariant& getData() const { return m_data; }

    nlohmann::json toJson() const override;
    void fromJson(const nlohmann::json& json) override;

private:
    std::vector<std::shared_ptr<InputPin>> m_connectedPins; ///< Connected input pins
    QVariant m_data;                                        ///< Current data value
};

} // namespace VSE

#endif // VSE_PIN_H

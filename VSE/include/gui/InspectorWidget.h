/**
 * @file InspectorWidget.h
 * @brief Property inspector widget for editing component parameters
 */

#ifndef VSE_GUI_INSPECTORWIDGET_H
#define VSE_GUI_INSPECTORWIDGET_H

#include <QWidget>
#include <QMap>
#include <QVariant>

// Forward declarations
class QVBoxLayout;
class QFormLayout;
class QScrollArea;
class QLabel;
class ComponentNodeItem;

namespace VSE {
namespace GUI {

/**
 * @class InspectorWidget
 * @brief Widget for displaying and editing component properties
 *
 * InspectorWidget provides:
 * - Dynamic property editor generation based on component type
 * - Support for various property types (int, float, string, bool, color, file)
 * - Real-time updates to component parameters
 * - Clear display when no component is selected
 * - Scrollable interface for many properties
 */
class InspectorWidget : public QWidget {
    Q_OBJECT

public:
    /**
     * @brief Construct a new InspectorWidget
     * @param parent Parent widget
     */
    explicit InspectorWidget(QWidget* parent = nullptr);

    /**
     * @brief Destructor
     */
    ~InspectorWidget() override;

    /**
     * @brief Set the component to inspect
     * @param node Component node to display properties for
     */
    void setInspectedNode(ComponentNodeItem* node);

    /**
     * @brief Clear the inspector (no selection)
     */
    void clear();

signals:
    /**
     * @brief Emitted when a property value changes
     * @param propertyName Name of the property
     * @param value New value
     */
    void propertyChanged(const QString& propertyName, const QVariant& value);

private slots:
    /**
     * @brief Handle property change from UI widget
     */
    void onPropertyChanged();

private:
    /**
     * @brief Populate inspector with component properties
     * @param node Component node to inspect
     */
    void populateProperties(ComponentNodeItem* node);

    /**
     * @brief Clear all property widgets
     */
    void clearProperties();

    /**
     * @brief Add a property editor to the form
     * @param name Property name
     * @param type Property type
     * @param value Current value
     */
    void addProperty(const QString& name, QVariant::Type type, const QVariant& value);

    /**
     * @brief Add integer property editor
     * @param name Property name
     * @param value Current value
     */
    void addIntProperty(const QString& name, int value);

    /**
     * @brief Add floating-point property editor
     * @param name Property name
     * @param value Current value
     */
    void addDoubleProperty(const QString& name, double value);

    /**
     * @brief Add string property editor
     * @param name Property name
     * @param value Current value
     */
    void addStringProperty(const QString& name, const QString& value);

    /**
     * @brief Add boolean property editor
     * @param name Property name
     * @param value Current value
     */
    void addBoolProperty(const QString& name, bool value);

    /**
     * @brief Add color property editor
     * @param name Property name
     * @param value Current value (QColor)
     */
    void addColorProperty(const QString& name, const QColor& value);

    /**
     * @brief Add file path property editor
     * @param name Property name
     * @param value Current value (file path)
     */
    void addFileProperty(const QString& name, const QString& value);

    /**
     * @brief Update property value in the inspected component
     * @param name Property name
     * @param value New value
     */
    void updateComponentProperty(const QString& name, const QVariant& value);

private:
    QVBoxLayout* m_mainLayout;          ///< Main layout
    QScrollArea* m_scrollArea;          ///< Scrollable area
    QWidget* m_contentWidget;           ///< Content widget inside scroll area
    QFormLayout* m_formLayout;          ///< Form layout for properties

    QLabel* m_titleLabel;               ///< Title label (component name)
    QLabel* m_emptyLabel;               ///< Label shown when no selection

    ComponentNodeItem* m_inspectedNode; ///< Currently inspected node

    // Map of property widgets for value updates
    QMap<QString, QWidget*> m_propertyWidgets;
};

} // namespace GUI
} // namespace VSE

#endif // VSE_GUI_INSPECTORWIDGET_H

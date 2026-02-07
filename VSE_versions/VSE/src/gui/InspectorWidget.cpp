/**
 * @file InspectorWidget.cpp
 * @brief Implementation of InspectorWidget
 */

#include "gui/InspectorWidget.h"
#include "gui/ComponentNodeItem.h"

#include <QVBoxLayout>
#include <QFormLayout>
#include <QScrollArea>
#include <QLabel>
#include <QSpinBox>
#include <QDoubleSpinBox>
#include <QLineEdit>
#include <QCheckBox>
#include <QPushButton>
#include <QColorDialog>
#include <QFileDialog>
#include <QFrame>
#include <QFont>

namespace VSE {
namespace GUI {

InspectorWidget::InspectorWidget(QWidget* parent)
    : QWidget(parent)
    , m_inspectedNode(nullptr)
{
    m_mainLayout = new QVBoxLayout(this);
    m_mainLayout->setContentsMargins(5, 5, 5, 5);
    m_mainLayout->setSpacing(5);

    // Title label
    m_titleLabel = new QLabel(this);
    m_titleLabel->setStyleSheet(
        "QLabel {"
        "  font-size: 14px;"
        "  font-weight: bold;"
        "  padding: 8px;"
        "  background-color: #3c3c3f;"
        "  border-radius: 4px;"
        "}"
    );
    m_titleLabel->setAlignment(Qt::AlignCenter);
    m_titleLabel->setVisible(false);
    m_mainLayout->addWidget(m_titleLabel);

    // Empty state label
    m_emptyLabel = new QLabel(tr("No component selected"), this);
    m_emptyLabel->setAlignment(Qt::AlignCenter);
    m_emptyLabel->setStyleSheet("color: gray; padding: 20px;");
    m_mainLayout->addWidget(m_emptyLabel);

    // Create scroll area
    m_scrollArea = new QScrollArea(this);
    m_scrollArea->setWidgetResizable(true);
    m_scrollArea->setFrameShape(QFrame::NoFrame);
    m_scrollArea->setHorizontalScrollBarPolicy(Qt::ScrollBarAlwaysOff);
    m_scrollArea->setVisible(false);

    // Content widget
    m_contentWidget = new QWidget();
    m_formLayout = new QFormLayout(m_contentWidget);
    m_formLayout->setContentsMargins(5, 5, 5, 5);
    m_formLayout->setSpacing(8);
    m_formLayout->setFieldGrowthPolicy(QFormLayout::ExpandingFieldsGrow);
    m_contentWidget->setLayout(m_formLayout);

    m_scrollArea->setWidget(m_contentWidget);
    m_mainLayout->addWidget(m_scrollArea);

    setLayout(m_mainLayout);
}

InspectorWidget::~InspectorWidget()
{
}

void InspectorWidget::setInspectedNode(ComponentNodeItem* node)
{
    if (m_inspectedNode == node) {
        return;
    }

    m_inspectedNode = node;

    if (node) {
        populateProperties(node);
        m_emptyLabel->setVisible(false);
        m_titleLabel->setVisible(true);
        m_scrollArea->setVisible(true);
    } else {
        clear();
    }
}

void InspectorWidget::clear()
{
    m_inspectedNode = nullptr;
    clearProperties();
    m_titleLabel->setVisible(false);
    m_scrollArea->setVisible(false);
    m_emptyLabel->setVisible(true);
}

void InspectorWidget::populateProperties(ComponentNodeItem* node)
{
    clearProperties();

    if (!node) {
        return;
    }

    // Set title
    m_titleLabel->setText(node->getComponentName());

    // Get properties from the node
    // For now, we'll add some example properties
    // In a real implementation, these would come from the component's metadata

    // Example properties (will be replaced with actual component properties)
    addStringProperty("Name", node->getComponentName());
    addIntProperty("X Position", static_cast<int>(node->pos().x()));
    addIntProperty("Y Position", static_cast<int>(node->pos().y()));

    // Add separator
    QFrame* line = new QFrame();
    line->setFrameShape(QFrame::HLine);
    line->setFrameShadow(QFrame::Sunken);
    m_formLayout->addRow(line);

    // Add example component-specific properties
    addIntProperty("Input Count", 2);
    addIntProperty("Output Count", 1);
    addBoolProperty("Enabled", true);
    addDoubleProperty("Scale", 1.0);
    addColorProperty("Color", QColor(100, 150, 200));
}

void InspectorWidget::clearProperties()
{
    // Remove all widgets from form layout
    while (m_formLayout->count() > 0) {
        QLayoutItem* item = m_formLayout->takeAt(0);
        if (item->widget()) {
            delete item->widget();
        }
        delete item;
    }

    m_propertyWidgets.clear();
}

void InspectorWidget::addProperty(const QString& name, QVariant::Type type, const QVariant& value)
{
    switch (type) {
        case QVariant::Int:
            addIntProperty(name, value.toInt());
            break;
        case QVariant::Double:
            addDoubleProperty(name, value.toDouble());
            break;
        case QVariant::String:
            addStringProperty(name, value.toString());
            break;
        case QVariant::Bool:
            addBoolProperty(name, value.toBool());
            break;
        case QVariant::Color:
            addColorProperty(name, value.value<QColor>());
            break;
        default:
            addStringProperty(name, value.toString());
            break;
    }
}

void InspectorWidget::addIntProperty(const QString& name, int value)
{
    QSpinBox* spinBox = new QSpinBox(m_contentWidget);
    spinBox->setRange(-999999, 999999);
    spinBox->setValue(value);
    spinBox->setProperty("propertyName", name);

    connect(spinBox, QOverload<int>::of(&QSpinBox::valueChanged),
            this, &InspectorWidget::onPropertyChanged);

    m_formLayout->addRow(name + ":", spinBox);
    m_propertyWidgets[name] = spinBox;
}

void InspectorWidget::addDoubleProperty(const QString& name, double value)
{
    QDoubleSpinBox* spinBox = new QDoubleSpinBox(m_contentWidget);
    spinBox->setRange(-999999.0, 999999.0);
    spinBox->setDecimals(3);
    spinBox->setSingleStep(0.1);
    spinBox->setValue(value);
    spinBox->setProperty("propertyName", name);

    connect(spinBox, QOverload<double>::of(&QDoubleSpinBox::valueChanged),
            this, &InspectorWidget::onPropertyChanged);

    m_formLayout->addRow(name + ":", spinBox);
    m_propertyWidgets[name] = spinBox;
}

void InspectorWidget::addStringProperty(const QString& name, const QString& value)
{
    QLineEdit* lineEdit = new QLineEdit(m_contentWidget);
    lineEdit->setText(value);
    lineEdit->setProperty("propertyName", name);

    connect(lineEdit, &QLineEdit::textChanged,
            this, &InspectorWidget::onPropertyChanged);

    m_formLayout->addRow(name + ":", lineEdit);
    m_propertyWidgets[name] = lineEdit;
}

void InspectorWidget::addBoolProperty(const QString& name, bool value)
{
    QCheckBox* checkBox = new QCheckBox(m_contentWidget);
    checkBox->setChecked(value);
    checkBox->setProperty("propertyName", name);

    connect(checkBox, &QCheckBox::toggled,
            this, &InspectorWidget::onPropertyChanged);

    m_formLayout->addRow(name + ":", checkBox);
    m_propertyWidgets[name] = checkBox;
}

void InspectorWidget::addColorProperty(const QString& name, const QColor& value)
{
    QPushButton* colorButton = new QPushButton(m_contentWidget);
    colorButton->setProperty("propertyName", name);
    colorButton->setProperty("color", value);

    // Set button style to show color
    QString style = QString(
        "QPushButton {"
        "  background-color: %1;"
        "  border: 1px solid #555;"
        "  border-radius: 3px;"
        "  padding: 5px;"
        "  min-width: 60px;"
        "}"
        "QPushButton:hover {"
        "  border: 1px solid #888;"
        "}"
    ).arg(value.name());
    colorButton->setStyleSheet(style);
    colorButton->setText(value.name());

    connect(colorButton, &QPushButton::clicked, [this, colorButton, name]() {
        QColor currentColor = colorButton->property("color").value<QColor>();
        QColor newColor = QColorDialog::getColor(currentColor, this, tr("Select Color"));

        if (newColor.isValid()) {
            colorButton->setProperty("color", newColor);
            QString style = QString(
                "QPushButton {"
                "  background-color: %1;"
                "  border: 1px solid #555;"
                "  border-radius: 3px;"
                "  padding: 5px;"
                "  min-width: 60px;"
                "}"
                "QPushButton:hover {"
                "  border: 1px solid #888;"
                "}"
            ).arg(newColor.name());
            colorButton->setStyleSheet(style);
            colorButton->setText(newColor.name());

            updateComponentProperty(name, newColor);
            emit propertyChanged(name, newColor);
        }
    });

    m_formLayout->addRow(name + ":", colorButton);
    m_propertyWidgets[name] = colorButton;
}

void InspectorWidget::addFileProperty(const QString& name, const QString& value)
{
    QWidget* fileWidget = new QWidget(m_contentWidget);
    QHBoxLayout* fileLayout = new QHBoxLayout(fileWidget);
    fileLayout->setContentsMargins(0, 0, 0, 0);
    fileLayout->setSpacing(5);

    QLineEdit* pathEdit = new QLineEdit(fileWidget);
    pathEdit->setText(value);
    pathEdit->setProperty("propertyName", name);
    pathEdit->setReadOnly(true);

    QPushButton* browseButton = new QPushButton(tr("Browse..."), fileWidget);
    browseButton->setMaximumWidth(80);

    connect(browseButton, &QPushButton::clicked, [this, pathEdit, name]() {
        QString filePath = QFileDialog::getOpenFileName(
            this,
            tr("Select File"),
            pathEdit->text(),
            tr("All Files (*)")
        );

        if (!filePath.isEmpty()) {
            pathEdit->setText(filePath);
            updateComponentProperty(name, filePath);
            emit propertyChanged(name, filePath);
        }
    });

    connect(pathEdit, &QLineEdit::textChanged,
            this, &InspectorWidget::onPropertyChanged);

    fileLayout->addWidget(pathEdit);
    fileLayout->addWidget(browseButton);
    fileWidget->setLayout(fileLayout);

    m_formLayout->addRow(name + ":", fileWidget);
    m_propertyWidgets[name] = fileWidget;
}

void InspectorWidget::onPropertyChanged()
{
    QObject* sender = QObject::sender();
    if (!sender) {
        return;
    }

    QString propertyName = sender->property("propertyName").toString();
    if (propertyName.isEmpty()) {
        return;
    }

    QVariant value;

    // Extract value based on widget type
    if (QSpinBox* spinBox = qobject_cast<QSpinBox*>(sender)) {
        value = spinBox->value();
    } else if (QDoubleSpinBox* spinBox = qobject_cast<QDoubleSpinBox*>(sender)) {
        value = spinBox->value();
    } else if (QLineEdit* lineEdit = qobject_cast<QLineEdit*>(sender)) {
        value = lineEdit->text();
    } else if (QCheckBox* checkBox = qobject_cast<QCheckBox*>(sender)) {
        value = checkBox->isChecked();
    }

    if (value.isValid()) {
        updateComponentProperty(propertyName, value);
        emit propertyChanged(propertyName, value);
    }
}

void InspectorWidget::updateComponentProperty(const QString& name, const QVariant& value)
{
    if (!m_inspectedNode) {
        return;
    }

    // Update position properties directly
    if (name == "X Position") {
        QPointF pos = m_inspectedNode->pos();
        pos.setX(value.toDouble());
        m_inspectedNode->setPos(pos);
    } else if (name == "Y Position") {
        QPointF pos = m_inspectedNode->pos();
        pos.setY(value.toDouble());
        m_inspectedNode->setPos(pos);
    } else if (name == "Name") {
        m_inspectedNode->setComponentName(value.toString());
        m_titleLabel->setText(value.toString());
    }

    // TODO: Update other component-specific properties
    // This will be implemented when component system is integrated
}

} // namespace GUI
} // namespace VSE

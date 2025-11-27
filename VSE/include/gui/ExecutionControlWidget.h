/**
 * @file ExecutionControlWidget.h
 * @brief GUI widget for controlling program execution
 *
 * Provides user interface controls for starting, stopping, pausing, and
 * stepping through visual program execution. Displays execution state and
 * statistics in real-time.
 */

#ifndef VSE_GUI_EXECUTIONCONTROLWIDGET_H
#define VSE_GUI_EXECUTIONCONTROLWIDGET_H

#include <QWidget>
#include <QPushButton>
#include <QLabel>
#include <QSpinBox>
#include <QDoubleSpinBox>
#include <QLCDNumber>
#include <QGroupBox>
#include <QComboBox>
#include <memory>

namespace VSE {
namespace Core {
    class ExecutionEngine;
    enum class ExecutionState;
    enum class ExecutionMode;
}

namespace GUI {

/**
 * @class ExecutionControlWidget
 * @brief Widget providing execution control UI
 *
 * The ExecutionControlWidget provides a comprehensive interface for
 * controlling visual program execution:
 * - Control buttons (Start, Stop, Pause, Step)
 * - Execution state display
 * - Real-time statistics (iterations, time, errors)
 * - Execution rate control
 * - Execution mode selection
 *
 * The widget automatically updates based on ExecutionEngine signals and
 * provides visual feedback for the current execution state.
 *
 * Example usage:
 * @code
 * auto engine = std::make_shared<ExecutionEngine>();
 * auto widget = new ExecutionControlWidget();
 * widget->setExecutionEngine(engine);
 * widget->show();
 * @endcode
 */
class ExecutionControlWidget : public QWidget {
    Q_OBJECT

public:
    /**
     * @brief Construct a new Execution Control Widget
     * @param parent Parent widget
     */
    explicit ExecutionControlWidget(QWidget* parent = nullptr);

    /**
     * @brief Destructor
     */
    ~ExecutionControlWidget() override;

    /**
     * @brief Set the execution engine to control
     * @param engine Shared pointer to execution engine
     */
    void setExecutionEngine(std::shared_ptr<Core::ExecutionEngine> engine);

    /**
     * @brief Get the controlled execution engine
     * @return std::shared_ptr<Core::ExecutionEngine> Execution engine
     */
    std::shared_ptr<Core::ExecutionEngine> getExecutionEngine() const {
        return m_engine;
    }

    /**
     * @brief Update display with current execution statistics
     */
    void updateStatistics();

    /**
     * @brief Update execution state display
     */
    void updateStateDisplay();

    /**
     * @brief Set whether controls are enabled
     * @param enabled Enable state
     */
    void setControlsEnabled(bool enabled);

public slots:
    /**
     * @brief Handle start button click
     */
    void onStartClicked();

    /**
     * @brief Handle stop button click
     */
    void onStopClicked();

    /**
     * @brief Handle pause button click
     */
    void onPauseClicked();

    /**
     * @brief Handle step button click
     */
    void onStepClicked();

    /**
     * @brief Handle reset button click
     */
    void onResetClicked();

    /**
     * @brief Handle execution rate change
     * @param rate New execution rate in Hz
     */
    void onExecutionRateChanged(double rate);

    /**
     * @brief Handle execution mode change
     * @param index Combo box index
     */
    void onExecutionModeChanged(int index);

private slots:
    /**
     * @brief Handle execution state change from engine
     * @param newState New execution state
     * @param oldState Previous execution state
     */
    void onEngineStateChanged(Core::ExecutionState newState, Core::ExecutionState oldState);

    /**
     * @brief Handle iteration completed signal
     * @param iteration Iteration number
     */
    void onIterationCompleted(uint64_t iteration);

    /**
     * @brief Handle error signal
     * @param message Error message
     * @param componentId Component that caused error
     */
    void onErrorOccurred(const QString& message, const QString& componentId);

    /**
     * @brief Handle statistics update
     * @param iterations Total iterations
     * @param elapsedMs Elapsed time in milliseconds
     * @param errors Error count
     */
    void onStatisticsUpdated(uint64_t iterations, int64_t elapsedMs, size_t errors);

private:
    /**
     * @brief Setup the user interface
     */
    void setupUI();

    /**
     * @brief Create control buttons group
     * @return QGroupBox* Group box with buttons
     */
    QGroupBox* createControlButtons();

    /**
     * @brief Create statistics display group
     * @return QGroupBox* Group box with statistics
     */
    QGroupBox* createStatisticsDisplay();

    /**
     * @brief Create settings group
     * @return QGroupBox* Group box with settings
     */
    QGroupBox* createSettingsPanel();

    /**
     * @brief Update button states based on execution state
     */
    void updateButtonStates();

    /**
     * @brief Format time duration for display
     * @param milliseconds Time in milliseconds
     * @return QString Formatted time string
     */
    QString formatDuration(int64_t milliseconds) const;

    /**
     * @brief Get color for execution state
     * @param state Execution state
     * @return QString Color name or hex code
     */
    QString getStateColor(Core::ExecutionState state) const;

    // Execution engine
    std::shared_ptr<Core::ExecutionEngine> m_engine;

    // Control buttons
    QPushButton* m_startButton;
    QPushButton* m_stopButton;
    QPushButton* m_pauseButton;
    QPushButton* m_stepButton;
    QPushButton* m_resetButton;

    // State display
    QLabel* m_stateLabel;
    QLabel* m_stateIcon;

    // Statistics displays
    QLCDNumber* m_iterationDisplay;
    QLabel* m_timeDisplay;
    QLabel* m_errorDisplay;
    QLabel* m_rateDisplay;

    // Settings controls
    QDoubleSpinBox* m_executionRateSpinBox;
    QComboBox* m_executionModeComboBox;

    // Status information
    QLabel* m_statusLabel;
    QLabel* m_lastErrorLabel;

    // Update timer for real-time display
    QTimer* m_updateTimer;

    // Constants
    static constexpr int UPDATE_INTERVAL_MS = 100;  ///< Display update rate
};

} // namespace GUI
} // namespace VSE

#endif // VSE_GUI_EXECUTIONCONTROLWIDGET_H

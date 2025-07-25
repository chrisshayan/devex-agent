package com.devex.plugin.settings

import com.intellij.openapi.options.Configurable
import com.intellij.openapi.ui.ValidationInfo
import com.intellij.ui.components.*
import com.intellij.ui.layout.panel
import com.intellij.util.ui.JBUI
import java.awt.BorderLayout
import java.awt.GridBagConstraints
import java.awt.GridBagLayout
import javax.swing.*
import javax.swing.border.TitledBorder

/**
 * Settings Configurable for DevEx Ambient Agent Plugin
 * Provides comprehensive UI for all plugin configuration options
 */
class DevExSettingsConfigurable : Configurable {
    
    private val settings = DevExSettings.getInstance()
    
    // Main panel
    private val mainPanel = JPanel(BorderLayout())
    
    // API Configuration
    private val apiEndpointField = JBTextField()
    private val apiTimeoutSpinner = JSpinner(SpinnerNumberModel(30, 5, 300, 5))
    private val developerIdField = JBTextField()
    
    // Monitoring Configuration
    private val fileMonitoringCheckbox = JBCheckBox("Monitor file changes")
    private val gitMonitoringCheckbox = JBCheckBox("Monitor git operations")
    private val buildMonitoringCheckbox = JBCheckBox("Monitor build events")
    private val monitoringIntervalSpinner = JSpinner(SpinnerNumberModel(60, 10, 3600, 10))
    
    // Notification Settings
    private val notificationsEnabledCheckbox = JBCheckBox("Enable notifications")
    private val criticalIssueNotificationsCheckbox = JBCheckBox("Critical issue alerts")
    private val agentStatusNotificationsCheckbox = JBCheckBox("Agent status changes")
    private val morningBriefNotificationsCheckbox = JBCheckBox("Morning brief ready")
    private val buildFailureNotificationsCheckbox = JBCheckBox("Build failures")
    private val notificationCheckIntervalSpinner = JSpinner(SpinnerNumberModel(30, 10, 300, 10))
    
    // Morning Brief Configuration
    private val autoGenerateMorningBriefCheckbox = JBCheckBox("Auto-generate morning brief")
    private val morningBriefTimeField = JBTextField()
    private val briefRetentionSpinner = JSpinner(SpinnerNumberModel(7, 1, 30, 1))
    
    // Advanced Settings
    private val debugModeCheckbox = JBCheckBox("Enable debug mode")
    private val logLevelCombo = JComboBox(arrayOf("TRACE", "DEBUG", "INFO", "WARN", "ERROR"))
    private val maxEventBufferSpinner = JSpinner(SpinnerNumberModel(1000, 100, 10000, 100))
    private val eventCooldownSpinner = JSpinner(SpinnerNumberModel(2, 1, 60, 1))
    
    // UI Settings
    private val toolWindowLocationCombo = JComboBox(arrayOf("left", "right", "bottom"))
    private val autoOpenToolWindowCheckbox = JBCheckBox("Auto-open tool window")
    private val showDetailedStatusCheckbox = JBCheckBox("Show detailed status")
    
    // Buttons
    private val testConnectionButton = JButton("Test Connection")
    private val resetDefaultsButton = JButton("Reset to Defaults")
    
    override fun getDisplayName(): String = "DevEx Ambient Agent"
    
    override fun createComponent(): JComponent {
        createUI()
        loadSettings()
        setupEventHandlers()
        return mainPanel
    }
    
    private fun createUI() {
        val scrollPane = JBScrollPane()
        val contentPanel = JPanel(GridBagLayout())
        val gbc = GridBagConstraints()
        
        gbc.fill = GridBagConstraints.HORIZONTAL
        gbc.insets = JBUI.insets(5)
        gbc.weightx = 1.0
        
        var row = 0
        
        // API Configuration Section
        gbc.gridy = row++
        contentPanel.add(createApiConfigPanel(), gbc)
        
        // Monitoring Configuration Section
        gbc.gridy = row++
        contentPanel.add(createMonitoringConfigPanel(), gbc)
        
        // Notification Settings Section
        gbc.gridy = row++
        contentPanel.add(createNotificationConfigPanel(), gbc)
        
        // Morning Brief Configuration Section
        gbc.gridy = row++
        contentPanel.add(createMorningBriefConfigPanel(), gbc)
        
        // Advanced Settings Section
        gbc.gridy = row++
        contentPanel.add(createAdvancedConfigPanel(), gbc)
        
        // UI Settings Section
        gbc.gridy = row++
        contentPanel.add(createUIConfigPanel(), gbc)
        
        // Buttons Section
        gbc.gridy = row++
        contentPanel.add(createButtonsPanel(), gbc)
        
        // Add some vertical space at the bottom
        gbc.gridy = row
        gbc.weighty = 1.0
        contentPanel.add(Box.createVerticalGlue(), gbc)
        
        scrollPane.setViewportView(contentPanel)
        mainPanel.add(scrollPane, BorderLayout.CENTER)
    }
    
    private fun createApiConfigPanel(): JPanel {
        val panel = panel {
            titledRow("API Configuration") {
                row("Agent Endpoint:") {
                    apiEndpointField(growX)
                        .comment("URL of the DevEx Agent API (e.g., http://localhost:8000)")
                }
                row("Connection Timeout:") {
                    apiTimeoutSpinner()
                        .comment("Timeout in seconds for API requests")
                }
                row("Developer ID:") {
                    developerIdField(growX)
                        .comment("Unique identifier for this developer")
                }
                row {
                    testConnectionButton()
                }
            }
        }
        return panel
    }
    
    private fun createMonitoringConfigPanel(): JPanel {
        val panel = panel {
            titledRow("Monitoring Configuration") {
                row {
                    fileMonitoringCheckbox()
                }
                row {
                    gitMonitoringCheckbox()
                }
                row {
                    buildMonitoringCheckbox()
                }
                row("Check Interval:") {
                    monitoringIntervalSpinner()
                        .comment("How often to check for events (seconds)")
                }
            }
        }
        return panel
    }
    
    private fun createNotificationConfigPanel(): JPanel {
        val panel = panel {
            titledRow("Notification Settings") {
                row {
                    notificationsEnabledCheckbox()
                        .comment("Master switch for all notifications")
                }
                row {
                    criticalIssueNotificationsCheckbox()
                }
                row {
                    agentStatusNotificationsCheckbox()
                }
                row {
                    morningBriefNotificationsCheckbox()
                }
                row {
                    buildFailureNotificationsCheckbox()
                }
                row("Check Interval:") {
                    notificationCheckIntervalSpinner()
                        .comment("How often to check for critical issues (seconds)")
                }
            }
        }
        return panel
    }
    
    private fun createMorningBriefConfigPanel(): JPanel {
        val panel = panel {
            titledRow("Morning Brief Configuration") {
                row {
                    autoGenerateMorningBriefCheckbox()
                        .comment("Automatically generate morning brief at specified time")
                }
                row("Brief Time (HH:mm):") {
                    morningBriefTimeField()
                        .comment("Time to generate morning brief (24-hour format)")
                }
                row("Retention Days:") {
                    briefRetentionSpinner()
                        .comment("How many days to keep brief history")
                }
            }
        }
        return panel
    }
    
    private fun createAdvancedConfigPanel(): JPanel {
        val panel = panel {
            titledRow("Advanced Settings") {
                row {
                    debugModeCheckbox()
                        .comment("Enable detailed logging and debugging features")
                }
                row("Log Level:") {
                    logLevelCombo()
                }
                row("Event Buffer Size:") {
                    maxEventBufferSpinner()
                        .comment("Maximum number of events to keep in memory")
                }
                row("Event Cooldown:") {
                    eventCooldownSpinner()
                        .comment("Minimum seconds between similar events")
                }
            }
        }
        return panel
    }
    
    private fun createUIConfigPanel(): JPanel {
        val panel = panel {
            titledRow("UI Settings") {
                row("Tool Window Location:") {
                    toolWindowLocationCombo()
                }
                row {
                    autoOpenToolWindowCheckbox()
                        .comment("Automatically open tool window when IDE starts")
                }
                row {
                    showDetailedStatusCheckbox()
                        .comment("Show detailed status information in tool window")
                }
            }
        }
        return panel
    }
    
    private fun createButtonsPanel(): JPanel {
        val panel = JPanel()
        panel.add(testConnectionButton)
        panel.add(Box.createHorizontalStrut(10))
        panel.add(resetDefaultsButton)
        return panel
    }
    
    private fun setupEventHandlers() {
        testConnectionButton.addActionListener {
            testConnection()
        }
        
        resetDefaultsButton.addActionListener {
            resetToDefaults()
        }
        
        notificationsEnabledCheckbox.addActionListener {
            updateNotificationControls()
        }
        
        autoGenerateMorningBriefCheckbox.addActionListener {
            updateMorningBriefControls()
        }
    }
    
    private fun testConnection() {
        testConnectionButton.isEnabled = false
        testConnectionButton.text = "Testing..."
        
        SwingUtilities.invokeLater {
            try {
                val endpoint = apiEndpointField.text.trim()
                // Simple validation
                if (endpoint.isBlank() || (!endpoint.startsWith("http://") && !endpoint.startsWith("https://"))) {
                    JOptionPane.showMessageDialog(
                        mainPanel,
                        "Invalid endpoint URL. Please use http:// or https://",
                        "Connection Test Failed",
                        JOptionPane.ERROR_MESSAGE
                    )
                } else {
                    // In a real implementation, you would test the actual connection here
                    JOptionPane.showMessageDialog(
                        mainPanel,
                        "Connection test feature coming soon!\n\nCurrent endpoint: $endpoint\n\nMake sure the DevEx Agent is running:\npython -m devex_agent.main",
                        "Connection Test",
                        JOptionPane.INFORMATION_MESSAGE
                    )
                }
            } finally {
                testConnectionButton.isEnabled = true
                testConnectionButton.text = "Test Connection"
            }
        }
    }
    
    private fun resetToDefaults() {
        val result = JOptionPane.showConfirmDialog(
            mainPanel,
            "This will reset all settings to their default values. Continue?",
            "Reset to Defaults",
            JOptionPane.YES_NO_OPTION,
            JOptionPane.QUESTION_MESSAGE
        )
        
        if (result == JOptionPane.YES_OPTION) {
            settings.resetToDefaults()
            loadSettings()
        }
    }
    
    private fun updateNotificationControls() {
        val enabled = notificationsEnabledCheckbox.isSelected
        criticalIssueNotificationsCheckbox.isEnabled = enabled
        agentStatusNotificationsCheckbox.isEnabled = enabled
        morningBriefNotificationsCheckbox.isEnabled = enabled
        buildFailureNotificationsCheckbox.isEnabled = enabled
        notificationCheckIntervalSpinner.isEnabled = enabled
    }
    
    private fun updateMorningBriefControls() {
        val enabled = autoGenerateMorningBriefCheckbox.isSelected
        morningBriefTimeField.isEnabled = enabled
        briefRetentionSpinner.isEnabled = enabled
    }
    
    private fun loadSettings() {
        // API Configuration
        apiEndpointField.text = settings.apiEndpoint
        apiTimeoutSpinner.value = settings.apiTimeout
        developerIdField.text = settings.developerId
        
        // Monitoring Configuration
        fileMonitoringCheckbox.isSelected = settings.fileMonitoringEnabled
        gitMonitoringCheckbox.isSelected = settings.gitMonitoringEnabled
        buildMonitoringCheckbox.isSelected = settings.buildMonitoringEnabled
        monitoringIntervalSpinner.value = settings.monitoringInterval
        
        // Notification Settings
        notificationsEnabledCheckbox.isSelected = settings.notificationsEnabled
        criticalIssueNotificationsCheckbox.isSelected = settings.criticalIssueNotifications
        agentStatusNotificationsCheckbox.isSelected = settings.agentStatusNotifications
        morningBriefNotificationsCheckbox.isSelected = settings.morningBriefNotifications
        buildFailureNotificationsCheckbox.isSelected = settings.buildFailureNotifications
        notificationCheckIntervalSpinner.value = settings.notificationCheckInterval
        
        // Morning Brief Configuration
        autoGenerateMorningBriefCheckbox.isSelected = settings.autoGenerateMorningBrief
        morningBriefTimeField.text = settings.morningBriefTime
        briefRetentionSpinner.value = settings.briefRetentionDays
        
        // Advanced Settings
        debugModeCheckbox.isSelected = settings.debugMode
        logLevelCombo.selectedItem = settings.logLevel
        maxEventBufferSpinner.value = settings.maxEventBufferSize
        eventCooldownSpinner.value = settings.eventCooldownSeconds
        
        // UI Settings
        toolWindowLocationCombo.selectedItem = settings.toolWindowLocation
        autoOpenToolWindowCheckbox.isSelected = settings.autoOpenToolWindow
        showDetailedStatusCheckbox.isSelected = settings.showDetailedStatus
        
        // Update control states
        updateNotificationControls()
        updateMorningBriefControls()
    }
    
    override fun isModified(): Boolean {
        return apiEndpointField.text != settings.apiEndpoint ||
               apiTimeoutSpinner.value != settings.apiTimeout ||
               developerIdField.text != settings.developerId ||
               fileMonitoringCheckbox.isSelected != settings.fileMonitoringEnabled ||
               gitMonitoringCheckbox.isSelected != settings.gitMonitoringEnabled ||
               buildMonitoringCheckbox.isSelected != settings.buildMonitoringEnabled ||
               monitoringIntervalSpinner.value != settings.monitoringInterval ||
               notificationsEnabledCheckbox.isSelected != settings.notificationsEnabled ||
               criticalIssueNotificationsCheckbox.isSelected != settings.criticalIssueNotifications ||
               agentStatusNotificationsCheckbox.isSelected != settings.agentStatusNotifications ||
               morningBriefNotificationsCheckbox.isSelected != settings.morningBriefNotifications ||
               buildFailureNotificationsCheckbox.isSelected != settings.buildFailureNotifications ||
               notificationCheckIntervalSpinner.value != settings.notificationCheckInterval ||
               autoGenerateMorningBriefCheckbox.isSelected != settings.autoGenerateMorningBrief ||
               morningBriefTimeField.text != settings.morningBriefTime ||
               briefRetentionSpinner.value != settings.briefRetentionDays ||
               debugModeCheckbox.isSelected != settings.debugMode ||
               logLevelCombo.selectedItem != settings.logLevel ||
               maxEventBufferSpinner.value != settings.maxEventBufferSize ||
               eventCooldownSpinner.value != settings.eventCooldownSeconds ||
               toolWindowLocationCombo.selectedItem != settings.toolWindowLocation ||
               autoOpenToolWindowCheckbox.isSelected != settings.autoOpenToolWindow ||
               showDetailedStatusCheckbox.isSelected != settings.showDetailedStatus
    }
    
    override fun apply() {
        // Validate inputs first
        val validationErrors = validateInputs()
        if (validationErrors.isNotEmpty()) {
            val errorMessage = validationErrors.joinToString("\n")
            JOptionPane.showMessageDialog(
                mainPanel,
                errorMessage,
                "Validation Error",
                JOptionPane.ERROR_MESSAGE
            )
            return
        }
        
        // Save settings
        settings.apiEndpoint = apiEndpointField.text.trim()
        settings.apiTimeout = apiTimeoutSpinner.value as Int
        settings.developerId = developerIdField.text.trim()
        settings.fileMonitoringEnabled = fileMonitoringCheckbox.isSelected
        settings.gitMonitoringEnabled = gitMonitoringCheckbox.isSelected
        settings.buildMonitoringEnabled = buildMonitoringCheckbox.isSelected
        settings.monitoringInterval = monitoringIntervalSpinner.value as Int
        settings.notificationsEnabled = notificationsEnabledCheckbox.isSelected
        settings.criticalIssueNotifications = criticalIssueNotificationsCheckbox.isSelected
        settings.agentStatusNotifications = agentStatusNotificationsCheckbox.isSelected
        settings.morningBriefNotifications = morningBriefNotificationsCheckbox.isSelected
        settings.buildFailureNotifications = buildFailureNotificationsCheckbox.isSelected
        settings.notificationCheckInterval = notificationCheckIntervalSpinner.value as Int
        settings.autoGenerateMorningBrief = autoGenerateMorningBriefCheckbox.isSelected
        settings.morningBriefTime = morningBriefTimeField.text.trim()
        settings.briefRetentionDays = briefRetentionSpinner.value as Int
        settings.debugMode = debugModeCheckbox.isSelected
        settings.logLevel = logLevelCombo.selectedItem as String
        settings.maxEventBufferSize = maxEventBufferSpinner.value as Int
        settings.eventCooldownSeconds = eventCooldownSpinner.value as Int
        settings.toolWindowLocation = toolWindowLocationCombo.selectedItem as String
        settings.autoOpenToolWindow = autoOpenToolWindowCheckbox.isSelected
        settings.showDetailedStatus = showDetailedStatusCheckbox.isSelected
    }
    
    private fun validateInputs(): List<String> {
        val errors = mutableListOf<String>()
        
        // Validate API endpoint
        val endpoint = apiEndpointField.text.trim()
        if (endpoint.isBlank()) {
            errors.add("API endpoint cannot be empty")
        } else if (!endpoint.startsWith("http://") && !endpoint.startsWith("https://")) {
            errors.add("API endpoint must start with http:// or https://")
        }
        
        // Validate developer ID
        val developerId = developerIdField.text.trim()
        if (developerId.isBlank()) {
            errors.add("Developer ID cannot be empty")
        } else if (!developerId.matches(Regex("[a-zA-Z0-9_-]+"))) {
            errors.add("Developer ID can only contain letters, numbers, underscores, and hyphens")
        }
        
        // Validate morning brief time format
        if (autoGenerateMorningBriefCheckbox.isSelected) {
            val timeText = morningBriefTimeField.text.trim()
            if (!timeText.matches(Regex("^([01]?[0-9]|2[0-3]):[0-5][0-9]$"))) {
                errors.add("Morning brief time must be in HH:mm format (e.g., 09:00)")
            }
        }
        
        return errors
    }
    
    override fun reset() {
        loadSettings()
    }
} 
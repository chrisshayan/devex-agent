package com.devex.plugin.ui

import com.intellij.openapi.project.Project
import com.intellij.openapi.wm.ToolWindow
import com.intellij.openapi.wm.ToolWindowFactory
import com.intellij.ui.content.ContentFactory
import com.intellij.ui.components.JBScrollPane
import com.intellij.ui.JBColor
import com.intellij.util.ui.JBUI
import com.devex.plugin.services.AmbientAgentService
import com.devex.plugin.services.MorningBrief
import kotlinx.coroutines.*
import java.awt.*
import java.awt.event.ActionEvent
import java.awt.event.ActionListener
import javax.swing.*
import javax.swing.border.EmptyBorder
import java.text.SimpleDateFormat
import java.util.*

/**
 * Enhanced Tool Window Factory for DevEx Ambient Agent
 * Provides comprehensive UI for morning briefs, status, and controls
 */
class DevExToolWindowFactory : ToolWindowFactory {
    
    override fun createToolWindowContent(project: Project, toolWindow: ToolWindow) {
        val toolWindowContent = DevExToolWindowContent(project)
        val content = ContentFactory.getInstance().createContent(toolWindowContent.contentPanel, "", false)
        toolWindow.contentManager.addContent(content)
    }
}

/**
 * Enhanced content panel with morning briefs, status display, and controls
 */
class DevExToolWindowContent(private val project: Project) {
    val contentPanel: JPanel = JPanel(BorderLayout())
    private val agentService = AmbientAgentService.getInstance()
    private val uiScope = CoroutineScope(Dispatchers.Main + SupervisorJob())
    
    // UI Components
    private val statusPanel = JPanel(FlowLayout(FlowLayout.LEFT))
    private val statusLabel = JLabel("⏳ Checking status...")
    private val lastUpdateLabel = JLabel("Never updated")
    private lateinit var briefScrollPane: JBScrollPane
    private val briefContentPanel = JPanel()
    private val controlsPanel = JPanel(FlowLayout())
    
    // Control buttons
    private val refreshButton = JButton("🔄 Refresh Brief")
    private val statusButton = JButton("📊 Check Status")
    private val settingsButton = JButton("⚙️ Settings")
    
    init {
        setupUI()
        startPeriodicUpdates()
        uiScope.launch {
            loadInitialData()
        }
    }
    
    private fun setupUI() {
        contentPanel.border = EmptyBorder(10, 10, 10, 10)
        
        // Header with title and status
        val headerPanel = JPanel(BorderLayout())
        val titleLabel = JLabel("DevEx Ambient Agent")
        titleLabel.font = titleLabel.font.deriveFont(Font.BOLD, 16f)
        headerPanel.add(titleLabel, BorderLayout.WEST)
        
        // Status indicator
        setupStatusPanel()
        headerPanel.add(statusPanel, BorderLayout.EAST)
        
        // Main content area for morning brief
        briefContentPanel.layout = BoxLayout(briefContentPanel, BoxLayout.Y_AXIS)
        briefContentPanel.border = EmptyBorder(10, 0, 10, 0)
        briefScrollPane = JBScrollPane(briefContentPanel)
        briefScrollPane.preferredSize = Dimension(400, 300)
        
        // Controls panel
        setupControlsPanel()
        
        // Layout
        contentPanel.add(headerPanel, BorderLayout.NORTH)
        contentPanel.add(briefScrollPane, BorderLayout.CENTER)
        contentPanel.add(controlsPanel, BorderLayout.SOUTH)
        
        // Initial content
        showWelcomeMessage()
    }
    
    private fun setupStatusPanel() {
        statusPanel.removeAll()
        statusLabel.foreground = JBColor.GRAY
        statusPanel.add(statusLabel)
        statusPanel.add(Box.createHorizontalStrut(10))
        lastUpdateLabel.font = lastUpdateLabel.font.deriveFont(Font.PLAIN, 10f)
        lastUpdateLabel.foreground = JBColor.GRAY
        statusPanel.add(lastUpdateLabel)
    }
    
    private fun setupControlsPanel() {
        // Refresh button
        refreshButton.addActionListener {
            uiScope.launch {
                refreshMorningBrief()
            }
        }
        
        // Status button
        statusButton.addActionListener {
            uiScope.launch {
                checkAgentStatus()
            }
        }
        
        // Settings button (placeholder for now)
        settingsButton.addActionListener {
            showSettingsDialog()
        }
        
        controlsPanel.add(refreshButton)
        controlsPanel.add(statusButton)
        controlsPanel.add(settingsButton)
    }
    
    private fun showWelcomeMessage() {
        briefContentPanel.removeAll()
        
        val welcomePanel = JPanel()
        welcomePanel.layout = BoxLayout(welcomePanel, BoxLayout.Y_AXIS)
        welcomePanel.alignmentX = Component.CENTER_ALIGNMENT
        
        val titleLabel = JLabel("🌅 DevEx Ambient Agent")
        titleLabel.font = titleLabel.font.deriveFont(Font.BOLD, 18f)
        titleLabel.alignmentX = Component.CENTER_ALIGNMENT
        
        val descLabel = JLabel("<html><center>Your intelligent development assistant is ready.<br/>Click 'Refresh Brief' to get your personalized morning summary.</center></html>")
        descLabel.alignmentX = Component.CENTER_ALIGNMENT
        
        val statusLabel = JLabel("📡 Agent Status: Checking...")
        statusLabel.alignmentX = Component.CENTER_ALIGNMENT
        statusLabel.foreground = JBColor.GRAY
        
        welcomePanel.add(Box.createVerticalStrut(20))
        welcomePanel.add(titleLabel)
        welcomePanel.add(Box.createVerticalStrut(10))
        welcomePanel.add(descLabel)
        welcomePanel.add(Box.createVerticalStrut(10))
        welcomePanel.add(statusLabel)
        welcomePanel.add(Box.createVerticalStrut(20))
        
        briefContentPanel.add(welcomePanel)
        briefContentPanel.revalidate()
        briefContentPanel.repaint()
    }
    
    private suspend fun loadInitialData() {
        checkAgentStatus()
    }
    
    private suspend fun refreshMorningBrief() {
        withContext(Dispatchers.Main) {
            refreshButton.isEnabled = false
            refreshButton.text = "🔄 Loading..."
            updateStatus("⏳ Generating morning brief...", JBColor.BLUE)
        }
        
        try {
            val brief = agentService.requestMorningBrief()
            withContext(Dispatchers.Main) {
                if (brief != null) {
                    displayMorningBrief(brief)
                    updateStatus("✅ Brief updated", JBColor.GREEN)
                } else {
                    showErrorMessage("Failed to generate morning brief. Check agent connection.")
                    updateStatus("❌ Brief failed", JBColor.RED)
                }
            }
        } catch (e: Exception) {
            withContext(Dispatchers.Main) {
                showErrorMessage("Error: ${e.message}")
                updateStatus("❌ Error", JBColor.RED)
            }
        } finally {
            withContext(Dispatchers.Main) {
                refreshButton.isEnabled = true
                refreshButton.text = "🔄 Refresh Brief"
                updateLastUpdateTime()
            }
        }
    }
    
    private suspend fun checkAgentStatus() {
        try {
            val status = agentService.getAgentStatus()
            withContext(Dispatchers.Main) {
                if (status != null) {
                    val statusText = when (status.status) {
                        "active" -> "✅ Active"
                        "disconnected" -> "🔴 Disconnected"
                        "error" -> "❌ Error"
                        else -> "⚠️ ${status.status}"
                    }
                    
                    val statusColor = when (status.status) {
                        "active" -> JBColor.GREEN
                        "disconnected" -> JBColor.RED
                        "error" -> JBColor.RED
                        else -> JBColor.ORANGE
                    }
                    
                    updateStatus("$statusText (${status.eventsCount} events)", statusColor)
                } else {
                    updateStatus("🔴 Agent unreachable", JBColor.RED)
                }
            }
        } catch (e: Exception) {
            withContext(Dispatchers.Main) {
                updateStatus("❌ Connection error", JBColor.RED)
            }
        }
    }
    
    private fun displayMorningBrief(brief: MorningBrief) {
        briefContentPanel.removeAll()
        
        val briefPanel = JPanel()
        briefPanel.layout = BoxLayout(briefPanel, BoxLayout.Y_AXIS)
        briefPanel.border = EmptyBorder(5, 5, 5, 5)
        
        // Header
        val headerLabel = JLabel("🌅 Morning Brief")
        headerLabel.font = headerLabel.font.deriveFont(Font.BOLD, 16f)
        briefPanel.add(headerLabel)
        briefPanel.add(Box.createVerticalStrut(5))
        
        // Greeting
        if (!brief.greeting.isNullOrBlank()) {
            val greetingLabel = JLabel("<html><i>${brief.greeting}</i></html>")
            greetingLabel.foreground = JBColor.BLUE
            briefPanel.add(greetingLabel)
            briefPanel.add(Box.createVerticalStrut(10))
        }
        
        // Summary
        val summaryLabel = JLabel("<html><b>Summary:</b><br/>${brief.summary}</html>")
        summaryLabel.border = JBUI.Borders.empty(5, 10)
        briefPanel.add(summaryLabel)
        briefPanel.add(Box.createVerticalStrut(10))
        
        // Activity Overview
        if (brief.activityOverview.isNotEmpty()) {
            briefPanel.add(createSectionLabel("📊 Activity Overview"))
            val activityPanel = createActivityOverviewPanel(brief.activityOverview)
            briefPanel.add(activityPanel)
            briefPanel.add(Box.createVerticalStrut(10))
        }
        
        // Critical Items
        if (brief.criticalItems.isNotEmpty()) {
            briefPanel.add(createSectionLabel("🚨 Critical Items"))
            for (item in brief.criticalItems.take(5)) {
                val itemPanel = createCriticalItemPanel(item)
                briefPanel.add(itemPanel)
            }
            briefPanel.add(Box.createVerticalStrut(10))
        }
        
        // Suggestions
        if (brief.suggestions.isNotEmpty()) {
            briefPanel.add(createSectionLabel("💡 Suggestions"))
            for (suggestion in brief.suggestions.take(5)) {
                val suggestionPanel = createSuggestionPanel(suggestion)
                briefPanel.add(suggestionPanel)
            }
        }
        
        briefContentPanel.add(briefPanel)
        briefContentPanel.revalidate()
        briefContentPanel.repaint()
    }
    
    private fun createSectionLabel(text: String): JLabel {
        val label = JLabel(text)
        label.font = label.font.deriveFont(Font.BOLD, 14f)
        label.border = EmptyBorder(5, 0, 5, 0)
        return label
    }
    
    private fun createActivityOverviewPanel(overview: Map<String, Any>): JPanel {
        val panel = JPanel(GridLayout(0, 2, 5, 2))
        panel.border = JBUI.Borders.empty(5, 15)
        
        for ((key, value) in overview) {
            val keyLabel = JLabel("${key.replace("_", " ").capitalize()}:")
            val valueLabel = JLabel(value.toString())
            valueLabel.foreground = JBColor.BLUE
            panel.add(keyLabel)
            panel.add(valueLabel)
        }
        
        return panel
    }
    
    private fun createCriticalItemPanel(item: Map<String, Any>): JPanel {
        val panel = JPanel(BorderLayout())
        panel.border = JBUI.Borders.empty(2, 15, 2, 5)
        
        val priorityIcon = when (item["priority"]?.toString()?.lowercase()) {
            "critical" -> "🔴"
            "high" -> "🟡"
            "medium" -> "🟠"
            else -> "⚪"
        }
        
        val titleLabel = JLabel("$priorityIcon ${item["title"] ?: "Critical Item"}")
        titleLabel.font = titleLabel.font.deriveFont(Font.BOLD)
        
        val descLabel = JLabel("<html>${item["description"] ?: ""}</html>")
        descLabel.foreground = JBColor.GRAY
        
        panel.add(titleLabel, BorderLayout.NORTH)
        panel.add(descLabel, BorderLayout.CENTER)
        
        return panel
    }
    
    private fun createSuggestionPanel(suggestion: Map<String, Any>): JPanel {
        val panel = JPanel(BorderLayout())
        panel.border = JBUI.Borders.empty(2, 15, 2, 5)
        
        val titleLabel = JLabel("• ${suggestion["title"] ?: "Suggestion"}")
        titleLabel.font = titleLabel.font.deriveFont(Font.BOLD)
        
        val descLabel = JLabel("<html>${suggestion["description"] ?: ""}</html>")
        descLabel.foreground = JBColor.GRAY
        
        panel.add(titleLabel, BorderLayout.NORTH)
        panel.add(descLabel, BorderLayout.CENTER)
        
        return panel
    }
    
    private fun showErrorMessage(message: String) {
        briefContentPanel.removeAll()
        
        val errorPanel = JPanel()
        errorPanel.layout = BoxLayout(errorPanel, BoxLayout.Y_AXIS)
        errorPanel.alignmentX = Component.CENTER_ALIGNMENT
        
        val errorLabel = JLabel("❌ Error")
        errorLabel.font = errorLabel.font.deriveFont(Font.BOLD, 16f)
        errorLabel.foreground = JBColor.RED
        errorLabel.alignmentX = Component.CENTER_ALIGNMENT
        
        val messageLabel = JLabel("<html><center>$message</center></html>")
        messageLabel.alignmentX = Component.CENTER_ALIGNMENT
        
        val helpLabel = JLabel("<html><center>Make sure the DevEx Agent is running:<br/><code>python -m devex_agent.main</code></center></html>")
        helpLabel.foreground = JBColor.GRAY
        helpLabel.alignmentX = Component.CENTER_ALIGNMENT
        
        errorPanel.add(Box.createVerticalStrut(20))
        errorPanel.add(errorLabel)
        errorPanel.add(Box.createVerticalStrut(10))
        errorPanel.add(messageLabel)
        errorPanel.add(Box.createVerticalStrut(10))
        errorPanel.add(helpLabel)
        
        briefContentPanel.add(errorPanel)
        briefContentPanel.revalidate()
        briefContentPanel.repaint()
    }
    
    private fun updateStatus(text: String, color: Color) {
        statusLabel.text = text
        statusLabel.foreground = color
        statusPanel.revalidate()
        statusPanel.repaint()
    }
    
    private fun updateLastUpdateTime() {
        val timeFormat = SimpleDateFormat("HH:mm:ss")
        lastUpdateLabel.text = "Updated: ${timeFormat.format(Date())}"
    }
    
    private fun showSettingsDialog() {
        JOptionPane.showMessageDialog(
            contentPanel,
            "Settings panel coming soon!\n\nFor now, configure the agent via:\n• .env file in project root\n• Agent endpoint: http://localhost:8000",
            "DevEx Agent Settings",
            JOptionPane.INFORMATION_MESSAGE
        )
    }
    
    private fun startPeriodicUpdates() {
        uiScope.launch {
            while (true) {
                delay(60000) // Check every minute
                try {
                    checkAgentStatus()
                } catch (e: Exception) {
                    // Ignore errors in background updates
                }
            }
        }
    }
    
    fun dispose() {
        uiScope.cancel()
    }
} 
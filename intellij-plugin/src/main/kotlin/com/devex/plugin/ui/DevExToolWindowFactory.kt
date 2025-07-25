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
import com.devex.plugin.services.CriticalItem
import com.devex.plugin.services.Suggestion
import com.devex.plugin.services.FileIssue
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
 * Fixed layout to prevent horizontal scrolling and improved content structure
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
        
        // Main content area for morning brief - Fixed layout
        briefContentPanel.layout = BoxLayout(briefContentPanel, BoxLayout.Y_AXIS)
        briefContentPanel.border = EmptyBorder(10, 0, 10, 0)
        
        // Create scroll pane with proper sizing
        briefScrollPane = JBScrollPane(briefContentPanel)
        briefScrollPane.horizontalScrollBarPolicy = JScrollPane.HORIZONTAL_SCROLLBAR_NEVER
        briefScrollPane.verticalScrollBarPolicy = JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED
        briefScrollPane.border = JBUI.Borders.empty()
        
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
        
        val welcomePanel = createConstrainedPanel()
        
        val titleLabel = JLabel("🌅 DevEx Ambient Agent")
        titleLabel.font = titleLabel.font.deriveFont(Font.BOLD, 18f)
        titleLabel.alignmentX = Component.CENTER_ALIGNMENT
        
        val descText = """
            <html><div style='text-align: center; width: 300px;'>
            Your intelligent development assistant is ready.<br/>
            Click 'Refresh Brief' to get your personalized morning summary.
            </div></html>
        """.trimIndent()
        
        val descLabel = JLabel(descText)
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
        
        val briefPanel = createConstrainedPanel()
        
        // Header
        val headerLabel = JLabel("🌅 Morning Brief")
        headerLabel.font = headerLabel.font.deriveFont(Font.BOLD, 16f)
        briefPanel.add(headerLabel)
        briefPanel.add(Box.createVerticalStrut(5))
        
        // Generated time
        if (brief.generatedAt.isNotBlank()) {
            val timeLabel = JLabel("Generated: ${formatGeneratedTime(brief.generatedAt)}")
            timeLabel.font = timeLabel.font.deriveFont(Font.PLAIN, 10f)
            timeLabel.foreground = JBColor.GRAY
            briefPanel.add(timeLabel)
            briefPanel.add(Box.createVerticalStrut(10))
        }
        
        // Greeting
        if (!brief.greeting.isNullOrBlank()) {
            val greetingPanel = createWrappedTextPanel(brief.greeting, JBColor.BLUE, Font.ITALIC)
            briefPanel.add(greetingPanel)
            briefPanel.add(Box.createVerticalStrut(10))
        }
        
        // Summary
        if (brief.summary.isNotBlank()) {
            briefPanel.add(createSectionLabel("📋 Summary"))
            val summaryPanel = createWrappedTextPanel(brief.summary, null, Font.PLAIN)
            briefPanel.add(summaryPanel)
            briefPanel.add(Box.createVerticalStrut(15))
        }
        
        // Activity Overview
        if (brief.activityOverview.isNotEmpty()) {
            briefPanel.add(createSectionLabel("📊 Activity Overview"))
            val activityPanel = createActivityOverviewPanel(brief.activityOverview)
            briefPanel.add(activityPanel)
            briefPanel.add(Box.createVerticalStrut(15))
        }
        
        // Critical Items with detailed view
        if (brief.criticalItems.isNotEmpty()) {
            briefPanel.add(createSectionLabel("🚨 Critical Items"))
            val criticalPanel = createDetailedCriticalItemsPanel(brief.criticalItems)
            briefPanel.add(criticalPanel)
            briefPanel.add(Box.createVerticalStrut(15))
        }
        
        // Suggestions with enhanced display
        if (brief.suggestions.isNotEmpty()) {
            briefPanel.add(createSectionLabel("💡 Suggestions"))
            val suggestionsPanel = createDetailedSuggestionsPanel(brief.suggestions)
            briefPanel.add(suggestionsPanel)
            briefPanel.add(Box.createVerticalStrut(15))
        }
        
        // Insights
        if (brief.insights.isNotEmpty()) {
            briefPanel.add(createSectionLabel("🔍 Insights"))
            val insightsPanel = createInsightsPanel(brief.insights)
            briefPanel.add(insightsPanel)
        }
        
        briefContentPanel.add(briefPanel)
        briefContentPanel.revalidate()
        briefContentPanel.repaint()
    }
    
    private fun createConstrainedPanel(): JPanel {
        val panel = JPanel()
        panel.layout = BoxLayout(panel, BoxLayout.Y_AXIS)
        panel.border = EmptyBorder(5, 5, 5, 5)
        panel.alignmentX = Component.LEFT_ALIGNMENT
        return panel
    }
    
    private fun createWrappedTextPanel(text: String, color: Color?, fontStyle: Int): JPanel {
        val panel = JPanel(BorderLayout())
        panel.border = JBUI.Borders.empty(5, 10, 5, 10)
        
        val textArea = JTextArea(text)
        textArea.isEditable = false
        textArea.isOpaque = false
        textArea.lineWrap = true
        textArea.wrapStyleWord = true
        textArea.font = textArea.font.deriveFont(fontStyle)
        
        if (color != null) {
            textArea.foreground = color
        }
        
        panel.add(textArea, BorderLayout.CENTER)
        return panel
    }
    
    private fun createDetailedCriticalItemsPanel(items: List<CriticalItem>): JPanel {
        val panel = createConstrainedPanel()
        
        for ((index, item) in items.withIndex()) {
            val itemPanel = createDetailedCriticalItemPanel(item, index + 1)
            panel.add(itemPanel)
            
            if (index < items.size - 1) {
                panel.add(Box.createVerticalStrut(8))
            }
        }
        
        return panel
    }
    
    private fun createDetailedCriticalItemPanel(item: CriticalItem, index: Int): JPanel {
        val panel = JPanel(BorderLayout())
        panel.border = JBUI.Borders.compound(
            JBUI.Borders.customLine(JBColor.GRAY, 0, 0, 1, 0),
            JBUI.Borders.empty(8, 15, 8, 5)
        )
        
        val leftPanel = JPanel()
        leftPanel.layout = BoxLayout(leftPanel, BoxLayout.Y_AXIS)
        
        // Priority indicator and title
        val priorityIcon = when (item.priority.lowercase()) {
            "critical" -> "🔴"
            "high" -> "🟡"
            "medium" -> "🟠"
            "low" -> "🟢"
            else -> "⚪"
        }
        
        val titleText = "${index}. $priorityIcon ${item.title}"
        val titleLabel = JLabel(titleText)
        titleLabel.font = titleLabel.font.deriveFont(Font.BOLD, 13f)
        leftPanel.add(titleLabel)
        
        // Count indicator for multiple issues
        if (item.count > 0) {
            val countLabel = JLabel("Found ${item.count} issues")
            countLabel.font = countLabel.font.deriveFont(Font.BOLD, 11f)
            countLabel.foreground = JBColor.RED
            leftPanel.add(countLabel)
            leftPanel.add(Box.createVerticalStrut(3))
        }
        
        // Description with proper wrapping
        if (item.description.isNotBlank()) {
            leftPanel.add(Box.createVerticalStrut(5))
            val descPanel = createWrappedTextPanel(item.description, JBColor.GRAY, Font.PLAIN)
            leftPanel.add(descPanel)
        }
        
        // File details if available
        if (item.files.isNotEmpty()) {
            leftPanel.add(Box.createVerticalStrut(5))
            val filesPanel = createFileIssuesPanel(item.files, maxDisplay = 3)
            leftPanel.add(filesPanel)
        }
        
        // Type and priority details
        leftPanel.add(Box.createVerticalStrut(5))
        val detailsText = "Type: ${item.type} • Priority: ${item.priority}"
        val detailsLabel = JLabel(detailsText)
        detailsLabel.font = detailsLabel.font.deriveFont(Font.PLAIN, 10f)
        detailsLabel.foreground = JBColor.GRAY
        leftPanel.add(detailsLabel)
        
        panel.add(leftPanel, BorderLayout.CENTER)
        
        // Right panel with action buttons
        val rightPanel = JPanel()
        rightPanel.layout = BoxLayout(rightPanel, BoxLayout.Y_AXIS)
        
        // Action required button
        if (item.actionRequired) {
            val actionButton = JButton("⚡")
            actionButton.toolTipText = "Action Required"
            actionButton.preferredSize = Dimension(30, 25)
            actionButton.addActionListener {
                showDetailedCriticalItemInfo(item)
            }
            rightPanel.add(actionButton)
        }
        
        // View details button
        if (item.files.isNotEmpty() || item.count > 0) {
            if (item.actionRequired) rightPanel.add(Box.createVerticalStrut(5))
            val detailsButton = JButton("📄")
            detailsButton.toolTipText = "View File Details"
            detailsButton.preferredSize = Dimension(30, 25)
            detailsButton.addActionListener {
                showFileDetailsDialog(item.files, item.title)
            }
            rightPanel.add(detailsButton)
        }
        
        if (rightPanel.componentCount > 0) {
            panel.add(rightPanel, BorderLayout.EAST)
        }
        
        return panel
    }
    
    private fun createDetailedSuggestionsPanel(suggestions: List<Suggestion>): JPanel {
        val panel = createConstrainedPanel()
        
        for ((index, suggestion) in suggestions.withIndex()) {
            val suggestionPanel = createDetailedSuggestionPanel(suggestion, index + 1)
            panel.add(suggestionPanel)
            
            if (index < suggestions.size - 1) {
                panel.add(Box.createVerticalStrut(8))
            }
        }
        
        return panel
    }
    
    private fun createDetailedSuggestionPanel(suggestion: Suggestion, index: Int): JPanel {
        val panel = JPanel(BorderLayout())
        panel.border = JBUI.Borders.empty(5, 15, 5, 5)
        
        val leftPanel = JPanel()
        leftPanel.layout = BoxLayout(leftPanel, BoxLayout.Y_AXIS)
        
        // Title with priority indicator
        val priorityIcon = when (suggestion.priority.lowercase()) {
            "high" -> "🔥"
            "medium" -> "⚡"
            "low" -> "💡"
            else -> "💭"
        }
        
        val titleText = "${index}. $priorityIcon ${suggestion.title}"
        val titleLabel = JLabel(titleText)
        titleLabel.font = titleLabel.font.deriveFont(Font.BOLD, 12f)
        leftPanel.add(titleLabel)
        
        // Description
        if (suggestion.description.isNotBlank()) {
            leftPanel.add(Box.createVerticalStrut(5))
            val descPanel = createWrappedTextPanel(suggestion.description, JBColor.GRAY, Font.PLAIN)
            leftPanel.add(descPanel)
        }
        
        // File details if available
        if (suggestion.files.isNotEmpty()) {
            leftPanel.add(Box.createVerticalStrut(5))
            val filesPanel = createFileIssuesPanel(suggestion.files, maxDisplay = 2)
            leftPanel.add(filesPanel)
        }
        
        // Type and action details
        leftPanel.add(Box.createVerticalStrut(5))
        val detailsText = buildString {
            append("Type: ${suggestion.type}")
            if (suggestion.action != null) {
                append(" • Action: ${suggestion.action}")
            }
            append(" • Priority: ${suggestion.priority}")
        }
        val detailsLabel = JLabel(detailsText)
        detailsLabel.font = detailsLabel.font.deriveFont(Font.PLAIN, 10f)
        detailsLabel.foreground = JBColor.BLUE
        leftPanel.add(detailsLabel)
        
        panel.add(leftPanel, BorderLayout.CENTER)
        
        // Right panel with action buttons
        val rightPanel = JPanel()
        rightPanel.layout = BoxLayout(rightPanel, BoxLayout.Y_AXIS)
        
        // Info button for more details
        val infoButton = JButton("ℹ️")
        infoButton.toolTipText = "More Details"
        infoButton.preferredSize = Dimension(30, 25)
        infoButton.addActionListener {
            showDetailedSuggestionInfo(suggestion)
        }
        rightPanel.add(infoButton)
        
        // View files button if files available
        if (suggestion.files.isNotEmpty()) {
            rightPanel.add(Box.createVerticalStrut(5))
            val filesButton = JButton("📄")
            filesButton.toolTipText = "View Related Files"
            filesButton.preferredSize = Dimension(30, 25)
            filesButton.addActionListener {
                showFileDetailsDialog(suggestion.files, suggestion.title)
            }
            rightPanel.add(filesButton)
        }
        
        panel.add(rightPanel, BorderLayout.EAST)
        
        return panel
    }
    
    private fun createInsightsPanel(insights: Map<String, Any>): JPanel {
        val panel = JPanel(GridBagLayout())
        panel.border = JBUI.Borders.empty(5, 15)
        
        val gbc = GridBagConstraints()
        gbc.anchor = GridBagConstraints.WEST
        gbc.insets = Insets(2, 0, 2, 10)
        
        var row = 0
        for ((key, value) in insights) {
            gbc.gridx = 0
            gbc.gridy = row
            gbc.weightx = 0.0
            
            val keyLabel = JLabel("${formatInsightKey(key)}:")
            keyLabel.font = keyLabel.font.deriveFont(Font.BOLD, 11f)
            panel.add(keyLabel, gbc)
            
            gbc.gridx = 1
            gbc.weightx = 1.0
            
            val valueLabel = JLabel(formatInsightValue(key, value))
            valueLabel.foreground = when (key) {
                "code_quality_score" -> if ((value as? Number)?.toInt() ?: 0 < 0) JBColor.RED else JBColor.GREEN
                "build_health" -> if ((value as? Number)?.toInt() ?: 0 > 0) JBColor.GREEN else JBColor.RED
                else -> JBColor.BLUE
            }
            panel.add(valueLabel, gbc)
            
            row++
        }
        
        return panel
    }
    
    private fun createSectionLabel(text: String): JLabel {
        val label = JLabel(text)
        label.font = label.font.deriveFont(Font.BOLD, 14f)
        label.border = EmptyBorder(10, 0, 5, 0)
        label.alignmentX = Component.LEFT_ALIGNMENT
        return label
    }
    
    private fun createActivityOverviewPanel(overview: Map<String, Any>): JPanel {
        val panel = JPanel(GridBagLayout())
        panel.border = JBUI.Borders.empty(5, 15)
        
        val gbc = GridBagConstraints()
        gbc.anchor = GridBagConstraints.WEST
        gbc.insets = Insets(2, 0, 2, 10)
        
        var row = 0
        for ((key, value) in overview) {
            gbc.gridx = 0
            gbc.gridy = row
            gbc.weightx = 0.0
            
            val keyLabel = JLabel("${formatActivityKey(key)}:")
            keyLabel.font = keyLabel.font.deriveFont(Font.BOLD, 11f)
            panel.add(keyLabel, gbc)
            
            gbc.gridx = 1
            gbc.weightx = 1.0
            
            val valueLabel = JLabel(value.toString())
            valueLabel.foreground = JBColor.BLUE
            panel.add(valueLabel, gbc)
            
            row++
        }
        
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

    private fun createFileIssuesPanel(files: List<FileIssue>, maxDisplay: Int = 3): JPanel {
        val panel = JPanel()
        panel.layout = BoxLayout(panel, BoxLayout.Y_AXIS)
        panel.border = JBUI.Borders.empty(3, 10, 3, 0)
        
        val displayFiles = files.take(maxDisplay)
        
        for (file in displayFiles) {
            val filePanel = JPanel(FlowLayout(FlowLayout.LEFT, 0, 2))
            
            // File icon and path
            val fileLabel = JLabel("📄 ${getFileName(file.filePath)}")
            fileLabel.font = fileLabel.font.deriveFont(Font.BOLD, 10f)
            fileLabel.foreground = JBColor.BLUE
            filePanel.add(fileLabel)
            
            // Line number if available
            if (file.lineNumber != null) {
                val lineLabel = JLabel(":${file.lineNumber}")
                lineLabel.font = lineLabel.font.deriveFont(Font.PLAIN, 10f)
                lineLabel.foreground = JBColor.GRAY
                filePanel.add(lineLabel)
            }
            
            // Severity indicator
            val severityIcon = when (file.severity.lowercase()) {
                "critical", "high" -> "🔴"
                "medium" -> "🟡"
                "low" -> "🟢"
                else -> "⚪"
            }
            val severityLabel = JLabel(" $severityIcon")
            filePanel.add(severityLabel)
            
            panel.add(filePanel)
        }
        
        // Show "and X more" if there are additional files
        if (files.size > maxDisplay) {
            val moreLabel = JLabel("... and ${files.size - maxDisplay} more files")
            moreLabel.font = moreLabel.font.deriveFont(Font.ITALIC, 9f)
            moreLabel.foreground = JBColor.GRAY
            val morePanel = JPanel(FlowLayout(FlowLayout.LEFT, 10, 2))
            morePanel.add(moreLabel)
            panel.add(morePanel)
        }
        
        return panel
    }
    
    private fun showDetailedCriticalItemInfo(item: CriticalItem) {
        val details = buildString {
            appendLine("Critical Item: ${item.title}")
            appendLine("=".repeat(50))
            appendLine()
            appendLine("Type: ${item.type}")
            appendLine("Priority: ${item.priority}")
            appendLine("Action Required: ${if (item.actionRequired) "Yes" else "No"}")
            if (item.count > 0) {
                appendLine("Issues Found: ${item.count}")
            }
            appendLine()
            appendLine("Description:")
            appendLine(item.description)
            
            if (item.files.isNotEmpty()) {
                appendLine()
                appendLine("Affected Files:")
                appendLine("-".repeat(20))
                for ((index, file) in item.files.withIndex()) {
                    appendLine("${index + 1}. ${file.filePath}")
                    if (file.lineNumber != null) {
                        appendLine("   Line: ${file.lineNumber}")
                    }
                    if (file.description.isNotBlank()) {
                        appendLine("   Issue: ${file.description}")
                    }
                    if (file.severity.isNotBlank()) {
                        appendLine("   Severity: ${file.severity}")
                    }
                    if (file.ruleId != null) {
                        appendLine("   Rule: ${file.ruleId}")
                    }
                    appendLine()
                }
            }
            
            if (item.metadata.isNotEmpty()) {
                appendLine("Additional Information:")
                appendLine("-".repeat(20))
                for ((key, value) in item.metadata) {
                    appendLine("${key.replace("_", " ").capitalizeWords()}: $value")
                }
            }
            
            appendLine()
            appendLine("Recommendation:")
            appendLine("Review the affected files and address the ${item.type} concerns.")
            appendLine("Focus on ${item.priority} priority items first.")
        }
        
        showDetailsDialog(details, "Critical Item Details")
    }
    
    private fun showDetailedSuggestionInfo(suggestion: Suggestion) {
        val details = buildString {
            appendLine("Suggestion: ${suggestion.title}")
            appendLine("=".repeat(50))
            appendLine()
            appendLine("Type: ${suggestion.type}")
            appendLine("Priority: ${suggestion.priority}")
            if (suggestion.action != null) {
                appendLine("Recommended Action: ${suggestion.action}")
            }
            appendLine()
            appendLine("Description:")
            appendLine(suggestion.description)
            
            if (suggestion.files.isNotEmpty()) {
                appendLine()
                appendLine("Related Files:")
                appendLine("-".repeat(20))
                for ((index, file) in suggestion.files.withIndex()) {
                    appendLine("${index + 1}. ${file.filePath}")
                    if (file.lineNumber != null) {
                        appendLine("   Line: ${file.lineNumber}")
                    }
                    if (file.description.isNotBlank()) {
                        appendLine("   Note: ${file.description}")
                    }
                    appendLine()
                }
            }
            
            if (suggestion.metadata.isNotEmpty()) {
                appendLine("Additional Information:")
                appendLine("-".repeat(20))
                for ((key, value) in suggestion.metadata) {
                    appendLine("${key.replace("_", " ").capitalizeWords()}: $value")
                }
            }
        }
        
        showDetailsDialog(details, "Suggestion Details")
    }
    
    private fun showFileDetailsDialog(files: List<FileIssue>, title: String) {
        val details = buildString {
            appendLine("File Details: $title")
            appendLine("=".repeat(50))
            appendLine()
            appendLine("Found ${files.size} file(s) with issues:")
            appendLine()
            
            for ((index, file) in files.withIndex()) {
                appendLine("${index + 1}. File: ${file.filePath}")
                if (file.lineNumber != null) {
                    appendLine("   Line Number: ${file.lineNumber}")
                }
                if (file.category != null) {
                    appendLine("   Category: ${file.category}")
                }
                appendLine("   Severity: ${file.severity}")
                if (file.ruleId != null) {
                    appendLine("   Rule ID: ${file.ruleId}")
                }
                if (file.description.isNotBlank()) {
                    appendLine("   Description: ${file.description}")
                }
                appendLine()
            }
        }
        
        showDetailsDialog(details, "File Issues")
    }
    
    private fun showDetailsDialog(details: String, title: String) {
        val textArea = JTextArea(details)
        textArea.isEditable = false
        textArea.rows = 20
        textArea.columns = 60
        textArea.font = Font(Font.MONOSPACED, Font.PLAIN, 12)
        
        val scrollPane = JScrollPane(textArea)
        scrollPane.preferredSize = Dimension(600, 400)
        
        JOptionPane.showMessageDialog(
            contentPanel,
            scrollPane,
            title,
            JOptionPane.INFORMATION_MESSAGE
        )
    }
    
    private fun getFileName(filePath: String): String {
        return filePath.substringAfterLast('/')
    }
    
    private fun formatActivityKey(key: String): String {
        return key.replace("_", " ").capitalizeWords()
    }
    
    private fun formatInsightKey(key: String): String {
        return key.replace("_", " ").capitalizeWords()
    }
    
    private fun formatInsightValue(key: String, value: Any): String {
        return when (key) {
            "code_quality_score" -> {
                val score = (value as? Number)?.toInt() ?: 0
                "$score ${if (score >= 0) "✅" else "⚠️"}"
            }
            "build_health" -> {
                val health = (value as? Number)?.toInt() ?: 0
                "$health ${if (health > 0) "✅" else "❌"}"
            }
            "patterns_detected" -> "$value patterns"
            else -> value.toString()
        }
    }
    
    private fun formatGeneratedTime(timestamp: String): String {
        return try {
            // Parse ISO timestamp and format for display
            val parts = timestamp.split("T")
            if (parts.size == 2) {
                val date = parts[0]
                val time = parts[1].split(".")[0]
                "$date at $time"
            } else {
                timestamp
            }
        } catch (e: Exception) {
            timestamp
        }
    }
    
    private fun String.capitalizeWords(): String {
        return split(" ").joinToString(" ") { it.capitalizeFirstLetter() }
    }
    
    private fun String.capitalizeFirstLetter(): String {
        return if (isEmpty()) this else this[0].uppercase() + substring(1).lowercase()
    }
} 
package com.devex.plugin.services

import com.intellij.notification.*
import com.intellij.openapi.application.ApplicationManager
import com.intellij.openapi.components.Service
import com.intellij.openapi.diagnostic.Logger
import com.intellij.openapi.project.Project
import com.intellij.openapi.project.ProjectManager
import kotlinx.coroutines.*
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter

/**
 * Notification Service for DevEx Ambient Agent
 * Provides real-time notifications for critical issues and agent status changes
 */
@Service(Service.Level.APP)
class NotificationService {
    
    private val logger = Logger.getInstance(NotificationService::class.java)
    private val notificationScope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    private val agentService = AmbientAgentService.getInstance()
    
    // Notification group for DevEx Agent
    companion object {
        private val NOTIFICATION_GROUP = NotificationGroupManager.getInstance()
            .getNotificationGroup("DevEx Agent Notifications")
        
        private const val CHECK_INTERVAL_MS = 30000L // 30 seconds
        
        fun getInstance(): NotificationService {
            return ApplicationManager.getApplication().getService(NotificationService::class.java)
        }
    }
    
    private var lastNotificationTime = 0L
    private val recentNotifications = mutableSetOf<String>()
    private var isMonitoring = false
    private var lastAgentStatus = "unknown"
    
    init {
        logger.info("🔔 Initializing DevEx Notification Service...")
        startCriticalIssueMonitoring()
    }
    
    /**
     * Start monitoring for critical issues and agent status changes
     */
    private fun startCriticalIssueMonitoring() {
        if (isMonitoring) return
        
        isMonitoring = true
        logger.info("🔍 Starting critical issue monitoring...")
        
        notificationScope.launch {
            while (isMonitoring) {
                try {
                    checkForCriticalIssues()
                    checkAgentStatus()
                    delay(CHECK_INTERVAL_MS)
                } catch (e: Exception) {
                    logger.debug("Error in notification monitoring: ${e.message}")
                    delay(CHECK_INTERVAL_MS)
                }
            }
        }
    }
    
    /**
     * Check for critical issues by getting agent status
     */
    private suspend fun checkForCriticalIssues() {
        try {
            // Get recent morning brief to check for critical items
            val brief = agentService.requestMorningBrief()
            if (brief != null && brief.criticalItems.isNotEmpty()) {
                val criticalItems = brief.criticalItems.filter { 
                    it["priority"]?.toString()?.lowercase() in listOf("critical", "high")
                }
                
                if (criticalItems.isNotEmpty()) {
                    showCriticalIssuesNotification(criticalItems)
                }
            }
        } catch (e: Exception) {
            logger.debug("Failed to check for critical issues: ${e.message}")
        }
    }
    
    /**
     * Check agent connection status
     */
    private suspend fun checkAgentStatus() {
        try {
            val status = agentService.getAgentStatus()
            val currentStatus = status?.status ?: "disconnected"
            
            // Notify on status changes
            if (currentStatus != lastAgentStatus) {
                when (currentStatus) {
                    "disconnected", "error" -> {
                        showAgentDisconnectedNotification()
                    }
                    "active" -> {
                        if (lastAgentStatus in listOf("disconnected", "error", "unknown")) {
                            showAgentReconnectedNotification()
                        }
                    }
                }
                lastAgentStatus = currentStatus
            }
        } catch (e: Exception) {
            if (lastAgentStatus != "disconnected") {
                showAgentDisconnectedNotification()
                lastAgentStatus = "disconnected"
            }
        }
    }
    
    /**
     * Show notification for critical issues
     */
    private fun showCriticalIssuesNotification(criticalItems: List<Map<String, Any>>) {
        val currentTime = System.currentTimeMillis()
        val notificationKey = "critical_issues_${criticalItems.size}"
        
        // Avoid spam - only notify once per hour for similar issues
        if (currentTime - lastNotificationTime < 3600000 && recentNotifications.contains(notificationKey)) {
            return
        }
        
        ApplicationManager.getApplication().invokeLater {
            val project = getCurrentProject()
            
            val title = "🚨 Critical Issues Detected"
            val content = buildString {
                append("${criticalItems.size} critical item(s) need your attention:\n\n")
                criticalItems.take(3).forEach { item ->
                    val priority = item["priority"]?.toString() ?: "unknown"
                    val title = item["title"]?.toString() ?: "Unknown issue"
                    append("${getPriorityIcon(priority)} $title\n")
                }
                if (criticalItems.size > 3) {
                    append("... and ${criticalItems.size - 3} more")
                }
            }
            
            val notification = NOTIFICATION_GROUP.createNotification(
                title,
                content,
                NotificationType.WARNING
            )
            
            // Add action to open tool window
            notification.addAction(object : NotificationAction("View Details") {
                override fun actionPerformed(e: com.intellij.openapi.actionSystem.AnActionEvent, notification: Notification) {
                    openDevExToolWindow(project)
                    notification.expire()
                }
            })
            
            // Add action to dismiss
            notification.addAction(object : NotificationAction("Dismiss") {
                override fun actionPerformed(e: com.intellij.openapi.actionSystem.AnActionEvent, notification: Notification) {
                    notification.expire()
                }
            })
            
            notification.notify(project)
            
            lastNotificationTime = currentTime
            recentNotifications.add(notificationKey)
            
            // Clean up old notifications from memory
            if (recentNotifications.size > 10) {
                recentNotifications.clear()
            }
        }
    }
    
    /**
     * Show notification when agent disconnects
     */
    private fun showAgentDisconnectedNotification() {
        ApplicationManager.getApplication().invokeLater {
            val project = getCurrentProject()
            
            val notification = NOTIFICATION_GROUP.createNotification(
                "🔴 DevEx Agent Disconnected",
                "The ambient agent is not reachable. Some features may not work.",
                NotificationType.WARNING
            )
            
            notification.addAction(object : NotificationAction("Check Connection") {
                override fun actionPerformed(e: com.intellij.openapi.actionSystem.AnActionEvent, notification: Notification) {
                    // Trigger a status check
                    notificationScope.launch {
                        checkAgentStatus()
                    }
                    notification.expire()
                }
            })
            
            notification.notify(project)
        }
    }
    
    /**
     * Show notification when agent reconnects
     */
    private fun showAgentReconnectedNotification() {
        ApplicationManager.getApplication().invokeLater {
            val project = getCurrentProject()
            
            val notification = NOTIFICATION_GROUP.createNotification(
                "✅ DevEx Agent Connected",
                "Ambient monitoring is now active.",
                NotificationType.INFORMATION
            )
            
            notification.notify(project)
        }
    }
    
    /**
     * Show notification for build failures
     */
    fun showBuildFailureNotification(buildInfo: Map<String, Any>) {
        ApplicationManager.getApplication().invokeLater {
            val project = getCurrentProject()
            
            val errorType = buildInfo["error_type"]?.toString() ?: "Unknown error"
            val errorMessage = buildInfo["error_message"]?.toString() ?: "Build failed"
            
            val notification = NOTIFICATION_GROUP.createNotification(
                "🔴 Build Failed",
                "$errorType: $errorMessage",
                NotificationType.ERROR
            )
            
            notification.addAction(object : NotificationAction("View Details") {
                override fun actionPerformed(e: com.intellij.openapi.actionSystem.AnActionEvent, notification: Notification) {
                    openDevExToolWindow(project)
                    notification.expire()
                }
            })
            
            notification.notify(project)
        }
    }
    
    /**
     * Show notification for successful workflows
     */
    fun showSuccessNotification(title: String, message: String) {
        ApplicationManager.getApplication().invokeLater {
            val project = getCurrentProject()
            
            val notification = NOTIFICATION_GROUP.createNotification(
                title,
                message,
                NotificationType.INFORMATION
            )
            
            // Auto-expire success notifications after 5 seconds
            notification.whenExpired {
                // Cleanup if needed
            }
            
            notification.notify(project)
        }
    }
    
    /**
     * Show custom notification with specified type and actions
     */
    fun showCustomNotification(
        title: String,
        content: String,
        type: NotificationType,
        actions: List<Pair<String, () -> Unit>> = emptyList()
    ) {
        ApplicationManager.getApplication().invokeLater {
            val project = getCurrentProject()
            
            val notification = NOTIFICATION_GROUP.createNotification(
                title,
                content,
                type
            )
            
            // Add custom actions
            actions.forEach { (actionTitle, actionCallback) ->
                notification.addAction(object : NotificationAction(actionTitle) {
                    override fun actionPerformed(e: com.intellij.openapi.actionSystem.AnActionEvent, notification: Notification) {
                        actionCallback()
                        notification.expire()
                    }
                })
            }
            
            notification.notify(project)
        }
    }
    
    /**
     * Show morning brief summary notification
     */
    fun showMorningBriefNotification(briefSummary: String, criticalCount: Int, suggestionCount: Int) {
        ApplicationManager.getApplication().invokeLater {
            val project = getCurrentProject()
            
            val icon = if (criticalCount > 0) "⚠️" else "🌅"
            val title = "$icon Morning Brief Ready"
            val content = buildString {
                append("$briefSummary\n\n")
                if (criticalCount > 0) {
                    append("🚨 $criticalCount critical item(s) need attention\n")
                }
                if (suggestionCount > 0) {
                    append("💡 $suggestionCount suggestion(s) available")
                }
            }
            
            val notification = NOTIFICATION_GROUP.createNotification(
                title,
                content,
                if (criticalCount > 0) NotificationType.WARNING else NotificationType.INFORMATION
            )
            
            notification.addAction(object : NotificationAction("View Brief") {
                override fun actionPerformed(e: com.intellij.openapi.actionSystem.AnActionEvent, notification: Notification) {
                    openDevExToolWindow(project)
                    notification.expire()
                }
            })
            
            notification.notify(project)
        }
    }
    
    // Helper methods
    private fun getPriorityIcon(priority: String): String {
        return when (priority.lowercase()) {
            "critical" -> "🔴"
            "high" -> "🟡"
            "medium" -> "🟠"
            "low" -> "🟢"
            else -> "⚪"
        }
    }
    
    private fun getCurrentProject(): Project? {
        val projects = ProjectManager.getInstance().openProjects
        return projects.firstOrNull() ?: ProjectManager.getInstance().defaultProject
    }
    
    private fun openDevExToolWindow(project: Project?) {
        if (project != null) {
            val toolWindowManager = com.intellij.openapi.wm.ToolWindowManager.getInstance(project)
            val toolWindow = toolWindowManager.getToolWindow("DevEx Agent")
            toolWindow?.activate(null)
        }
    }
    
    /**
     * Stop monitoring and cleanup
     */
    fun dispose() {
        logger.info("🛑 Disposing DevEx Notification Service...")
        isMonitoring = false
        notificationScope.cancel()
        recentNotifications.clear()
    }
} 
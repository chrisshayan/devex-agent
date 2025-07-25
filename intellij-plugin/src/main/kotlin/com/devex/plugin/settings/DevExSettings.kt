package com.devex.plugin.settings

import com.intellij.openapi.application.ApplicationManager
import com.intellij.openapi.components.*
import com.intellij.util.xmlb.XmlSerializerUtil

/**
 * Settings state for DevEx Ambient Agent Plugin
 * Persists user configuration across IDE sessions
 */
@State(
    name = "DevExSettings",
    storages = [Storage("DevExAmbientAgent.xml")]
)
@Service(Service.Level.APP)
class DevExSettings : PersistentStateComponent<DevExSettings> {
    
    // API Configuration
    var apiEndpoint: String = "http://localhost:8000"
    var apiTimeout: Int = 30 // seconds
    var developerId: String = System.getProperty("user.name", "developer")
    
    // Monitoring Configuration
    var fileMonitoringEnabled: Boolean = true
    var gitMonitoringEnabled: Boolean = true
    var buildMonitoringEnabled: Boolean = true
    var monitoringInterval: Int = 60 // seconds
    
    // Notification Settings
    var notificationsEnabled: Boolean = true
    var criticalIssueNotifications: Boolean = true
    var agentStatusNotifications: Boolean = true
    var morningBriefNotifications: Boolean = true
    var buildFailureNotifications: Boolean = true
    var notificationCheckInterval: Int = 30 // seconds
    
    // Morning Brief Configuration
    var autoGenerateMorningBrief: Boolean = false
    var morningBriefTime: String = "09:00" // HH:mm format
    var briefRetentionDays: Int = 7
    
    // Advanced Settings
    var debugMode: Boolean = false
    var logLevel: String = "INFO"
    var maxEventBufferSize: Int = 1000
    var eventCooldownSeconds: Int = 2
    
    // UI Settings
    var toolWindowLocation: String = "right" // left, right, bottom
    var autoOpenToolWindow: Boolean = false
    var showDetailedStatus: Boolean = true
    
    companion object {
        fun getInstance(): DevExSettings {
            return ApplicationManager.getApplication().getService(DevExSettings::class.java)
        }
    }
    
    override fun getState(): DevExSettings {
        return this
    }
    
    override fun loadState(state: DevExSettings) {
        XmlSerializerUtil.copyBean(state, this)
    }
    
    // Helper methods for validation
    fun isValidApiEndpoint(): Boolean {
        return apiEndpoint.isNotBlank() && 
               (apiEndpoint.startsWith("http://") || apiEndpoint.startsWith("https://"))
    }
    
    fun isValidDeveloperId(): Boolean {
        return developerId.isNotBlank() && developerId.matches(Regex("[a-zA-Z0-9_-]+"))
    }
    
    fun getApiEndpointWithPath(path: String): String {
        val baseUrl = apiEndpoint.trimEnd('/')
        val cleanPath = path.trimStart('/')
        return "$baseUrl/$cleanPath"
    }
    
    // Reset to defaults
    fun resetToDefaults() {
        apiEndpoint = "http://localhost:8000"
        apiTimeout = 30
        developerId = System.getProperty("user.name", "developer")
        fileMonitoringEnabled = true
        gitMonitoringEnabled = true
        buildMonitoringEnabled = true
        monitoringInterval = 60
        notificationsEnabled = true
        criticalIssueNotifications = true
        agentStatusNotifications = true
        morningBriefNotifications = true
        buildFailureNotifications = true
        notificationCheckInterval = 30
        autoGenerateMorningBrief = false
        morningBriefTime = "09:00"
        briefRetentionDays = 7
        debugMode = false
        logLevel = "INFO"
        maxEventBufferSize = 1000
        eventCooldownSeconds = 2
        toolWindowLocation = "right"
        autoOpenToolWindow = false
        showDetailedStatus = true
    }
} 
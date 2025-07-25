package com.devex.plugin.services

import com.intellij.openapi.application.ApplicationManager
import com.intellij.openapi.components.ApplicationService
import com.intellij.openapi.components.Service
import com.intellij.openapi.diagnostic.Logger
import com.intellij.openapi.project.Project
import kotlinx.coroutines.*
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import com.fasterxml.jackson.module.kotlin.jacksonObjectMapper
import com.fasterxml.jackson.module.kotlin.readValue
import java.io.IOException

/**
 * Ambient Agent Service - Core communication service for DevEx Ambient Agent
 * 
 * Following LangChain Academy ambient agent patterns:
 * - Event-driven communication
 * - Background processing
 * - Human-in-the-loop notifications
 */
@Service(Service.Level.APP)
class AmbientAgentService : ApplicationService {
    
    private val logger = Logger.getInstance(AmbientAgentService::class.java)
    private val objectMapper = jacksonObjectMapper()
    private val httpClient = OkHttpClient()
    
    // Configuration
    private val agentCoreUrl = "http://localhost:8000"
    private val developerId = System.getProperty("user.name") + "@" + getHostname()
    
    // Service state
    private var isInitialized = false
    private var serviceScope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    
    init {
        logger.info("🚀 Initializing DevEx Ambient Agent Service...")
        initialize()
    }
    
    private fun initialize() {
        serviceScope.launch {
            try {
                // Test connection to agent core
                val healthCheck = checkAgentCoreHealth()
                if (healthCheck) {
                    isInitialized = true
                    logger.info("✅ Ambient Agent Service initialized successfully")
                    startPeriodicHealthCheck()
                } else {
                    logger.warn("⚠️ Agent core not available, will retry...")
                    scheduleRetryInitialization()
                }
            } catch (e: Exception) {
                logger.error("❌ Failed to initialize Ambient Agent Service", e)
                scheduleRetryInitialization()
            }
        }
    }
    
    /**
     * Send event to ambient agent core
     * This is the primary method for ambient event processing
     */
    suspend fun sendEvent(
        type: String,
        source: String = "intellij",
        projectPath: String? = null,
        filePath: String? = null,
        description: String? = null,
        metadata: Map<String, Any> = emptyMap()
    ) {
        if (!isInitialized) {
            logger.debug("Agent service not initialized, queuing event...")
            // TODO: Implement event queuing for offline scenarios
            return
        }
        
        try {
            val eventData = mapOf(
                "type" to type,
                "source" to source,
                "developer_id" to developerId,
                "project_path" to projectPath,
                "file_path" to filePath,
                "description" to description,
                "metadata" to metadata
            )
            
            val requestBody = objectMapper.writeValueAsString(eventData)
                .toRequestBody("application/json".toMediaType())
            
            val request = Request.Builder()
                .url("$agentCoreUrl/events/ingest")
                .post(requestBody)
                .build()
            
            httpClient.newCall(request).execute().use { response ->
                if (response.isSuccessful) {
                    logger.debug("📨 Event sent successfully: $type")
                } else {
                    logger.warn("⚠️ Failed to send event: ${response.code}")
                }
            }
            
        } catch (e: Exception) {
            logger.error("❌ Error sending event to agent core", e)
        }
    }
    
    /**
     * Request morning brief from ambient agent
     * This triggers the LangGraph workflow
     */
    suspend fun requestMorningBrief(): MorningBrief? {
        if (!isInitialized) {
            logger.warn("Agent service not initialized")
            return null
        }
        
        return try {
            val request = Request.Builder()
                .url("$agentCoreUrl/brief/morning/$developerId")
                .get()
                .build()
            
            httpClient.newCall(request).execute().use { response ->
                if (response.isSuccessful) {
                    val briefJson = response.body?.string() ?: "{}"
                    val briefData = objectMapper.readValue<Map<String, Any>>(briefJson)
                    logger.info("🌅 Morning brief received successfully")
                    
                    MorningBrief(
                        developerId = briefData["developer_id"] as? String ?: developerId,
                        generatedAt = briefData["generated_at"] as? String ?: "",
                        greeting = briefData["greeting"] as? String,
                        summary = briefData["summary"] as? String ?: "",
                        activityOverview = briefData["activity_overview"] as? Map<String, Any> ?: emptyMap(),
                        criticalItems = briefData["critical_items"] as? List<Map<String, Any>> ?: emptyList(),
                        suggestions = briefData["suggestions"] as? List<Map<String, Any>> ?: emptyList(),
                        insights = briefData["insights"] as? Map<String, Any> ?: emptyMap()
                    )
                } else {
                    logger.warn("⚠️ Failed to get morning brief: ${response.code}")
                    null
                }
            }
        } catch (e: Exception) {
            logger.error("❌ Error requesting morning brief", e)
            null
        }
    }
    
    /**
     * Get agent status
     */
    suspend fun getAgentStatus(): AgentStatus? {
        if (!isInitialized) {
            return AgentStatus(
                status = "disconnected",
                message = "Agent core not available"
            )
        }
        
        return try {
            val request = Request.Builder()
                .url("$agentCoreUrl/status/$developerId")
                .get()
                .build()
            
            httpClient.newCall(request).execute().use { response ->
                if (response.isSuccessful) {
                    val statusJson = response.body?.string() ?: "{}"
                    val statusData = objectMapper.readValue<Map<String, Any>>(statusJson)
                    
                    AgentStatus(
                        status = statusData["status"] as? String ?: "unknown",
                        message = statusData["message"] as? String,
                        eventsCount = (statusData["events_count"] as? Number)?.toInt() ?: 0,
                        lastBrief = statusData["last_brief"] as? String,
                        isMonitoring = statusData["is_monitoring"] as? Boolean ?: false
                    )
                } else {
                    AgentStatus(
                        status = "error",
                        message = "HTTP ${response.code}"
                    )
                }
            }
        } catch (e: Exception) {
            logger.error("❌ Error getting agent status", e)
            AgentStatus(
                status = "error",
                message = e.message ?: "Unknown error"
            )
        }
    }
    
    private suspend fun checkAgentCoreHealth(): Boolean {
        return try {
            val request = Request.Builder()
                .url("$agentCoreUrl/")
                .get()
                .build()
            
            httpClient.newCall(request).execute().use { response ->
                response.isSuccessful
            }
        } catch (e: Exception) {
            logger.debug("Agent core health check failed: ${e.message}")
            false
        }
    }
    
    private fun startPeriodicHealthCheck() {
        serviceScope.launch {
            while (isInitialized) {
                delay(60_000) // Check every minute
                val isHealthy = checkAgentCoreHealth()
                if (!isHealthy) {
                    logger.warn("⚠️ Lost connection to agent core")
                    isInitialized = false
                    scheduleRetryInitialization()
                    break
                }
            }
        }
    }
    
    private fun scheduleRetryInitialization() {
        serviceScope.launch {
            delay(30_000) // Retry after 30 seconds
            initialize()
        }
    }
    
    private fun getHostname(): String {
        return try {
            java.net.InetAddress.getLocalHost().hostName
        } catch (e: Exception) {
            "unknown"
        }
    }
    
    override fun dispose() {
        logger.info("🛑 Disposing Ambient Agent Service...")
        serviceScope.cancel()
    }
    
    companion object {
        fun getInstance(): AmbientAgentService {
            return ApplicationManager.getApplication().getService(AmbientAgentService::class.java)
        }
    }
}

// Data classes for API communication
data class MorningBrief(
    val developerId: String,
    val generatedAt: String,
    val greeting: String?,
    val summary: String,
    val activityOverview: Map<String, Any>,
    val criticalItems: List<Map<String, Any>>,
    val suggestions: List<Map<String, Any>>,
    val insights: Map<String, Any>
)

data class AgentStatus(
    val status: String,
    val message: String? = null,
    val eventsCount: Int = 0,
    val lastBrief: String? = null,
    val isMonitoring: Boolean = false
) 
package com.devex.plugin.services

import com.intellij.openapi.application.ApplicationManager
import com.intellij.openapi.components.Service
import com.intellij.openapi.diagnostic.Logger
import com.intellij.openapi.Disposable
import com.intellij.openapi.project.Project
import com.devex.plugin.settings.DevExSettings
import kotlinx.coroutines.*
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import com.fasterxml.jackson.module.kotlin.jacksonObjectMapper
import com.fasterxml.jackson.module.kotlin.readValue
import java.io.IOException
import java.net.SocketTimeoutException
import java.net.ConnectException
import java.util.concurrent.ConcurrentLinkedQueue
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicInteger
import java.time.LocalDateTime
import java.util.concurrent.TimeUnit

/**
 * Enhanced Ambient Agent Service - Robust communication service for DevEx Ambient Agent
 * 
 * Features:
 * - Exponential backoff reconnection with circuit breaker
 * - Event queuing for offline scenarios  
 * - Connection pooling and timeout management
 * - Settings integration and real-time configuration
 * - Comprehensive error handling and recovery
 * - Health monitoring with metrics
 */
@Service(Service.Level.APP)
class AmbientAgentService : Disposable {
    
    private val logger = Logger.getInstance(AmbientAgentService::class.java)
    private val objectMapper = jacksonObjectMapper()
    private val settings = DevExSettings.getInstance()
    
    // Enhanced HTTP client with connection pooling
    private val httpClient = OkHttpClient.Builder()
        .connectTimeout(120, TimeUnit.SECONDS)  
        .readTimeout(120, TimeUnit.SECONDS)    
        .writeTimeout(120, TimeUnit.SECONDS)    
        .connectionPool(ConnectionPool(5, 5, TimeUnit.MINUTES))
        .retryOnConnectionFailure(true)
        .build()
    
    // Service state management
    private var serviceScope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    private val connectionState = ConnectionState()
    private val eventQueue = ConcurrentLinkedQueue<QueuedEvent>()
    private val reconnectionManager = ReconnectionManager()
    private val metricsCollector = MetricsCollector()
    
    // Circuit breaker state
    private val circuitBreakerFailures = AtomicInteger(0)
    private val circuitBreakerOpen = AtomicBoolean(false)
    private var circuitBreakerOpenTime = 0L
    
    init {
        logger.info("🚀 Initializing Enhanced DevEx Ambient Agent Service...")
        initialize()
    }
    
    private fun initialize() {
        serviceScope.launch {
            try {
                logger.info("🔧 Configuring service with settings...")
                
                // Initialize connection
                if (attemptConnection()) {
                    connectionState.markConnected()
                    startBackgroundTasks()
                    processQueuedEvents()
                    logger.info("✅ Ambient Agent Service initialized successfully")
                } else {
                    connectionState.markDisconnected()
                    logger.warn("⚠️ Agent core not available, starting reconnection process...")
                    reconnectionManager.startReconnection()
                }
                
            } catch (e: Exception) {
                logger.error("❌ Failed to initialize Ambient Agent Service", e)
                connectionState.markError(e.message ?: "Unknown error")
                reconnectionManager.startReconnection()
            }
        }
    }
    
    /**
     * Enhanced event sending with queuing and retry logic
     */
    suspend fun sendEvent(
        type: String,
        source: String = "intellij",
        projectPath: String? = null,
        filePath: String? = null,
        description: String? = null,
        metadata: Map<String, Any> = emptyMap()
    ) {
        if (!settings.fileMonitoringEnabled && type == "file_changed") return
        if (!settings.gitMonitoringEnabled && type == "git_commit") return
        if (!settings.buildMonitoringEnabled && type == "build_event") return
        
        val event = QueuedEvent(
            type = type,
            source = source,
            projectPath = projectPath,
            filePath = filePath,
            description = description,
            metadata = metadata,
            timestamp = System.currentTimeMillis(),
            retryCount = 0
        )
        
        if (connectionState.isConnected() && !circuitBreakerOpen.get()) {
            if (sendEventDirectly(event)) {
                metricsCollector.recordEventSent()
                logger.debug("📨 Event sent successfully: $type")
            } else {
                queueEvent(event)
            }
        } else {
            queueEvent(event)
            logger.debug("📤 Event queued (offline): $type")
        }
    }
    
    /**
     * Enhanced morning brief request with timeout and retry
     */
    suspend fun requestMorningBrief(): MorningBrief? {
        if (!connectionState.isConnected()) {
            logger.warn("🔴 Cannot request morning brief: agent disconnected")
            return null
        }
        
        if (circuitBreakerOpen.get()) {
            logger.warn("🔴 Cannot request morning brief: circuit breaker open")
            return null
        }
        
        return withRetry(maxRetries = 3) {
            try {
                val request = Request.Builder()
                    .url(settings.getApiEndpointWithPath("/brief/morning/${settings.developerId}"))
                    .get()
                    .build()
                
                httpClient.newCall(request).execute().use { response ->
                    when {
                        response.isSuccessful -> {
                            val briefJson = response.body?.string() ?: "{}"
                            val briefData = objectMapper.readValue<Map<String, Any>>(briefJson)
                            logger.info("🌅 Morning brief received successfully")
                            metricsCollector.recordBriefGenerated()
                            
                            MorningBrief(
                                developerId = briefData["developer_id"] as? String ?: settings.developerId,
                                generatedAt = briefData["generated_at"] as? String ?: "",
                                greeting = briefData["greeting"] as? String,
                                summary = briefData["summary"] as? String ?: "",
                                activityOverview = briefData["activity_overview"] as? Map<String, Any> ?: emptyMap(),
                                criticalItems = parseCriticalItems(briefData["critical_items"] as? List<Map<String, Any>> ?: emptyList()),
                                suggestions = parseSuggestions(briefData["suggestions"] as? List<Map<String, Any>> ?: emptyList()),
                                insights = briefData["insights"] as? Map<String, Any> ?: emptyMap()
                            )
                        }
                        response.code == 404 -> {
                            logger.warn("⚠️ Morning brief not found for developer: ${settings.developerId}")
                            null
                        }
                        else -> {
                            logger.warn("⚠️ Failed to get morning brief: ${response.code}")
                            recordFailure()
                            null
                        }
                    }
                }
            } catch (e: Exception) {
                logger.error("❌ Error requesting morning brief", e)
                recordFailure()
                throw e
            }
        }
    }
    
    /**
     * Enhanced agent status with detailed connection info
     */
    suspend fun getAgentStatus(): AgentStatus? {
        if (!connectionState.isConnected()) {
            return AgentStatus(
                status = "disconnected",
                message = "Agent core not available - ${connectionState.lastError ?: "No connection"}",
                eventsCount = eventQueue.size,
                lastConnectionAttempt = reconnectionManager.lastAttemptTime,
                queuedEvents = eventQueue.size,
                circuitBreakerOpen = circuitBreakerOpen.get()
            )
        }
        
        if (circuitBreakerOpen.get()) {
            return AgentStatus(
                status = "circuit_breaker_open",
                message = "Circuit breaker open due to repeated failures",
                eventsCount = eventQueue.size,
                circuitBreakerOpen = true
            )
        }
        
        return withRetry(maxRetries = 2) {
            try {
                val request = Request.Builder()
                    .url(settings.getApiEndpointWithPath("/status/${settings.developerId}"))
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
                            isMonitoring = statusData["is_monitoring"] as? Boolean ?: false,
                            queuedEvents = eventQueue.size,
                            connectionUptime = connectionState.getUptimeSeconds(),
                            circuitBreakerOpen = false
                        )
                    } else {
                        logger.warn("⚠️ Failed to get agent status: ${response.code}")
                        recordFailure()
                        AgentStatus(
                            status = "error",
                            message = "HTTP ${response.code}",
                            queuedEvents = eventQueue.size
                        )
                    }
                }
            } catch (e: Exception) {
                logger.error("❌ Error getting agent status", e)
                recordFailure()
                throw e
            }
        }
    }
    
    /**
     * Test connection with detailed diagnostics
     */
    suspend fun testConnection(): ConnectionTestResult {
        logger.info("🔍 Testing connection to agent...")
        
        return try {
            val startTime = System.currentTimeMillis()
            
            val request = Request.Builder()
                .url(settings.getApiEndpointWithPath("/"))
                .get()
                .build()
            
            httpClient.newCall(request).execute().use { response ->
                val latency = System.currentTimeMillis() - startTime
                
                when {
                    response.isSuccessful -> {
                        logger.info("✅ Connection test successful (${latency}ms)")
                        resetCircuitBreaker()
                        ConnectionTestResult(
                            success = true,
                            latencyMs = latency,
                            message = "Connection successful",
                            endpoint = settings.apiEndpoint
                        )
                    }
                    else -> {
                        logger.warn("⚠️ Connection test failed: HTTP ${response.code}")
                        ConnectionTestResult(
                            success = false,
                            latencyMs = latency,
                            message = "HTTP ${response.code}: ${response.message}",
                            endpoint = settings.apiEndpoint
                        )
                    }
                }
            }
        } catch (e: ConnectException) {
            logger.warn("🔴 Connection test failed: Connection refused")
            ConnectionTestResult(
                success = false,
                message = "Connection refused - is the agent running?",
                endpoint = settings.apiEndpoint,
                error = e.message
            )
        } catch (e: SocketTimeoutException) {
            logger.warn("🔴 Connection test failed: Timeout")
            ConnectionTestResult(
                success = false,
                message = "Connection timeout",
                endpoint = settings.apiEndpoint,
                error = e.message
            )
        } catch (e: Exception) {
            logger.error("❌ Connection test error", e)
            ConnectionTestResult(
                success = false,
                message = "Connection error: ${e.message}",
                endpoint = settings.apiEndpoint,
                error = e.message
            )
        }
    }
    
    // Private helper methods
    private suspend fun attemptConnection(): Boolean {
        return try {
            val request = Request.Builder()
                .url(settings.getApiEndpointWithPath("/"))
                .get()
                .build()
            
            httpClient.newCall(request).execute().use { response ->
                val success = response.isSuccessful
                if (success) {
                    resetCircuitBreaker()
                    metricsCollector.recordConnection()
                } else {
                    recordFailure()
                }
                success
            }
        } catch (e: Exception) {
            logger.debug("Connection attempt failed: ${e.message}")
            recordFailure()
            false
        }
    }
    
    private suspend fun sendEventDirectly(event: QueuedEvent): Boolean {
        return try {
            val eventData = mapOf(
                "type" to event.type,
                "source" to event.source,
                "developer_id" to settings.developerId,
                "project_path" to event.projectPath,
                "file_path" to event.filePath,
                "description" to event.description,
                "metadata" to event.metadata
            )
            
            val requestBody = objectMapper.writeValueAsString(eventData)
                .toRequestBody("application/json".toMediaType())
            
            val request = Request.Builder()
                .url(settings.getApiEndpointWithPath("/events/ingest"))
                .post(requestBody)
                .build()
            
            httpClient.newCall(request).execute().use { response ->
                if (response.isSuccessful) {
                    true
                } else {
                    logger.warn("⚠️ Failed to send event: ${response.code}")
                    recordFailure()
                    false
                }
            }
        } catch (e: Exception) {
            logger.error("❌ Error sending event directly", e)
            recordFailure()
            false
        }
    }
    
    private fun queueEvent(event: QueuedEvent) {
        if (eventQueue.size < settings.maxEventBufferSize) {
            eventQueue.offer(event)
            logger.debug("📥 Event queued: ${event.type}")
        } else {
            // Remove oldest event to make room
            eventQueue.poll()
            eventQueue.offer(event)
            logger.warn("⚠️ Event queue full, removed oldest event")
        }
    }
    
    private suspend fun processQueuedEvents() {
        logger.info("🔄 Processing ${eventQueue.size} queued events...")
        
        while (eventQueue.isNotEmpty() && connectionState.isConnected() && !circuitBreakerOpen.get()) {
            val event = eventQueue.poll() ?: break
            
            if (sendEventDirectly(event)) {
                metricsCollector.recordEventSent()
                logger.debug("📨 Queued event sent: ${event.type}")
            } else {
                // If failed, put it back unless too old or too many retries
                if (event.shouldRetry()) {
                    eventQueue.offer(event.withRetry())
                    logger.debug("🔄 Event requeued for retry: ${event.type}")
                    delay(1000) // Wait before next attempt
                } else {
                    logger.warn("❌ Dropping event after max retries: ${event.type}")
                }
                break // Stop processing if we hit an error
            }
            delay(100) // Throttle event processing
        }
    }
    
    private fun startBackgroundTasks() {
        // Periodic health check
        serviceScope.launch {
            while (connectionState.isConnected()) {
                delay(settings.monitoringInterval * 1000L)
                if (!attemptConnection()) {
                    connectionState.markDisconnected()
                    reconnectionManager.startReconnection()
                    break
                }
            }
        }
        
        // Event queue processing
        serviceScope.launch {
            while (true) {
                delay(30_000) // Process queue every 30 seconds
                if (connectionState.isConnected() && eventQueue.isNotEmpty()) {
                    processQueuedEvents()
                }
            }
        }
        
        // Metrics collection
        serviceScope.launch {
            while (true) {
                delay(60_000) // Collect metrics every minute
                metricsCollector.logMetrics()
            }
        }
    }
    
    private suspend fun <T> withRetry(maxRetries: Int = 3, operation: suspend () -> T): T? {
        repeat(maxRetries) { attempt ->
            try {
                return operation()
            } catch (e: Exception) {
                if (attempt == maxRetries - 1) {
                    throw e
                }
                delay((attempt + 1) * 1000L) // Progressive delay
            }
        }
        return null
    }
    
    private fun recordFailure() {
        val failures = circuitBreakerFailures.incrementAndGet()
        logger.debug("🔴 Recorded failure #$failures")
        
        if (failures >= 5) { // Circuit breaker threshold
            circuitBreakerOpen.set(true)
            circuitBreakerOpenTime = System.currentTimeMillis()
            logger.warn("🔴 Circuit breaker opened after $failures failures")
            
            // Auto-reset circuit breaker after 60 seconds
            serviceScope.launch {
                delay(60_000)
                resetCircuitBreaker()
            }
        }
    }
    
    private fun resetCircuitBreaker() {
        circuitBreakerFailures.set(0)
        circuitBreakerOpen.set(false)
        circuitBreakerOpenTime = 0L
        logger.debug("✅ Circuit breaker reset")
    }
    
    /**
     * Enhanced parsing for critical items with detailed file information
     */
    private fun parseCriticalItems(rawItems: List<Map<String, Any>>): List<CriticalItem> {
        return rawItems.map { item ->
            CriticalItem(
                type = item["type"]?.toString() ?: "unknown",
                priority = item["priority"]?.toString() ?: "medium",
                title = item["title"]?.toString() ?: "Critical Issue",
                description = item["description"]?.toString() ?: "",
                actionRequired = item["action_required"] as? Boolean ?: false,
                files = parseFileIssues(item["files"] as? List<Map<String, Any>>),
                count = (item["count"] as? Number)?.toInt() ?: 0,
                metadata = item.filterKeys { it !in listOf("type", "priority", "title", "description", "action_required", "files", "count") }
            )
        }
    }
    
    /**
     * Enhanced parsing for suggestions with detailed information
     */
    private fun parseSuggestions(rawSuggestions: List<Map<String, Any>>): List<Suggestion> {
        return rawSuggestions.map { suggestion ->
            Suggestion(
                type = suggestion["type"]?.toString() ?: "general",
                title = suggestion["title"]?.toString() ?: "Suggestion",
                description = suggestion["description"]?.toString() ?: "",
                priority = suggestion["priority"]?.toString() ?: "medium",
                action = suggestion["action"]?.toString(),
                files = parseFileIssues(suggestion["files"] as? List<Map<String, Any>>),
                metadata = suggestion.filterKeys { it !in listOf("type", "title", "description", "priority", "action", "files") }
            )
        }
    }
    
    /**
     * Parse file issues from raw data
     */
    private fun parseFileIssues(rawFiles: List<Map<String, Any>>?): List<FileIssue> {
        return rawFiles?.map { file ->
            FileIssue(
                filePath = file["file_path"]?.toString() ?: file["path"]?.toString() ?: "unknown",
                lineNumber = (file["line_number"] as? Number)?.toInt() ?: (file["line"] as? Number)?.toInt(),
                description = file["description"]?.toString() ?: file["message"]?.toString() ?: "",
                severity = file["severity"]?.toString() ?: "medium",
                ruleId = file["rule_id"]?.toString() ?: file["rule"]?.toString(),
                category = file["category"]?.toString() ?: file["type"]?.toString()
            )
        } ?: emptyList()
    }
    
    /**
     * Fetch detailed file issues for security or quality analysis
     */
    suspend fun getDetailedIssues(type: String): List<FileIssue>? {
        if (!connectionState.isConnected() || circuitBreakerOpen.get()) {
            return null
        }
        
        return withRetry(maxRetries = 2) {
            try {
                val request = Request.Builder()
                    .url(settings.getApiEndpointWithPath("/analysis/$type/${settings.developerId}"))
                    .get()
                    .build()
                
                httpClient.newCall(request).execute().use { response ->
                    if (response.isSuccessful) {
                        val issuesJson = response.body?.string() ?: "[]"
                        val issuesData = objectMapper.readValue<List<Map<String, Any>>>(issuesJson)
                        parseFileIssues(issuesData)
                    } else {
                        logger.warn("⚠️ Failed to get detailed issues: ${response.code}")
                        null
                    }
                }
            } catch (e: Exception) {
                logger.error("❌ Error getting detailed issues", e)
                throw e
            }
        }
    }
    
    override fun dispose() {
        logger.info("🛑 Disposing Enhanced Ambient Agent Service...")
        reconnectionManager.stop()
        serviceScope.cancel()
        httpClient.dispatcher.executorService.shutdown()
        httpClient.connectionPool.evictAll()
    }
    
    companion object {
        fun getInstance(): AmbientAgentService {
            return ApplicationManager.getApplication().getService(AmbientAgentService::class.java)
        }
    }
    
    // Inner classes for state management
    private inner class ConnectionState {
        private var connected = AtomicBoolean(false)
        private var connectionTime = 0L
        var lastError: String? = null
        
        fun markConnected() {
            connected.set(true)
            connectionTime = System.currentTimeMillis()
            lastError = null
            logger.info("🟢 Agent connected")
        }
        
        fun markDisconnected() {
            connected.set(false)
            logger.warn("🔴 Agent disconnected")
        }
        
        fun markError(error: String) {
            connected.set(false)
            lastError = error
            logger.error("❌ Agent error: $error")
        }
        
        fun isConnected() = connected.get()
        
        fun getUptimeSeconds(): Long {
            return if (connected.get()) (System.currentTimeMillis() - connectionTime) / 1000 else 0
        }
    }
    
    private inner class ReconnectionManager {
        private var reconnectJob: Job? = null
        private var attempts = 0
        var lastAttemptTime: String? = null
        
        fun startReconnection() {
            if (reconnectJob?.isActive == true) return
            
            reconnectJob = serviceScope.launch {
                while (!connectionState.isConnected()) {
                    attempts++
                    lastAttemptTime = LocalDateTime.now().toString()
                    
                    // Exponential backoff: 1s, 2s, 4s, 8s, 16s, max 60s
                    val delay = minOf(60_000L, 1000L * (1L shl (attempts - 1)))
                    
                    logger.info("🔄 Reconnection attempt #$attempts in ${delay / 1000}s...")
                    delay(delay)
                    
                    if (attemptConnection()) {
                        connectionState.markConnected()
                        attempts = 0
                        startBackgroundTasks()
                        processQueuedEvents()
                        break
                    }
                }
            }
        }
        
        fun stop() {
            reconnectJob?.cancel()
        }
    }
    
    private inner class MetricsCollector {
        private var eventsSent = AtomicInteger(0)
        private var briefsGenerated = AtomicInteger(0)
        private var connections = AtomicInteger(0)
        
        fun recordEventSent() = eventsSent.incrementAndGet()
        fun recordBriefGenerated() = briefsGenerated.incrementAndGet()
        fun recordConnection() = connections.incrementAndGet()
        
        fun logMetrics() {
            if (settings.debugMode) {
                logger.info("📊 Metrics - Events: ${eventsSent.get()}, Briefs: ${briefsGenerated.get()}, Connections: ${connections.get()}, Queue: ${eventQueue.size}")
            }
        }
    }
}

// Enhanced data classes
data class QueuedEvent(
    val type: String,
    val source: String,
    val projectPath: String?,
    val filePath: String?,
    val description: String?,
    val metadata: Map<String, Any>,
    val timestamp: Long,
    val retryCount: Int
) {
    fun shouldRetry(): Boolean {
        val age = System.currentTimeMillis() - timestamp
        return retryCount < 3 && age < 300_000 // Max 3 retries within 5 minutes
    }
    
    fun withRetry(): QueuedEvent = copy(retryCount = retryCount + 1)
}

data class MorningBrief(
    val developerId: String,
    val generatedAt: String,
    val greeting: String?,
    val summary: String,
    val activityOverview: Map<String, Any>,
    val criticalItems: List<CriticalItem>,
    val suggestions: List<Suggestion>,
    val insights: Map<String, Any>
)

data class CriticalItem(
    val type: String,
    val priority: String,
    val title: String,
    val description: String,
    val actionRequired: Boolean = false,
    val files: List<FileIssue> = emptyList(),
    val count: Int = 0,
    val metadata: Map<String, Any> = emptyMap()
)

data class Suggestion(
    val type: String,
    val title: String,
    val description: String,
    val priority: String,
    val action: String?,
    val files: List<FileIssue> = emptyList(),
    val metadata: Map<String, Any> = emptyMap()
)

data class FileIssue(
    val filePath: String,
    val lineNumber: Int? = null,
    val description: String,
    val severity: String = "medium",
    val ruleId: String? = null,
    val category: String? = null
)

data class AgentStatus(
    val status: String,
    val message: String? = null,
    val eventsCount: Int = 0,
    val lastBrief: String? = null,
    val isMonitoring: Boolean = false,
    val queuedEvents: Int = 0,
    val connectionUptime: Long = 0,
    val lastConnectionAttempt: String? = null,
    val circuitBreakerOpen: Boolean = false
)

data class ConnectionTestResult(
    val success: Boolean,
    val latencyMs: Long = 0,
    val message: String,
    val endpoint: String,
    val error: String? = null
) 
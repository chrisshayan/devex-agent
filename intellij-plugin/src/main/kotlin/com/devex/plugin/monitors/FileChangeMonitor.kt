package com.devex.plugin.monitors

import com.intellij.openapi.diagnostic.Logger
import com.intellij.openapi.vfs.VirtualFile
import com.intellij.openapi.vfs.VirtualFileEvent
import com.intellij.openapi.vfs.VirtualFileListener
import com.intellij.openapi.vfs.VirtualFileManager
import com.intellij.openapi.vfs.VirtualFileManagerListener
import com.intellij.openapi.project.Project
import com.intellij.openapi.project.ProjectManager
import com.devex.plugin.services.AmbientAgentService
import kotlinx.coroutines.*

/**
 * File Change Monitor - Detects file system events for ambient agent processing
 * 
 * Following ambient agent patterns:
 * - Event-driven monitoring
 * - Non-intrusive background operation
 * - Automatic event forwarding to agent core
 */
class FileChangeMonitor : VirtualFileManagerListener {
    
    private val logger = Logger.getInstance(FileChangeMonitor::class.java)
    private val agentService = AmbientAgentService.getInstance()
    private val monitorScope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    
    // Event filtering to avoid spam
    private val lastEventTimes = mutableMapOf<String, Long>()
    private val eventCooldownMs = 2000L // 2 seconds between similar events
    
    init {
        logger.info("🔍 Starting DevEx Ambient File Change Monitor...")
        VirtualFileManager.getInstance().addVirtualFileManagerListener(this)
    }
    
    override fun after(events: MutableList<out VirtualFileEvent>) {
        // Process file change events
        for (event in events) {
            processFileEvent(event)
        }
    }
    
    private fun processFileEvent(event: VirtualFileEvent) {
        val file = event.file
        
        // Filter out irrelevant files
        if (!shouldMonitorFile(file)) {
            return
        }
        
        // Implement event cooldown to prevent spam
        val eventKey = "${file.path}_${event.javaClass.simpleName}"
        val currentTime = System.currentTimeMillis()
        val lastEventTime = lastEventTimes[eventKey] ?: 0
        
        if (currentTime - lastEventTime < eventCooldownMs) {
            return // Skip this event due to cooldown
        }
        
        lastEventTimes[eventKey] = currentTime
        
        // Determine event type and send to agent
        monitorScope.launch {
            try {
                val eventType = when {
                    event is VirtualFileEvent -> when {
                        file.exists() -> "file_changed"
                        else -> "file_deleted"
                    }
                    else -> "file_event"
                }
                
                val project = findProjectForFile(file)
                val projectPath = project?.basePath
                val description = generateEventDescription(eventType, file)
                val metadata = collectFileMetadata(file, event)
                
                logger.debug("📝 Detected $eventType: ${file.name}")
                
                agentService.sendEvent(
                    type = eventType,
                    source = "intellij",
                    projectPath = projectPath,
                    filePath = file.path,
                    description = description,
                    metadata = metadata
                )
                
            } catch (e: Exception) {
                logger.error("❌ Error processing file event", e)
            }
        }
    }
    
    private fun shouldMonitorFile(file: VirtualFile): Boolean {
        // Only monitor relevant files for development
        val path = file.path.lowercase()
        val name = file.name.lowercase()
        
        // Skip system/temp files
        if (path.contains("/.idea/") || 
            path.contains("/target/") || 
            path.contains("/build/") ||
            path.contains("/node_modules/") ||
            path.contains("/.git/") ||
            name.startsWith(".")) {
            return false
        }
        
        // Include source code files
        val sourceExtensions = setOf(
            "java", "kt", "scala", "py", "js", "ts", "tsx", "jsx",
            "c", "cpp", "h", "hpp", "cs", "go", "rs", "rb",
            "php", "swift", "m", "mm", "sql", "xml", "json",
            "yaml", "yml", "properties", "gradle", "pom"
        )
        
        val extension = file.extension?.lowercase()
        return extension in sourceExtensions
    }
    
    private fun findProjectForFile(file: VirtualFile): Project? {
        val projectManager = ProjectManager.getInstance()
        
        for (project in projectManager.openProjects) {
            if (project.isDisposed) continue
            
            val projectFile = project.projectFile
            val baseDir = project.baseDir
            
            when {
                baseDir != null && file.path.startsWith(baseDir.path) -> return project
                projectFile != null && file.path.startsWith(projectFile.parent.path) -> return project
            }
        }
        
        return null
    }
    
    private fun generateEventDescription(eventType: String, file: VirtualFile): String {
        return when (eventType) {
            "file_changed" -> "Modified ${file.name}"
            "file_deleted" -> "Deleted ${file.name}"
            "file_created" -> "Created ${file.name}"
            else -> "File event: ${file.name}"
        }
    }
    
    private fun collectFileMetadata(file: VirtualFile, event: VirtualFileEvent): Map<String, Any> {
        val metadata = mutableMapOf<String, Any>()
        
        try {
            metadata["file_extension"] = file.extension ?: ""
            metadata["file_size"] = file.length
            metadata["is_directory"] = file.isDirectory
            metadata["modification_timestamp"] = file.timeStamp
            
            // Estimate lines changed (simplified)
            if (file.extension in setOf("java", "kt", "py", "js", "ts")) {
                try {
                    val content = String(file.contentsToByteArray())
                    val lineCount = content.lines().size
                    metadata["estimated_lines"] = lineCount
                    
                    // Simple heuristic for change size
                    when {
                        lineCount > 500 -> metadata["change_size"] = "large"
                        lineCount > 100 -> metadata["change_size"] = "medium"
                        else -> metadata["change_size"] = "small"
                    }
                } catch (e: Exception) {
                    // Ignore errors in content analysis
                }
            }
            
        } catch (e: Exception) {
            logger.debug("Error collecting file metadata: ${e.message}")
        }
        
        return metadata
    }
    
    fun dispose() {
        logger.info("🛑 Disposing File Change Monitor...")
        VirtualFileManager.getInstance().removeVirtualFileManagerListener(this)
        monitorScope.cancel()
    }
} 
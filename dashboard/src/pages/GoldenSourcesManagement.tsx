import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import {
  Server,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Settings,
  Activity,
  
  Star,
  Database,
  Globe,
  FileText,
  
  Plus,
  RefreshCw
} from 'lucide-react'
import LoadingSpinner from '../components/LoadingSpinner'
import { fetchGoldenSourcesList, registerGoldenSource, ingestGoldenSource, getGoldenSourceHealth } from '../services/api'

interface GoldenSource {
  id: string
  name: string
  type: 'github' | 'confluence' | 'documentation' | 'filesystem'
  url: string
  status: 'healthy' | 'warning' | 'error' | 'offline'
  last_sync: string
  alignment_score: number
  total_documents: number
  last_update: string
  enabled: boolean
  config: {
    auto_sync: boolean
    sync_frequency: string
    quality_threshold: number
  }
}

// interface SourceHealth {
//   uptime: number
//   response_time: number
//   success_rate: number
//   last_error?: string
//   sync_status: 'syncing' | 'completed' | 'failed' | 'idle'
// }

export default function GoldenSourcesManagement() {
  const { developerId } = useParams<{ developerId: string }>()
  const [sources, setSources] = useState<GoldenSource[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedSource, setSelectedSource] = useState<GoldenSource | null>(null)
  const [showAddModal, setShowAddModal] = useState(false)
  const [newSource, setNewSource] = useState({
    name: '',
    type: 'github' as 'github' | 'confluence' | 'documentation' | 'filesystem',
    url: '',
    auto_sync: true,
    quality_threshold: 0.8
  })

  // Default developer ID if not provided in URL
  const currentDeveloperId = developerId || 'chrisshayan'

  useEffect(() => {
    loadGoldenSources()
  }, [currentDeveloperId])

  const loadGoldenSources = async () => {
    try {
      setLoading(true)
      setError(null)
      
      // Use real API call
      const response = await fetchGoldenSourcesList(currentDeveloperId)
      
      if (response && response.sources) {
        setSources(response.sources)
      } else {
        // Fallback if no sources returned
        setSources([])
      }
      
    } catch (err) {
      console.error('Error loading golden sources:', err)
      setError('Failed to load golden sources. The service may be unavailable.')
      
      // Fallback to demo data if API fails
      const fallbackSources: GoldenSource[] = [
        {
          id: 'github-react',
          name: 'Facebook React Repository',
          type: 'github',
          url: 'https://github.com/facebook/react',
          status: 'healthy',
          last_sync: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
          alignment_score: 95,
          total_documents: 1247,
          last_update: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(),
          enabled: true,
          config: {
            auto_sync: true,
            sync_frequency: 'daily',
            quality_threshold: 0.8
          }
        },
        {
          id: 'typescript-handbook',
          name: 'TypeScript Official Handbook',
          type: 'documentation',
          url: 'https://www.typescriptlang.org/docs/',
          status: 'healthy',
          last_sync: new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString(),
          alignment_score: 92,
          total_documents: 423,
          last_update: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
          enabled: true,
          config: {
            auto_sync: true,
            sync_frequency: 'weekly',
            quality_threshold: 0.85
          }
        }
      ]
      setSources(fallbackSources)
      
    } finally {
      setLoading(false)
    }
  }

  const handleAddSource = async () => {
    try {
      // Map UI form to backend GoldenSourceConfig schema
      const type = newSource.type === 'documentation' ? 'file' : newSource.type
      const payload: any = {
        type,
        priority: 'medium',
        auto_sync: newSource.auto_sync,
        sync_interval: newSource.auto_sync ? '1d' : '7d',
        enabled: true,
        // source-specific config
        config: type === 'github'
          ? {
              name: newSource.name,
              repository: newSource.url.replace('https://github.com/',''),
              branch: 'main',
              include_patterns: [],
              exclude_patterns: [],
              include_issues: true,
              include_prs: true,
              include_wiki: true
            }
          : type === 'confluence'
          ? {
              name: newSource.name,
              base_url: newSource.url,
              space_key: 'DOCS',
              page_filter: undefined,
              username: '',
              api_token: '',
              include_attachments: true,
              include_comments: false
            }
          : {
              name: newSource.name,
              path: newSource.url || '.',
              include_extensions: ['.md', '.txt', '.py', '.ts', '.tsx'],
              exclude_directories: ['.git','node_modules','dist','build','__pycache__'],
              recursive: true
            }
      }

      await registerGoldenSource(payload)

      // Refresh list from backend
      await loadGoldenSources()

      setShowAddModal(false)
    } catch (err) {
      console.error('Error adding source:', err)
      alert('❌ Failed to add golden source. Please check configuration and try again.')
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy': return <CheckCircle2 className="w-5 h-5 text-green-500" />
      case 'warning': return <AlertTriangle className="w-5 h-5 text-yellow-500" />
      case 'error': return <XCircle className="w-5 h-5 text-red-500" />
      case 'offline': return <XCircle className="w-5 h-5 text-gray-500" />
      default: return <Activity className="w-5 h-5 text-gray-400" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'bg-green-100 text-green-800 border-green-200'
      case 'warning': return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'error': return 'bg-red-100 text-red-800 border-red-200'
      case 'offline': return 'bg-gray-100 text-gray-800 border-gray-200'
      default: return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'github': return <Database className="w-4 h-4" />
      case 'confluence': return <Globe className="w-4 h-4" />
      case 'documentation': return <FileText className="w-4 h-4" />
      case 'filesystem': return <Server className="w-4 h-4" />
      default: return <Database className="w-4 h-4" />
    }
  }

  const handleSync = async (sourceId: string) => {
    try {
      await ingestGoldenSource(sourceId, true)
      // Optionally poll health to update last_sync and counts
      setTimeout(async () => {
        try {
          await getGoldenSourceHealth(sourceId)
          await loadGoldenSources()
        } catch {}
      }, 1500)
    } catch (err) {
      console.error('Sync failed:', err)
      alert('❌ Sync failed. Please check backend logs for details.')
    }
  }

  const handleToggleEnabled = async (sourceId: string) => {
    setSources(sources.map(source => 
      source.id === sourceId 
        ? { ...source, enabled: !source.enabled }
        : source
    ))
  }

  const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60))
    
    if (diffInHours < 1) return 'Just now'
    if (diffInHours < 24) return `${diffInHours}h ago`
    const diffInDays = Math.floor(diffInHours / 24)
    return `${diffInDays}d ago`
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <h3 className="text-red-800 font-medium">Error Loading Golden Sources</h3>
        <p className="text-red-600 mt-2">{error}</p>
        <button 
          onClick={loadGoldenSources}
          className="mt-4 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
        >
          Retry
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg p-8 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">Golden Sources Management</h1>
            <p className="text-blue-100 text-lg">
              Manage and monitor your trusted knowledge sources for AI-powered insights
            </p>
          </div>
          <div className="hidden md:block">
            <Star className="h-20 w-20 text-blue-200" />
          </div>
        </div>
        
        <div className="mt-6 grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white bg-opacity-20 rounded-lg p-4">
            <div className="text-2xl font-bold">{sources.length}</div>
            <div className="text-blue-100 text-sm">Total Sources</div>
          </div>
          <div className="bg-white bg-opacity-20 rounded-lg p-4">
            <div className="text-2xl font-bold">{sources.filter(s => s.status === 'healthy').length}</div>
            <div className="text-blue-100 text-sm">Healthy Sources</div>
          </div>
          <div className="bg-white bg-opacity-20 rounded-lg p-4">
            <div className="text-2xl font-bold">{sources.reduce((sum, s) => sum + s.total_documents, 0).toLocaleString()}</div>
            <div className="text-blue-100 text-sm">Total Documents</div>
          </div>
          <div className="bg-white bg-opacity-20 rounded-lg p-4">
            <div className="text-2xl font-bold">{Math.round(sources.reduce((sum, s) => sum + s.alignment_score, 0) / sources.length)}%</div>
            <div className="text-blue-100 text-sm">Avg Alignment</div>
          </div>
        </div>
      </div>

      {/* Actions Bar */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <h2 className="text-xl font-semibold text-gray-900">Golden Sources</h2>
          <button
            onClick={loadGoldenSources}
            className="flex items-center space-x-2 px-3 py-2 text-sm bg-gray-100 hover:bg-gray-200 rounded-md transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Refresh</span>
          </button>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
        >
          <Plus className="w-4 h-4" />
          <span>Add Source</span>
        </button>
      </div>

      {/* Sources Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {sources.map((source) => (
          <div key={source.id} className="bg-white rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-shadow">
            <div className="p-6">
              {/* Source Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className="flex-shrink-0">
                    {getTypeIcon(source.type)}
                  </div>
                  <div>
                    <h3 className="text-lg font-medium text-gray-900">{source.name}</h3>
                    <p className="text-sm text-gray-500">{source.url}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  {getStatusIcon(source.status)}
                  <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(source.status)}`}>
                    {source.status}
                  </span>
                </div>
              </div>

              {/* Metrics */}
              <div className="grid grid-cols-3 gap-4 mb-4">
                <div className="text-center">
                  <div className="text-lg font-semibold text-gray-900">{source.alignment_score}%</div>
                  <div className="text-xs text-gray-500">Alignment</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-semibold text-gray-900">{source.total_documents.toLocaleString()}</div>
                  <div className="text-xs text-gray-500">Documents</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-semibold text-gray-900">{formatTimeAgo(source.last_sync)}</div>
                  <div className="text-xs text-gray-500">Last Sync</div>
                </div>
              </div>

              {/* Progress Bar for Alignment */}
              <div className="mb-4">
                <div className="flex items-center justify-between text-sm text-gray-600 mb-1">
                  <span>Alignment Score</span>
                  <span>{source.alignment_score}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full ${
                      source.alignment_score >= 90 ? 'bg-green-500' :
                      source.alignment_score >= 80 ? 'bg-yellow-500' : 'bg-red-500'
                    }`}
                    style={{ width: `${source.alignment_score}%` }}
                  ></div>
                </div>
              </div>

              {/* Configuration */}
              <div className="space-y-2 text-sm text-gray-600 mb-4">
                <div className="flex items-center justify-between">
                  <span>Auto Sync:</span>
                  <span className={source.config.auto_sync ? 'text-green-600' : 'text-gray-500'}>
                    {source.config.auto_sync ? 'Enabled' : 'Disabled'}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span>Frequency:</span>
                  <span className="capitalize">{source.config.sync_frequency}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span>Quality Threshold:</span>
                  <span>{Math.round(source.config.quality_threshold * 100)}%</span>
                </div>
              </div>

              {/* Actions */}
              <div className="flex items-center justify-between pt-4 border-t border-gray-100">
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => handleSync(source.id)}
                    className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                  >
                    Sync Now
                  </button>
                  <button
                    onClick={() => setSelectedSource(source)}
                    className="text-gray-600 hover:text-gray-800 text-sm font-medium"
                  >
                    <Settings className="w-4 h-4" />
                  </button>
                </div>
                <div className="flex items-center space-x-2">
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={source.enabled}
                      onChange={() => handleToggleEnabled(source.id)}
                      className="sr-only peer"
                    />
                    <div className="w-9 h-5 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-blue-600"></div>
                  </label>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Source Details Modal */}
      {selectedSource && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium">Source Configuration</h3>
              <button
                onClick={() => setSelectedSource(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                <XCircle className="w-5 h-5" />
              </button>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
                <input
                  type="text"
                  value={selectedSource.name}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  readOnly
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">URL</label>
                <input
                  type="url"
                  value={selectedSource.url}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  readOnly
                />
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Sync Frequency</label>
                  <select className="w-full px-3 py-2 border border-gray-300 rounded-md">
                    <option value="manual">Manual</option>
                    <option value="daily">Daily</option>
                    <option value="weekly">Weekly</option>
                    <option value="monthly">Monthly</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Quality Threshold</label>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.05"
                    value={selectedSource.config.quality_threshold}
                    className="w-full"
                  />
                  <div className="text-xs text-gray-500 mt-1">
                    {Math.round(selectedSource.config.quality_threshold * 100)}%
                  </div>
                </div>
              </div>
              
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="auto-sync"
                  checked={selectedSource.config.auto_sync}
                  className="rounded"
                />
                <label htmlFor="auto-sync" className="text-sm text-gray-700">
                  Enable automatic synchronization
                </label>
              </div>
            </div>
            
            <div className="flex items-center justify-end space-x-3 mt-6">
              <button
                onClick={() => setSelectedSource(null)}
                className="px-4 py-2 text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={() => setSelectedSource(null)}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                Save Changes
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Add Source Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium">Add New Golden Source</h3>
              <button
                onClick={() => setShowAddModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <XCircle className="w-5 h-5" />
              </button>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Name *</label>
                <input
                  type="text"
                  value={newSource.name}
                  onChange={(e) => setNewSource({...newSource, name: e.target.value})}
                  placeholder="e.g., React Official Documentation"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Type *</label>
                <select 
                  value={newSource.type}
                  onChange={(e) => setNewSource({...newSource, type: e.target.value as any})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="github">GitHub Repository</option>
                  <option value="documentation">Documentation Site</option>
                  <option value="confluence">Confluence Wiki</option>
                  <option value="filesystem">File System</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">URL *</label>
                <input
                  type="url"
                  value={newSource.url}
                  onChange={(e) => setNewSource({...newSource, url: e.target.value})}
                  placeholder="https://github.com/facebook/react"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Quality Threshold</label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.05"
                  value={newSource.quality_threshold}
                  onChange={(e) => setNewSource({...newSource, quality_threshold: parseFloat(e.target.value)})}
                  className="w-full"
                />
                <div className="text-xs text-gray-500 mt-1">
                  {Math.round(newSource.quality_threshold * 100)}% - Minimum quality score for content inclusion
                </div>
              </div>
              
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="auto-sync-new"
                  checked={newSource.auto_sync}
                  onChange={(e) => setNewSource({...newSource, auto_sync: e.target.checked})}
                  className="rounded"
                />
                <label htmlFor="auto-sync-new" className="text-sm text-gray-700">
                  Enable automatic synchronization
                </label>
              </div>
            </div>
            
            <div className="flex items-center justify-end space-x-3 mt-6">
              <button
                onClick={() => setShowAddModal(false)}
                className="px-4 py-2 text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleAddSource}
                disabled={!newSource.name || !newSource.url}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Add Source
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
} 
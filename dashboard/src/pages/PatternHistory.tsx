import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import {
  TrendingUp,
  TrendingDown,
  Activity,
  Clock,
  BarChart3,
  Target,
  Award,
  Brain,
  Code,
  Star,
  Calendar,
  Filter,
  Download,
  Eye,
  ChevronRight,
  AlertCircle,
  CheckCircle2
} from 'lucide-react'
import LoadingSpinner from '../components/LoadingSpinner'
import { fetchPatternHistory, fetchSkillProgression, fetchCoachingMetrics } from '../services/api'

interface PatternEvolution {
  id: string
  pattern_name: string
  category: 'architectural' | 'behavioral' | 'performance' | 'security'
  first_detected: string
  confidence_history: Array<{
    date: string
    confidence: number
    occurrences: number
  }>
  current_confidence: number
  trend: 'improving' | 'declining' | 'stable'
  impact_score: number
  files_affected: string[]
}

interface SkillProgression {
  skill_name: string
  level_history: Array<{
    date: string
    level: number
    assessment_type: 'codebert' | 'coaching' | 'self_assessment'
  }>
  current_level: number
  target_level: number
  progression_rate: number
  coaching_sessions: number
}

interface CoachingMetric {
  metric_name: string
  category: 'engagement' | 'effectiveness' | 'outcome'
  value: number
  trend: number
  benchmark: number
  last_updated: string
}

export default function PatternHistory() {
  const { developerId } = useParams<{ developerId: string }>()
  const [patterns, setPatterns] = useState<PatternEvolution[]>([])
  const [skills, setSkills] = useState<SkillProgression[]>([])
  const [coachingMetrics, setCoachingMetrics] = useState<CoachingMetric[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedTimeframe, setSelectedTimeframe] = useState('3months')
  const [selectedCategory, setSelectedCategory] = useState('all')

  // Default developer ID if not provided in URL
  const currentDeveloperId = developerId || 'chrisshayan'

  useEffect(() => {
    loadPatternHistory()
  }, [selectedTimeframe, selectedCategory, currentDeveloperId])

  const loadPatternHistory = async () => {
    try {
      setLoading(true)
      setError(null)
      
      // Use real API calls
      const [patternResponse, skillResponse, coachingResponse] = await Promise.all([
        fetchPatternHistory(currentDeveloperId, selectedTimeframe),
        fetchSkillProgression(currentDeveloperId, selectedTimeframe),
        fetchCoachingMetrics(currentDeveloperId)
      ])
      
      // Set pattern data
      if (patternResponse && patternResponse.patterns) {
        setPatterns(patternResponse.patterns)
      }
      
      // Set skill data
      if (skillResponse && skillResponse.skills) {
        setSkills(skillResponse.skills)
      }
      
      // Set coaching metrics
      if (coachingResponse && coachingResponse.metrics) {
        setCoachingMetrics(coachingResponse.metrics)
      }
      
    } catch (err) {
      console.error('Error loading pattern history:', err)
      setError('Failed to load pattern history. Some services may be unavailable.')
      
      // Fallback to minimal demo data if API fails
      setPatterns([
        {
          id: 'react-patterns',
          pattern_name: 'React Component Patterns',
          category: 'architectural',
          first_detected: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000).toISOString(),
          confidence_history: [
            { date: '2023-11-01', confidence: 70, occurrences: 8 },
            { date: '2023-12-01', confidence: 82, occurrences: 15 },
            { date: '2024-01-01', confidence: 90, occurrences: 23 },
            { date: '2024-01-15', confidence: 95, occurrences: 31 }
          ],
          current_confidence: 95,
          trend: 'improving',
          impact_score: 8.5,
          files_affected: ['Dashboard.tsx', 'components/']
        }
      ])
      
      setSkills([
        {
          skill_name: 'React Development',
          level_history: [
            { date: '2023-11-01', level: 7.2, assessment_type: 'codebert' },
            { date: '2023-12-01', level: 7.8, assessment_type: 'coaching' },
            { date: '2024-01-01', level: 8.3, assessment_type: 'codebert' },
            { date: '2024-01-15', level: 8.7, assessment_type: 'coaching' }
          ],
          current_level: 8.7,
          target_level: 9.5,
          progression_rate: 0.15,
          coaching_sessions: 8
        }
      ])
      
      setCoachingMetrics([
        {
          metric_name: 'Suggestion Adoption Rate',
          category: 'effectiveness',
          value: 78,
          trend: 12,
          benchmark: 65,
          last_updated: new Date().toISOString()
        },
        {
          metric_name: 'Learning Velocity',
          category: 'outcome',
          value: 1.8,
          trend: 0.2,
          benchmark: 1.3,
          last_updated: new Date().toISOString()
        }
      ])
      
    } finally {
      setLoading(false)
    }
  }

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'improving': return <TrendingUp className="w-4 h-4 text-green-500" />
      case 'declining': return <TrendingDown className="w-4 h-4 text-red-500" />
      case 'stable': return <Activity className="w-4 h-4 text-gray-500" />
      default: return <Activity className="w-4 h-4 text-gray-500" />
    }
  }

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'architectural': return 'bg-blue-100 text-blue-800'
      case 'behavioral': return 'bg-green-100 text-green-800'
      case 'performance': return 'bg-yellow-100 text-yellow-800'
      case 'security': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    })
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
        <h3 className="text-red-800 font-medium">Error Loading Pattern History</h3>
        <p className="text-red-600 mt-2">{error}</p>
        <button 
          onClick={loadPatternHistory}
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
      <div className="bg-gradient-to-r from-purple-600 to-indigo-600 rounded-lg p-8 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">Pattern History & Analytics</h1>
            <p className="text-purple-100 text-lg">
              Track the evolution of your coding patterns and skill progression over time
            </p>
          </div>
          <div className="hidden md:block">
            <BarChart3 className="h-20 w-20 text-purple-200" />
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Timeframe</label>
            <select
              value={selectedTimeframe}
              onChange={(e) => setSelectedTimeframe(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md text-sm"
            >
              <option value="1month">Last Month</option>
              <option value="3months">Last 3 Months</option>
              <option value="6months">Last 6 Months</option>
              <option value="1year">Last Year</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md text-sm"
            >
              <option value="all">All Categories</option>
              <option value="architectural">Architectural</option>
              <option value="behavioral">Behavioral</option>
              <option value="performance">Performance</option>
              <option value="security">Security</option>
            </select>
          </div>
        </div>
        <button className="flex items-center space-x-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-md transition-colors">
          <Download className="w-4 h-4" />
          <span>Export Data</span>
        </button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Code className="h-8 w-8 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Patterns Tracked</p>
              <p className="text-2xl font-semibold text-gray-900">{patterns.length}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <TrendingUp className="h-8 w-8 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Improving Patterns</p>
              <p className="text-2xl font-semibold text-gray-900">
                {patterns.filter(p => p.trend === 'improving').length}
              </p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Star className="h-8 w-8 text-yellow-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Avg Confidence</p>
              <p className="text-2xl font-semibold text-gray-900">
                {Math.round(patterns.reduce((sum, p) => sum + p.current_confidence, 0) / patterns.length)}%
              </p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Brain className="h-8 w-8 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Coaching Sessions</p>
              <p className="text-2xl font-semibold text-gray-900">
                {skills.reduce((sum, s) => sum + s.coaching_sessions, 0)}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Pattern Evolution */}
      <div className="bg-white rounded-lg border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Pattern Evolution Timeline</h3>
        </div>
        <div className="p-6">
          <div className="space-y-6">
            {patterns.map((pattern) => (
              <div key={pattern.id} className="border border-gray-100 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center space-x-3">
                    <h4 className="text-lg font-medium text-gray-900">{pattern.pattern_name}</h4>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getCategoryColor(pattern.category)}`}>
                      {pattern.category}
                    </span>
                    {getTrendIcon(pattern.trend)}
                  </div>
                  <div className="text-sm text-gray-500">
                    Since {formatDate(pattern.first_detected)}
                  </div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                  <div>
                    <div className="text-sm text-gray-600">Current Confidence</div>
                    <div className="text-xl font-semibold text-gray-900">{pattern.current_confidence}%</div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-600">Impact Score</div>
                    <div className="text-xl font-semibold text-gray-900">{pattern.impact_score}/10</div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-600">Files Affected</div>
                    <div className="text-xl font-semibold text-gray-900">{pattern.files_affected.length}</div>
                  </div>
                </div>
                
                {/* Mini confidence chart */}
                <div className="h-20 bg-gray-50 rounded flex items-end justify-between p-2">
                  {pattern.confidence_history.map((point, index) => (
                    <div
                      key={index}
                      className="bg-blue-500 rounded-t"
                      style={{
                        height: `${(point.confidence / 100) * 60}px`,
                        width: `${100 / pattern.confidence_history.length - 2}%`
                      }}
                      title={`${point.date}: ${point.confidence}%`}
                    />
                  ))}
                </div>
                
                <div className="mt-3 flex items-center justify-between">
                  <div className="flex flex-wrap gap-1">
                    {pattern.files_affected.slice(0, 3).map((file, index) => (
                      <span key={index} className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
                        {file}
                      </span>
                    ))}
                    {pattern.files_affected.length > 3 && (
                      <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
                        +{pattern.files_affected.length - 3} more
                      </span>
                    )}
                  </div>
                  <button className="text-blue-600 hover:text-blue-800 text-sm font-medium flex items-center">
                    View Details <ChevronRight className="w-4 h-4 ml-1" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Skill Progression */}
      <div className="bg-white rounded-lg border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Skill Progression Insights</h3>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {skills.map((skill, index) => (
              <div key={index} className="border border-gray-100 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="text-lg font-medium text-gray-900">{skill.skill_name}</h4>
                  <div className="text-sm text-gray-500">
                    {skill.coaching_sessions} sessions
                  </div>
                </div>
                
                <div className="mb-4">
                  <div className="flex justify-between text-sm text-gray-600 mb-1">
                    <span>Current Level</span>
                    <span>{skill.current_level}/10</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-green-500 h-2 rounded-full" 
                      style={{ width: `${(skill.current_level / 10) * 100}%` }}
                    />
                  </div>
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>Target: {skill.target_level}/10</span>
                    <span>Rate: +{skill.progression_rate}/month</span>
                  </div>
                </div>
                
                {/* Mini skill progression chart */}
                <div className="h-16 bg-gray-50 rounded flex items-end justify-between p-2">
                  {skill.level_history.map((point, index) => (
                    <div
                      key={index}
                      className="bg-green-500 rounded-t"
                      style={{
                        height: `${(point.level / 10) * 48}px`,
                        width: `${100 / skill.level_history.length - 2}%`
                      }}
                      title={`${point.date}: ${point.level}/10`}
                    />
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Coaching Effectiveness Metrics */}
      <div className="bg-white rounded-lg border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Coaching Effectiveness Metrics</h3>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {coachingMetrics.map((metric, index) => (
              <div key={index} className="text-center">
                <div className="text-2xl font-bold text-gray-900">
                  {metric.metric_name.includes('Rate') || metric.metric_name.includes('Improvement') 
                    ? `${metric.value}%` 
                    : metric.value}
                </div>
                <div className="text-sm text-gray-600 mb-2">{metric.metric_name}</div>
                <div className={`flex items-center justify-center text-xs ${
                  metric.trend > 0 ? 'text-green-600' : metric.trend < 0 ? 'text-red-600' : 'text-gray-600'
                }`}>
                  {metric.trend > 0 ? (
                    <TrendingUp className="w-3 h-3 mr-1" />
                  ) : metric.trend < 0 ? (
                    <TrendingDown className="w-3 h-3 mr-1" />
                  ) : (
                    <Activity className="w-3 h-3 mr-1" />
                  )}
                  {metric.trend > 0 ? '+' : ''}{metric.trend}
                  {metric.metric_name.includes('Rate') || metric.metric_name.includes('Improvement') ? '%' : ''}
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  Benchmark: {metric.benchmark}
                  {metric.metric_name.includes('Rate') || metric.metric_name.includes('Improvement') ? '%' : ''}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
} 
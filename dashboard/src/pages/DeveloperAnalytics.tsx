import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { 
  TrendingUp, 
  Users, 
  Award, 
  Clock,
  BarChart3,
  Activity,
  Target,
  Zap,
  BookOpen,
  Code,
  GitBranch,
  Brain,
  Star,
  CheckCircle2,
  ArrowUp,
  ArrowDown,
  Minus,
  Trophy,
  Calendar,
  ChevronRight,
  AlertCircle,
  User,
  Settings,
  Lightbulb,
  TrendingDown
} from 'lucide-react'
import MetricCard from '../components/MetricCard'
import SkillProgressChart from '../components/charts/SkillProgressChart'
import CodeQualityChart from '../components/charts/CodeQualityChart'
import LearningVelocityChart from '../components/charts/LearningVelocityChart'
import CoachingImpactChart from '../components/charts/CoachingImpactChart'
import LoadingSpinner from '../components/LoadingSpinner'
import { 
  fetchDeveloperDashboard,
  fetchDeveloperSkillsTimeline,
  fetchDeveloperCodeQualityTrends,
  fetchDeveloperLearningVelocity,
  fetchDeveloperCoachingImpact
} from '../services/api'

// Real API response interfaces based on actual data structure
interface DashboardData {
  status: string
  developer_id: string
  dashboard: {
    developer_id: string
    dashboard_id: string
    generated_at: string
    skill_progression: Array<{
      developer_id: string
      skill_name: string
      skill_category: string
      timeline_data: Array<{
        timestamp: string
        level: number
        velocity: number
        milestone_events: any[]
      }>
      trend_analysis: {
        trend: string
        slope: number
        average_level: number
        variance: number
        improvement_rate: number
      }
      projected_progression: {
        projected_level: number
        confidence: number
        trend_continuation: boolean
        estimated_mastery_months: number
      }
      confidence_intervals: {
        low: number
        high: number
        confidence: number
      }
      first_assessment: string
      last_updated: string
      total_data_points: number
    }>
    code_quality: {
      developer_id: string
      metric_id: string
      complexity_timeline: Array<{
        timestamp: string
        score: number
        trend: string
      }>
      pattern_adoption_timeline: Array<{
        timestamp: string
        score: number
        trend: string
      }>
      security_score_timeline: Array<{
        timestamp: string
        score: number
        trend: string
      }>
      maintainability_timeline: Array<{
        timestamp: string
        score: number
        trend: string
      }>
      test_coverage_timeline: Array<{
        timestamp: string
        score: number
        trend: string
      }>
      golden_source_similarity: Array<{
        timestamp: string
        similarity_score: number
        golden_source_alignment: string
      }>
      quality_trend: string
      improvement_rate: number
      assessment_period_start: string
      assessment_period_end: string
      total_commits_analyzed: number
    }
    learning_velocity: {
      developer_id: string
      analysis_id: string
      skills_per_month: number
      learning_consistency_score: number
      learning_efficiency: number
      velocity_timeline: Array<{
        timestamp: string
        velocity: number
        skill_count: number
        engagement: number
      }>
      acceleration_timeline: Array<{
        timestamp: string
        acceleration: number
        velocity_change: boolean
      }>
      coaching_correlation: number
      resource_effectiveness: {
        books: number
        courses: number
        projects: number
        tutorials: number
      }
      milestone_completion_impact: number
      predicted_velocity_3months: number
      predicted_velocity_6months: number
      velocity_factors: {
        coaching_frequency: number
        milestone_completion: number
        resource_quality: number
        consistency: number
      }
      analysis_period_start: string
      analysis_period_end: string
      generated_at: string
    }
    coaching_impact: {
      developer_id: string
      analysis_id: string
      total_sessions: number
      suggestions_acceptance_rate: number
      skill_improvement_correlation: number
      coaching_velocity_impact: number
      session_effectiveness_timeline: Array<{
        timestamp: string
        effectiveness_score: number
        satisfaction: number
        suggestions_accepted: number
        theme: string
      }>
      high_impact_sessions: string[]
      coaching_themes: Record<string, number>
      before_after_metrics: {
        code_quality: { before: number; after: number; improvement: number }
        testing_practices: { before: number; after: number; improvement: number }
        architecture_understanding: { before: number; after: number; improvement: number }
      }
      long_term_impact: {
        skill_retention_rate: number
        behavior_change_persistence: number
        knowledge_transfer_to_peers: number
        overall_confidence_increase: number
      }
      developer_satisfaction_trend: Array<{
        timestamp: string
        satisfaction: number
        trend: string
      }>
      time_to_improvement: Record<string, number>
      coaching_roi_score: number
      career_progression_acceleration: number
      analysis_period_start: string
      analysis_period_end: string
      coaching_model_version: string
    }
    overall_progress_score: number
    career_stage_progression: {
      current_stage: string
      months_in_current_stage: number
      progression_to_next: number
      next_stage: string
      key_milestones_completed: string[]
      remaining_milestones: string[]
    }
    key_achievements: Array<{
      achievement: string
      date: string
      category: string
      impact: string
    }>
    areas_of_strength: string[]
    improvement_opportunities: string[]
    skill_mastery_timeline: Record<string, string>
    career_progression_forecast: {
      next_career_stage: string
      estimated_timeline: string
      key_requirements: string[]
      probability: number
    }
    dashboard_config: {
      time_period_days: number
    }
    refresh_frequency: string
  }
  generated_at: string
}

const DeveloperAnalytics = () => {
  const { developerId } = useParams<{ developerId: string }>()
  const [loading, setLoading] = useState(true)
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState('overview')

  useEffect(() => {
    const loadDashboardData = async () => {
      if (!developerId) return

      try {
        setLoading(true)
        setError(null)

        // Fetch dashboard data
        const dashboard = await fetchDeveloperDashboard(developerId)
        setDashboardData(dashboard)

      } catch (err) {
        console.error('Failed to load dashboard data:', err)
        setError('Failed to load dashboard data. Please try again.')
      } finally {
        setLoading(false)
      }
    }

    loadDashboardData()
  }, [developerId])

  const formatPercentage = (value: number): string => {
    return `${(value * 100).toFixed(1)}%`
  }

  const formatScore = (value: number): string => {
    return value.toFixed(2)
  }

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'improving': return <ArrowUp className="w-4 h-4 text-green-500" />
      case 'declining': return <ArrowDown className="w-4 h-4 text-red-500" />
      case 'stable': return <Minus className="w-4 h-4 text-gray-500" />
      default: return <Minus className="w-4 h-4 text-gray-500" />
    }
  }

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'high': return 'text-green-600 bg-green-100'
      case 'medium': return 'text-yellow-600 bg-yellow-100'
      case 'low': return 'text-blue-600 bg-blue-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  if (loading) return <LoadingSpinner />
  if (error) return <div className="p-6 text-red-600">{error}</div>
  if (!dashboardData) return <div className="p-6 text-gray-600">No data available</div>

  const { dashboard } = dashboardData

  const tabs = [
    { id: 'overview', label: 'Overview', icon: BarChart3 },
    { id: 'skills', label: 'Skills', icon: Star },
    { id: 'code-quality', label: 'Code Quality', icon: Code },
    { id: 'learning', label: 'Learning', icon: BookOpen },
    { id: 'coaching', label: 'Coaching', icon: Users },
    { id: 'career', label: 'Career', icon: Trophy }
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="py-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <User className="w-8 h-8 text-blue-600 mr-3" />
                <div>
                  <h1 className="text-3xl font-bold text-gray-900 capitalize">
                    {developerId} Analytics
                  </h1>
                  <p className="mt-1 text-sm text-gray-500">
                    Generated on {new Date(dashboard.generated_at).toLocaleDateString()}
                  </p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                  {dashboard.career_stage_progression.current_stage}
                </span>
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  Progress Score: {formatPercentage(dashboard.overall_progress_score)}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8">
            {tabs.map((tab) => {
              const Icon = tab.icon
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="w-4 h-4 mr-2" />
                  {tab.label}
                </button>
              )
            })}
          </nav>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="space-y-8">
            {/* Key Metrics Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
               <MetricCard
                 title="Overall Progress"
                 value={formatPercentage(dashboard.overall_progress_score)}
                 icon={Target}
                 trend={{ value: dashboard.overall_progress_score, direction: dashboard.overall_progress_score > 0.5 ? 'up' : 'neutral' }}
               />
               <MetricCard
                 title="Skills Per Month"
                 value={dashboard.learning_velocity.skills_per_month.toFixed(1)}
                 icon={Zap}
                 trend={{ value: dashboard.learning_velocity.skills_per_month, direction: 'up' }}
               />
               <MetricCard
                 title="Coaching ROI"
                 value={`${dashboard.coaching_impact.coaching_roi_score.toFixed(1)}x`}
                 icon={Users}
                 trend={{ value: dashboard.coaching_impact.coaching_roi_score, direction: 'up' }}
               />
               <MetricCard
                 title="Learning Efficiency"
                 value={formatPercentage(dashboard.learning_velocity.learning_efficiency)}
                 icon={Brain}
                 trend={{ value: dashboard.learning_velocity.learning_efficiency, direction: 'up' }}
               />
             </div>

            {/* Career Progression */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Career Progression</h2>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-600">Current Stage</span>
                    <span className="text-sm text-gray-500">
                      {dashboard.career_stage_progression.months_in_current_stage} months
                    </span>
                  </div>
                  <div className="text-lg font-medium text-gray-900 mb-4">
                    {dashboard.career_stage_progression.current_stage}
                  </div>
                  
                  <div className="mb-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-gray-600">Progress to Next Stage</span>
                      <span className="text-sm text-gray-900">
                        {formatPercentage(dashboard.career_stage_progression.progression_to_next)}
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-blue-600 h-2 rounded-full" 
                        style={{ width: `${dashboard.career_stage_progression.progression_to_next * 100}%` }}
                      ></div>
                    </div>
                    <div className="text-sm text-gray-600 mt-1">
                      Next: {dashboard.career_stage_progression.next_stage}
                    </div>
                  </div>

                  <div className="space-y-2">
                    <h4 className="text-sm font-medium text-gray-900">Completed Milestones</h4>
                    {dashboard.career_stage_progression.key_milestones_completed.map((milestone, index) => (
                      <div key={index} className="flex items-center text-sm text-green-600">
                        <CheckCircle2 className="w-4 h-4 mr-2" />
                        {milestone}
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <h4 className="text-sm font-medium text-gray-900 mb-3">Career Forecast</h4>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Next Stage:</span>
                      <span className="text-sm font-medium">{dashboard.career_progression_forecast.next_career_stage}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Estimated Timeline:</span>
                      <span className="text-sm font-medium">{dashboard.career_progression_forecast.estimated_timeline}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Probability:</span>
                      <span className="text-sm font-medium">{formatPercentage(dashboard.career_progression_forecast.probability)}</span>
                    </div>
                  </div>

                  <div className="mt-4">
                    <h5 className="text-xs font-medium text-gray-900 mb-2">Key Requirements</h5>
                    <div className="space-y-1">
                      {dashboard.career_progression_forecast.key_requirements.map((req, index) => (
                        <div key={index} className="flex items-center text-xs text-gray-600">
                          <ChevronRight className="w-3 h-3 mr-1" />
                          {req}
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="mt-4">
                    <h5 className="text-xs font-medium text-gray-900 mb-2">Remaining Milestones</h5>
                    <div className="space-y-1">
                      {dashboard.career_stage_progression.remaining_milestones.map((milestone, index) => (
                        <div key={index} className="flex items-center text-xs text-gray-600">
                          <AlertCircle className="w-3 h-3 mr-1" />
                          {milestone}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Key Achievements */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Recent Achievements</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {dashboard.key_achievements.map((achievement, index) => (
                  <div key={index} className="flex items-start space-x-3 p-4 border border-gray-200 rounded-lg">
                    <Trophy className="w-5 h-5 text-yellow-500 mt-0.5" />
                    <div className="flex-1 min-w-0">
                      <h4 className="text-sm font-medium text-gray-900">{achievement.achievement}</h4>
                      <div className="flex items-center mt-1 space-x-2">
                        <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${getImpactColor(achievement.impact)}`}>
                          {achievement.impact} impact
                        </span>
                        <span className="text-xs text-gray-500">{achievement.category}</span>
                      </div>
                      <p className="text-xs text-gray-500 mt-1">
                        {new Date(achievement.date).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Skill Mastery Timeline */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Skill Mastery Timeline</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {Object.entries(dashboard.skill_mastery_timeline).map(([skill, timeline]) => (
                  <div key={skill} className="p-4 border border-gray-200 rounded-lg">
                    <div className="flex items-center justify-between">
                      <h4 className="text-sm font-medium text-gray-900 capitalize">{skill}</h4>
                      <Calendar className="w-4 h-4 text-gray-400" />
                    </div>
                    <p className="text-lg font-semibold text-blue-600 mt-1">{timeline}</p>
                    <p className="text-xs text-gray-500">to mastery</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Skills Tab */}
        {activeTab === 'skills' && (
          <div className="space-y-8">
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-6">Skill Progression Timeline</h2>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {dashboard.skill_progression.map((skill, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-4">
                      <div>
                        <h3 className="text-lg font-medium text-gray-900 capitalize">{skill.skill_name}</h3>
                        <span className="text-sm text-gray-500 capitalize">{skill.skill_category}</span>
                      </div>
                      <div className="text-right">
                        <div className="text-lg font-semibold text-blue-600">
                          {formatPercentage(skill.timeline_data[skill.timeline_data.length - 1]?.level || 0)}
                        </div>
                        <div className="flex items-center text-sm text-gray-500">
                          {getTrendIcon(skill.trend_analysis.trend)}
                          <span className="ml-1">{skill.trend_analysis.trend}</span>
                        </div>
                      </div>
                    </div>

                    <div className="space-y-3">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Improvement Rate:</span>
                        <span className="font-medium">{skill.trend_analysis.improvement_rate.toFixed(1)}x</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Mastery Timeline:</span>
                        <span className="font-medium">{skill.projected_progression.estimated_mastery_months.toFixed(1)} months</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Confidence:</span>
                        <span className="font-medium">{formatPercentage(skill.projected_progression.confidence)}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Data Points:</span>
                        <span className="font-medium">{skill.total_data_points}</span>
                      </div>
                    </div>

                    {/* Progress bar */}
                    <div className="mt-4">
                      <div className="flex justify-between text-xs mb-1">
                        <span>Current Level</span>
                        <span>{formatPercentage(skill.timeline_data[skill.timeline_data.length - 1]?.level || 0)}</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-blue-600 h-2 rounded-full" 
                          style={{ width: `${(skill.timeline_data[skill.timeline_data.length - 1]?.level || 0) * 100}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Areas of Strength */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Areas of Strength</h2>
              <div className="flex flex-wrap gap-2">
                {dashboard.areas_of_strength.map((strength, index) => (
                  <span key={index} className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                    <Star className="w-3 h-3 mr-1" />
                    {strength}
                  </span>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Code Quality Tab */}
        {activeTab === 'code-quality' && (
          <div className="space-y-8">
            {/* Quality Metrics Overview */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <MetricCard
                title="Complexity Score"
                value={formatScore(dashboard.code_quality.complexity_timeline[dashboard.code_quality.complexity_timeline.length - 1]?.score || 0)}
                icon={Code}
                trend={{ value: dashboard.code_quality.complexity_timeline[dashboard.code_quality.complexity_timeline.length - 1]?.score || 0, direction: dashboard.code_quality.quality_trend === 'improving' ? 'up' : 'neutral' }}
              />
              <MetricCard
                title="Pattern Adoption"
                value={formatScore(dashboard.code_quality.pattern_adoption_timeline[dashboard.code_quality.pattern_adoption_timeline.length - 1]?.score || 0)}
                icon={Target}
                trend={{ value: dashboard.code_quality.pattern_adoption_timeline[dashboard.code_quality.pattern_adoption_timeline.length - 1]?.score || 0, direction: 'up' }}
              />
              <MetricCard
                title="Security Score"
                value={formatScore(dashboard.code_quality.security_score_timeline[dashboard.code_quality.security_score_timeline.length - 1]?.score || 0)}
                icon={AlertCircle}
                trend={{ value: dashboard.code_quality.security_score_timeline[dashboard.code_quality.security_score_timeline.length - 1]?.score || 0, direction: 'up' }}
              />
              <MetricCard
                title="Test Coverage"
                value={formatScore(dashboard.code_quality.test_coverage_timeline[dashboard.code_quality.test_coverage_timeline.length - 1]?.score || 0)}
                icon={CheckCircle2}
                trend={{ value: dashboard.code_quality.test_coverage_timeline[dashboard.code_quality.test_coverage_timeline.length - 1]?.score || 0, direction: 'up' }}
              />
            </div>

            {/* Golden Source Similarity */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Golden Source Alignment</h2>
              <div className="mb-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-600">Current Similarity Score</span>
                  <span className="text-lg font-semibold text-blue-600">
                    {formatPercentage(dashboard.code_quality.golden_source_similarity[dashboard.code_quality.golden_source_similarity.length - 1]?.similarity_score || 0)}
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div 
                    className="bg-blue-600 h-3 rounded-full" 
                    style={{ 
                      width: `${(dashboard.code_quality.golden_source_similarity[dashboard.code_quality.golden_source_similarity.length - 1]?.similarity_score || 0) * 100}%` 
                    }}
                  ></div>
                </div>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div>
                  <h4 className="text-sm font-medium text-gray-900 mb-3">Alignment Trend</h4>
                  <div className="space-y-2">
                    {dashboard.code_quality.golden_source_similarity.slice(-5).map((entry, index) => (
                      <div key={index} className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">
                          {new Date(entry.timestamp).toLocaleDateString()}
                        </span>
                        <div className="flex items-center">
                          <span className="font-medium mr-2">{formatPercentage(entry.similarity_score)}</span>
                          {getTrendIcon(entry.golden_source_alignment)}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <h4 className="text-sm font-medium text-gray-900 mb-3">Quality Metrics</h4>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Improvement Rate:</span>
                      <span className="font-medium">{(dashboard.code_quality.improvement_rate * 100).toFixed(2)}%</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Commits Analyzed:</span>
                      <span className="font-medium">{dashboard.code_quality.total_commits_analyzed}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Overall Trend:</span>
                      <div className="flex items-center">
                        {getTrendIcon(dashboard.code_quality.quality_trend)}
                        <span className="ml-1 font-medium capitalize">{dashboard.code_quality.quality_trend}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Quality Timeline Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Complexity Timeline</h3>
                <CodeQualityChart data={dashboard.code_quality.complexity_timeline} />
              </div>
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Security Score</h3>
                <CodeQualityChart data={dashboard.code_quality.security_score_timeline} />
              </div>
            </div>
          </div>
        )}

        {/* Learning Tab */}
        {activeTab === 'learning' && (
          <div className="space-y-8">
            {/* Learning Velocity Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <MetricCard
                title="Skills Per Month"
                value={dashboard.learning_velocity.skills_per_month.toFixed(1)}
                icon={Zap}
                trend={{ value: dashboard.learning_velocity.skills_per_month, direction: 'up' }}
              />
              <MetricCard
                title="Learning Efficiency"
                value={formatPercentage(dashboard.learning_velocity.learning_efficiency)}
                icon={Brain}
                trend={{ value: dashboard.learning_velocity.learning_efficiency, direction: 'up' }}
              />
              <MetricCard
                title="Consistency Score"
                value={formatPercentage(dashboard.learning_velocity.learning_consistency_score)}
                icon={Target}
                trend={{ value: dashboard.learning_velocity.learning_consistency_score, direction: 'up' }}
              />
              <MetricCard
                title="3-Month Prediction"
                value={dashboard.learning_velocity.predicted_velocity_3months.toFixed(1)}
                icon={TrendingUp}
                trend={{ value: dashboard.learning_velocity.predicted_velocity_3months, direction: 'up' }}
              />
            </div>

            {/* Resource Effectiveness */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Learning Resource Effectiveness</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {Object.entries(dashboard.learning_velocity.resource_effectiveness).map(([resource, effectiveness]) => (
                  <div key={resource} className="text-center p-4 border border-gray-200 rounded-lg">
                    <div className="text-2xl font-bold text-blue-600">{formatPercentage(effectiveness)}</div>
                    <div className="text-sm text-gray-600 capitalize">{resource}</div>
                    <div className="mt-2">
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-blue-600 h-2 rounded-full" 
                          style={{ width: `${effectiveness * 100}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Velocity Factors */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Learning Velocity Factors</h2>
              <div className="space-y-4">
                {Object.entries(dashboard.learning_velocity.velocity_factors).map(([factor, impact]) => (
                  <div key={factor} className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-900 capitalize">
                      {factor.replace('_', ' ')}
                    </span>
                    <div className="flex items-center space-x-3">
                      <div className="w-32 bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-blue-600 h-2 rounded-full" 
                          style={{ width: `${impact * 100}%` }}
                        ></div>
                      </div>
                      <span className="text-sm font-semibold text-gray-900 w-12">
                        {formatPercentage(impact)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Velocity Timeline */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Learning Velocity Timeline</h2>
              <LearningVelocityChart data={dashboard.learning_velocity.velocity_timeline} />
            </div>
          </div>
        )}

        {/* Coaching Tab */}
        {activeTab === 'coaching' && (
          <div className="space-y-8">
            {/* Coaching Impact Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <MetricCard
                title="ROI Score"
                value={`${dashboard.coaching_impact.coaching_roi_score.toFixed(1)}x`}
                icon={Trophy}
                trend={{ value: dashboard.coaching_impact.coaching_roi_score, direction: 'up' }}
              />
              <MetricCard
                title="Acceptance Rate"
                value={formatPercentage(dashboard.coaching_impact.suggestions_acceptance_rate)}
                icon={CheckCircle2}
                trend={{ value: dashboard.coaching_impact.suggestions_acceptance_rate, direction: 'up' }}
              />
              <MetricCard
                title="Total Sessions"
                value={dashboard.coaching_impact.total_sessions.toString()}
                icon={Users}
                trend={{ value: dashboard.coaching_impact.total_sessions, direction: 'up' }}
              />
              <MetricCard
                title="Career Acceleration"
                value={`${dashboard.coaching_impact.career_progression_acceleration.toFixed(1)}x`}
                icon={TrendingUp}
                trend={{ value: dashboard.coaching_impact.career_progression_acceleration, direction: 'up' }}
              />
            </div>

            {/* Before/After Metrics */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Before/After Coaching Impact</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {Object.entries(dashboard.coaching_impact.before_after_metrics).map(([area, metrics]) => (
                  <div key={area} className="text-center p-4 border border-gray-200 rounded-lg">
                    <h4 className="text-sm font-medium text-gray-900 mb-2 capitalize">
                      {area.replace('_', ' ')}
                    </h4>
                    <div className="flex justify-center items-center space-x-4 mb-2">
                      <div>
                        <div className="text-lg font-semibold text-gray-600">{formatPercentage(metrics.before)}</div>
                        <div className="text-xs text-gray-500">Before</div>
                      </div>
                      <ArrowUp className="w-4 h-4 text-green-500" />
                      <div>
                        <div className="text-lg font-semibold text-green-600">{formatPercentage(metrics.after)}</div>
                        <div className="text-xs text-gray-500">After</div>
                      </div>
                    </div>
                    <div className="text-sm font-medium text-blue-600">
                      +{formatPercentage(metrics.improvement)} improvement
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Coaching Themes */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Coaching Focus Areas</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {Object.entries(dashboard.coaching_impact.coaching_themes).map(([theme, count]) => (
                  <div key={theme} className="text-center p-4 border border-gray-200 rounded-lg">
                    <div className="text-2xl font-bold text-blue-600">{count}</div>
                    <div className="text-sm text-gray-600 capitalize">{theme.replace('_', ' ')}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* Long-term Impact */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Long-term Impact Analysis</h2>
              <div className="space-y-4">
                {Object.entries(dashboard.coaching_impact.long_term_impact).map(([metric, value]) => (
                  <div key={metric} className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-900 capitalize">
                      {metric.replace(/_/g, ' ')}
                    </span>
                    <div className="flex items-center space-x-3">
                      <div className="w-32 bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-green-600 h-2 rounded-full" 
                          style={{ width: `${value * 100}%` }}
                        ></div>
                      </div>
                      <span className="text-sm font-semibold text-gray-900 w-12">
                        {formatPercentage(value)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Time to Improvement */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Time to Improvement</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {Object.entries(dashboard.coaching_impact.time_to_improvement).map(([skill, days]) => (
                  <div key={skill} className="text-center p-4 border border-gray-200 rounded-lg">
                    <div className="text-2xl font-bold text-orange-600">{days}</div>
                    <div className="text-sm text-gray-600">days</div>
                    <div className="text-xs text-gray-500 capitalize">{skill.replace('_', ' ')}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* Session Effectiveness */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Session Effectiveness Timeline</h2>
              <CoachingImpactChart data={dashboard.coaching_impact.session_effectiveness_timeline} />
            </div>
          </div>
        )}

        {/* Career Tab */}
        {activeTab === 'career' && (
          <div className="space-y-8">
            {/* Current Career Status */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-6">Career Development Overview</h2>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Current Position</h3>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Stage:</span>
                      <span className="font-medium">{dashboard.career_stage_progression.current_stage}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Time in Stage:</span>
                      <span className="font-medium">{dashboard.career_stage_progression.months_in_current_stage} months</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Progress to Next:</span>
                      <span className="font-medium">{formatPercentage(dashboard.career_stage_progression.progression_to_next)}</span>
                    </div>
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Career Forecast</h3>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Next Stage:</span>
                      <span className="font-medium">{dashboard.career_progression_forecast.next_career_stage}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Timeline:</span>
                      <span className="font-medium">{dashboard.career_progression_forecast.estimated_timeline}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Success Probability:</span>
                      <span className="font-medium">{formatPercentage(dashboard.career_progression_forecast.probability)}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Milestones Progress */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Completed Milestones</h3>
                <div className="space-y-3">
                  {dashboard.career_stage_progression.key_milestones_completed.map((milestone, index) => (
                    <div key={index} className="flex items-center space-x-3">
                      <CheckCircle2 className="w-5 h-5 text-green-500" />
                      <span className="text-sm text-gray-900">{milestone}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Remaining Milestones</h3>
                <div className="space-y-3">
                  {dashboard.career_stage_progression.remaining_milestones.map((milestone, index) => (
                    <div key={index} className="flex items-center space-x-3">
                      <AlertCircle className="w-5 h-5 text-orange-500" />
                      <span className="text-sm text-gray-900">{milestone}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Key Requirements */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Requirements for Next Stage</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {dashboard.career_progression_forecast.key_requirements.map((requirement, index) => (
                  <div key={index} className="flex items-center space-x-3 p-3 border border-gray-200 rounded-lg">
                    <Lightbulb className="w-5 h-5 text-blue-500" />
                    <span className="text-sm text-gray-900">{requirement}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Achievement Timeline */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Career Achievements</h3>
              <div className="space-y-4">
                {dashboard.key_achievements.map((achievement, index) => (
                  <div key={index} className="flex items-start space-x-4 p-4 border-l-4 border-blue-500 bg-blue-50">
                    <Trophy className="w-5 h-5 text-yellow-500 mt-0.5" />
                    <div className="flex-1">
                      <h4 className="text-sm font-medium text-gray-900">{achievement.achievement}</h4>
                      <div className="flex items-center mt-1 space-x-4">
                        <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${getImpactColor(achievement.impact)}`}>
                          {achievement.impact} impact
                        </span>
                        <span className="text-xs text-gray-500">{achievement.category}</span>
                        <span className="text-xs text-gray-500">
                          {new Date(achievement.date).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default DeveloperAnalytics 
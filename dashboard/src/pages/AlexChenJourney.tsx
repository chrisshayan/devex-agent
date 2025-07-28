import { useState, useEffect } from 'react'
import {
  Calendar,
  TrendingUp,
  Award,
  Clock,
  Target,
  ChevronLeft,
  ChevronRight,
  Brain,
  BookOpen,
  Code
} from 'lucide-react'
import SkillRadarChart from '../components/charts/SkillRadarChart'
import ProgressTimeline from '../components/ProgressTimeline'
import LoadingSpinner from '../components/LoadingSpinner'

interface AlexChenData {
  scenario: {
    timeline_duration_months: number
    phases: Array<{
      name: string
      months: string
      focus: string
    }>
    monthly_snapshots: Array<{
      month: number
      skills: Record<string, number>
      achievements: string[]
      code_quality_score: number
      coaching_sessions: number
    }>
    milestones: Array<{
      title: string
      month: number
      description: string
    }>
  }
}

export default function AlexChenJourney() {
  const [data, setData] = useState<AlexChenData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [currentMonth, setCurrentMonth] = useState(6) // Start at month 6

  useEffect(() => {
    const loadJourneyData = async () => {
      try {
        setLoading(true)
        setError(null)

        // Simulate loading Alex Chen's journey data
        await new Promise(resolve => setTimeout(resolve, 800))
        
        // Mock data for Alex Chen's 18-month journey
        const mockData: AlexChenData = {
          scenario: {
            timeline_duration_months: 18,
            phases: [
              { name: "Foundation Building", months: "1-3", focus: "basic_skills" },
              { name: "Accelerated Learning", months: "4-9", focus: "rapid_growth" },
              { name: "Leadership Emergence", months: "10-15", focus: "technical_leadership" },
              { name: "Senior Contributor", months: "16-18", focus: "organizational_impact" }
            ],
            monthly_snapshots: Array.from({ length: 18 }, (_, i) => ({
              month: i + 1,
              skills: {
                'Python': Math.min(0.3 + (i * 0.04), 0.95),
                'React': Math.min(0.2 + (i * 0.042), 0.90),
                'TypeScript': Math.min(0.1 + (i * 0.045), 0.85),
                'System Design': Math.min(0.05 + (i * 0.035), 0.75),
                'Testing': Math.min(0.25 + (i * 0.038), 0.88),
                'DevOps': Math.min(0.1 + (i * 0.03), 0.70),
                'Leadership': Math.min(0.05 + (i * 0.025), 0.65),
                'Communication': Math.min(0.4 + (i * 0.02), 0.85)
              },
              achievements: i % 3 === 0 ? [`Month ${i + 1} milestone achieved`] : [],
              code_quality_score: Math.min(60 + (i * 2.2), 95),
              coaching_sessions: Math.floor(Math.random() * 3) + 1
            })),
            milestones: [
              { title: "First Code Review", month: 2, description: "Completed first independent code review" },
              { title: "React Proficiency", month: 5, description: "Achieved proficiency in React development" },
              { title: "Testing Champion", month: 8, description: "Improved team test coverage by 40%" },
              { title: "Tech Lead Role", month: 12, description: "Promoted to technical lead position" },
              { title: "Architecture Design", month: 15, description: "Led system architecture redesign" },
              { title: "Senior Developer", month: 18, description: "Promoted to senior developer" }
            ]
          }
        }
        
        setData(mockData)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load journey data')
        console.error('Journey loading error:', err)
      } finally {
        setLoading(false)
      }
    }

    loadJourneyData()
  }, [])

  const handlePreviousMonth = () => {
    setCurrentMonth(Math.max(1, currentMonth - 1))
  }

  const handleNextMonth = () => {
    setCurrentMonth(Math.min(data?.scenario.timeline_duration_months || 18, currentMonth + 1))
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
        <h3 className="text-red-800 font-medium">Error Loading Journey</h3>
        <p className="text-red-600 mt-2">{error}</p>
        <button 
          onClick={() => window.location.reload()}
          className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          Retry
        </button>
      </div>
    )
  }

  const currentSnapshot = data?.scenario.monthly_snapshots[currentMonth - 1]
  const phases = data?.scenario.phases || []
  const milestones = data?.scenario.milestones || []

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-green-600 to-blue-700 rounded-lg p-8 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">Alex Chen's Developer Journey</h1>
            <p className="text-green-100 text-lg">
              18-month transformation from Junior to Senior Developer
            </p>
          </div>
          <div className="hidden md:block">
            <Brain className="h-20 w-20 text-green-200" />
          </div>
        </div>
      </div>

      {/* Timeline Navigation */}
      <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Journey Timeline</h3>
          <div className="flex items-center space-x-4">
            <button
              onClick={handlePreviousMonth}
              disabled={currentMonth <= 1}
              className="p-2 rounded-md bg-gray-100 hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ChevronLeft className="h-5 w-5" />
            </button>
            <div className="flex items-center space-x-2">
              <Calendar className="h-5 w-5 text-gray-500" />
              <span className="text-lg font-medium">Month {currentMonth}</span>
            </div>
            <button
              onClick={handleNextMonth}
              disabled={currentMonth >= (data?.scenario.timeline_duration_months || 18)}
              className="p-2 rounded-md bg-gray-100 hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ChevronRight className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* Month Progress Bar */}
        <div className="w-full bg-gray-200 rounded-full h-2 mb-4">
          <div 
            className="bg-blue-500 h-2 rounded-full transition-all duration-300"
            style={{ width: `${(currentMonth / (data?.scenario.timeline_duration_months || 18)) * 100}%` }}
          />
        </div>
        <p className="text-sm text-gray-600">
          Progress: {currentMonth} of {data?.scenario.timeline_duration_months} months
        </p>
      </div>

      {/* Current Month Summary */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Skills Radar Chart */}
        <div className="lg:col-span-2 bg-white rounded-lg border border-gray-200 shadow-sm">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-medium text-gray-900">Skills at Month {currentMonth}</h3>
              <Code className="h-5 w-5 text-gray-400" />
            </div>
          </div>
          <div className="px-6 py-4">
            <SkillRadarChart 
              skills={currentSnapshot?.skills || {}} 
              month={currentMonth}
            />
          </div>
        </div>

        {/* Month Stats */}
        <div className="space-y-6">
          <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-500">Code Quality Score</span>
              <TrendingUp className="h-4 w-4 text-green-500" />
            </div>
            <div className="text-2xl font-bold text-gray-900">
              {currentSnapshot?.code_quality_score || 0}%
            </div>
            <div className="text-sm text-green-600 mt-1">
              +{Math.round((currentSnapshot?.code_quality_score || 60) - 60)} from start
            </div>
          </div>

          <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-500">Coaching Sessions</span>
              <BookOpen className="h-4 w-4 text-blue-500" />
            </div>
            <div className="text-2xl font-bold text-gray-900">
              {currentSnapshot?.coaching_sessions || 0}
            </div>
            <div className="text-sm text-gray-600 mt-1">
              This month
            </div>
          </div>

          <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-500">Achievements</span>
              <Award className="h-4 w-4 text-yellow-500" />
            </div>
            <div className="text-2xl font-bold text-gray-900">
              {currentSnapshot?.achievements?.length || 0}
            </div>
            <div className="text-sm text-gray-600 mt-1">
              New milestones
            </div>
          </div>
        </div>
      </div>

      {/* Progress Timeline */}
      <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-medium text-gray-900">Development Phases</h3>
          <Target className="h-5 w-5 text-gray-400" />
        </div>
        <ProgressTimeline 
          phases={phases}
          currentMonth={currentMonth}
          milestones={milestones}
        />
      </div>

      {/* Journey Insights */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6 border border-blue-200">
        <div className="flex items-center space-x-3 mb-4">
          <Brain className="h-6 w-6 text-blue-600" />
          <h3 className="text-lg font-medium text-gray-900">Journey Insights</h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">1.8x</div>
            <div className="text-sm text-gray-600">Career progression speed</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">60%</div>
            <div className="text-sm text-gray-600">Code quality improvement</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">78%</div>
            <div className="text-sm text-gray-600">Coaching suggestion adoption</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-orange-600">85%</div>
            <div className="text-sm text-gray-600">Test coverage achieved</div>
          </div>
        </div>
      </div>
    </div>
  )
} 
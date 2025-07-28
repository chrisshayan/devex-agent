import { useState, useEffect } from 'react'
import {
  TrendingUp,
  Award,
  Clock,
  BarChart3,
  Activity,
  Target,
  Zap
} from 'lucide-react'
import MetricCard from '../components/MetricCard'
import SkillProgressChart from '../components/charts/SkillProgressChart'
import LearningVelocityChart from '../components/charts/LearningVelocityChart'
import CoachingImpactChart from '../components/charts/CoachingImpactChart'
import LoadingSpinner from '../components/LoadingSpinner'
import { fetchDashboardOverview } from '../services/api'

interface DashboardData {
  totalDevelopers: number
  activeCoachingSessions: number
  avgSkillImprovement: number
  avgCareerAcceleration: number
  recentActivity: Array<{
    id: string
    type: string
    message: string
    timestamp: string
  }>
}

export default function Dashboard() {
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        setLoading(true)
        setError(null)

        // Load dashboard overview data
        const dashboardData = await fetchDashboardOverview()
        setData(dashboardData)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load dashboard data')
        console.error('Dashboard loading error:', err)
      } finally {
        setLoading(false)
      }
    }

    loadDashboardData()
  }, [])

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
        <h3 className="text-red-800 font-medium">Error Loading Dashboard</h3>
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

  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 rounded-lg p-8 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">DevEx Analytics Dashboard</h1>
            <p className="text-blue-100 text-lg">
              Real-time insights into developer growth and AI-powered coaching effectiveness
            </p>
          </div>
          <div className="hidden md:block">
            <Activity className="h-20 w-20 text-blue-200" />
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Active Developers"
          value={data?.totalDevelopers?.toLocaleString() || "0"}
          icon={TrendingUp}
          trend={{ value: 12, direction: 'up' }}
          description="Developers using DevEx coaching"
        />
        <MetricCard
          title="Coaching Sessions"
          value={data?.activeCoachingSessions?.toLocaleString() || "0"}
          icon={Award}
          trend={{ value: 8, direction: 'up' }}
          description="Active coaching sessions this week"
        />
        <MetricCard
          title="Avg Skill Growth"
          value={`${data?.avgSkillImprovement?.toFixed(1) || "0.0"}%`}
          icon={TrendingUp}
          trend={{ value: 15, direction: 'up' }}
          description="Monthly skill improvement rate"
        />
        <MetricCard
          title="Career Acceleration"
          value={`${data?.avgCareerAcceleration?.toFixed(1) || "1.0"}x`}
          icon={Clock}
          trend={{ value: 22, direction: 'up' }}
          description="Faster than traditional progression"
        />
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Skill Progress Overview */}
        <div className="bg-white rounded-lg border border-gray-200 shadow-sm">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-medium text-gray-900">Skill Progress Overview</h3>
              <BarChart3 className="h-5 w-5 text-gray-400" />
            </div>
          </div>
          <div className="px-6 py-4">
            <SkillProgressChart />
          </div>
        </div>

        {/* Learning Velocity Trends */}
        <div className="bg-white rounded-lg border border-gray-200 shadow-sm">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-medium text-gray-900">Learning Velocity Trends</h3>
              <Zap className="h-5 w-5 text-gray-400" />
            </div>
          </div>
          <div className="px-6 py-4">
            <LearningVelocityChart />
          </div>
        </div>
      </div>

      {/* Coaching Impact & Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Coaching Impact */}
        <div className="lg:col-span-2 bg-white rounded-lg border border-gray-200 shadow-sm">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-medium text-gray-900">Coaching Impact Analysis</h3>
              <Target className="h-5 w-5 text-gray-400" />
            </div>
          </div>
          <div className="px-6 py-4">
            <CoachingImpactChart />
          </div>
        </div>

        {/* Recent Activity */}
        <div className="bg-white rounded-lg border border-gray-200 shadow-sm">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">Recent Activity</h3>
          </div>
          <div className="px-6 py-4">
            <div className="space-y-4">
              {data?.recentActivity?.map((activity) => (
                <div key={activity.id} className="flex items-start space-x-3">
                  <div className="flex-shrink-0">
                    <div className="h-2 w-2 bg-blue-500 rounded-full mt-2"></div>
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-gray-900">{activity.message}</p>
                    <p className="text-xs text-gray-500">{activity.timestamp}</p>
                  </div>
                </div>
              )) || (
                <p className="text-gray-500 text-sm">No recent activity</p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-gray-50 rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Developer Analytics</h3>
        <p className="text-gray-600 mb-4">Explore detailed analytics and insights for individual developers</p>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <a 
            href="/alex-chen" 
            className="px-4 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 text-center block transition-colors"
          >
            🎯 Alex Chen Journey
          </a>
          <a 
            href="/developer/alex-chen" 
            className="px-4 py-3 bg-purple-600 text-white rounded-md hover:bg-purple-700 text-center block transition-colors"
          >
            📊 Alex Chen Analytics
          </a>
          <a 
            href="/developer/chrisshayan" 
            className="px-4 py-3 bg-green-600 text-white rounded-md hover:bg-green-700 text-center block transition-colors"
          >
            📈 Chris Shayan Analytics
          </a>
          <button className="px-4 py-3 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors">
            📋 Export Data
          </button>
        </div>
      </div>
    </div>
  )
} 
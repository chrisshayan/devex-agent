import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  Activity,
  TrendingUp,
  Target,
  BookOpen,
  Award,
  Calendar,
  User,
  ArrowLeft,
  Clock,
  Star,
  ChevronRight,
  BarChart3,
  Lightbulb,
  Zap,
  Brain
} from 'lucide-react';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { motion } from 'framer-motion';

interface DeveloperAnalyticsProps {}

interface SkillTimeline {
  timestamp: string;
  level: number;
  velocity: number;
  milestone_events: any[];
}

interface SkillProgression {
  skill_name: string;
  skill_category: string;
  timeline_data: SkillTimeline[];
  trend_analysis: {
    trend: string;
    improvement_rate: number;
    average_level: number;
  };
  projected_progression: {
    projected_level: number;
    estimated_mastery_months: number;
    confidence: number;
  };
}

interface DashboardData {
  developer_id: string;
  generated_at: string;
  skill_progression: SkillProgression[];
  code_quality: any;
  learning_velocity: any;
  coaching_impact: any;
  overall_progress_score: number;
  career_stage_progression: any;
  key_achievements: any[];
  skill_mastery_timeline: Record<string, string>;
  career_progression_forecast: any;
}

interface DemoData {
  scenario_name: string;
  developer_profile: any;
  timeline_duration_months: number;
  monthly_snapshots: any[];
  milestone_completions: any[];
  coaching_sessions: any[];
}

const SKILL_COLORS = {
  python: '#3776ab',
  javascript: '#f7df1e',
  react: '#61dafb',
  testing: '#25c2a0',
  architecture: '#ff6b6b',
  language: '#3776ab',
  framework: '#61dafb',
  technical: '#25c2a0',
  soft_skill: '#ff6b6b'
};

const SFIA_LEVELS = [
  { level: 0.0, name: 'Awareness', description: 'Has basic awareness of concepts' },
  { level: 0.2, name: 'Foundation', description: 'Understands basic principles' },
  { level: 0.4, name: 'Practitioner', description: 'Can apply skills with guidance' },
  { level: 0.6, name: 'Competent', description: 'Works independently' },
  { level: 0.8, name: 'Proficient', description: 'Leads and mentors others' },
  { level: 1.0, name: 'Expert', description: 'Industry expert and thought leader' }
];

const getSFIALevel = (level: number) => {
  return SFIA_LEVELS.find((sfia, index) => {
    const nextLevel = SFIA_LEVELS[index + 1];
    return level >= sfia.level && (!nextLevel || level < nextLevel.level);
  }) || SFIA_LEVELS[0];
};

const DeveloperAnalytics: React.FC<DeveloperAnalyticsProps> = () => {
  const { developerId } = useParams<{ developerId: string }>();
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [demoData, setDemoData] = useState<DemoData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        if (developerId === 'alex-chen') {
          // Fetch Alex Chen demo data
          const demoResponse = await fetch('/api/v1/demo/alex-chen/journey');
          if (!demoResponse.ok) throw new Error('Failed to fetch demo data');
          const demo = await demoResponse.json();
          setDemoData(demo.scenario);
        } else {
          // Fetch real developer analytics
          const dashboardResponse = await fetch(`/api/v1/analytics/developer/${developerId}/dashboard`);
          if (!dashboardResponse.ok) throw new Error('Failed to fetch dashboard data');
          const dashboard = await dashboardResponse.json();
          setDashboardData(dashboard.dashboard);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    if (developerId) {
      fetchData();
    }
  }, [developerId]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="flex items-center space-x-2">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="text-gray-600">Loading analytics...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Error Loading Data</h2>
          <p className="text-gray-600">{error}</p>
          <Link to="/" className="mt-4 inline-flex items-center text-blue-600 hover:text-blue-700">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Dashboard
          </Link>
        </div>
      </div>
    );
  }

  const data = dashboardData || demoData;
  const isDemoData = !!demoData;

  if (!data) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-xl font-semibold text-gray-900 mb-2">No Data Available</h2>
          <p className="text-gray-600">No analytics data found for this developer.</p>
        </div>
      </div>
    );
  }

  const renderSkillProgression = () => {
    const skills = isDemoData 
      ? Object.entries(data.developer_profile?.technical_skills || {}).map(([name, level]) => ({
          skill_name: name,
          skill_category: 'technical',
          current_level: level as number,
          trend_analysis: { trend: 'improving', improvement_rate: 0.05 }
        }))
      : dashboardData?.skill_progression || [];

    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900">Skill Progression</h3>
          <span className="text-sm text-gray-500">SFIA Framework Levels</span>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {skills.slice(0, 6).map((skill, index) => {
            const currentLevel = isDemoData ? skill.current_level : skill.timeline_data?.[skill.timeline_data.length - 1]?.level || 0;
            const sfiaLevel = getSFIALevel(currentLevel);
            const improvement = skill.trend_analysis?.improvement_rate || 0;
            
            return (
              <motion.div
                key={skill.skill_name}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 hover:shadow-md transition-shadow"
              >
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h4 className="font-medium text-gray-900 capitalize">{skill.skill_name.replace('_', ' ')}</h4>
                    <span className="text-sm text-gray-500 capitalize">{skill.skill_category}</span>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-blue-600">{Math.round(currentLevel * 100)}%</div>
                    <div className="text-xs text-gray-500">{sfiaLevel.name}</div>
                  </div>
                </div>
                
                <div className="mb-3">
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-sm font-medium text-gray-700">Proficiency</span>
                    <span className="text-sm text-gray-500">{sfiaLevel.description}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-gradient-to-r from-blue-500 to-blue-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${currentLevel * 100}%` }}
                    ></div>
                  </div>
                </div>
                
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center text-green-600">
                    <TrendingUp className="h-4 w-4 mr-1" />
                    <span>+{Math.round(improvement * 100)}% growth</span>
                  </div>
                  <span className="text-gray-500">
                    {skill.trend_analysis?.trend || 'improving'}
                  </span>
                </div>
              </motion.div>
            );
          })}
        </div>

        {/* Skills Radar Chart */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <h4 className="font-medium text-gray-900 mb-4">Skills Overview</h4>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={skills.slice(0, 6).map(skill => ({
                skill: skill.skill_name.replace('_', ' '),
                level: isDemoData ? skill.current_level * 100 : (skill.timeline_data?.[skill.timeline_data.length - 1]?.level || 0) * 100
              }))}>
                <PolarGrid />
                <PolarAngleAxis dataKey="skill" tick={{ fontSize: 12 }} />
                <PolarRadiusAxis domain={[0, 100]} tick={{ fontSize: 10 }} />
                <Radar
                  name="Skill Level"
                  dataKey="level"
                  stroke="#3B82F6"
                  fill="#3B82F6"
                  fillOpacity={0.3}
                />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    );
  };

  const renderCodeQuality = () => {
    if (isDemoData) {
      return (
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Code Quality Evolution</h3>
          <p className="text-gray-600">Code quality metrics will be available for real developer data.</p>
        </div>
      );
    }

    const codeQuality = dashboardData?.code_quality;
    if (!codeQuality) return null;

    const qualityMetrics = [
      { 
        name: 'Complexity', 
        data: codeQuality.complexity_timeline?.slice(-12) || [],
        color: '#3B82F6',
        icon: BarChart3 
      },
      { 
        name: 'Test Coverage', 
        data: codeQuality.test_coverage_timeline?.slice(-12) || [],
        color: '#10B981',
        icon: Target 
      },
      { 
        name: 'Security', 
        data: codeQuality.security_score_timeline?.slice(-12) || [],
        color: '#F59E0B',
        icon: Award 
      },
      { 
        name: 'Maintainability', 
        data: codeQuality.maintainability_timeline?.slice(-12) || [],
        color: '#8B5CF6',
        icon: Lightbulb 
      }
    ];

    return (
      <div className="space-y-6">
        <h3 className="text-lg font-semibold text-gray-900">Code Quality Trends</h3>
        
        {/* Quality Metrics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {qualityMetrics.map((metric, index) => {
            const latestScore = metric.data[metric.data.length - 1]?.score || 0;
            const previousScore = metric.data[metric.data.length - 2]?.score || 0;
            const change = latestScore - previousScore;
            const Icon = metric.icon;
            
            return (
              <motion.div
                key={metric.name}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: index * 0.1 }}
                className="bg-white p-6 rounded-xl shadow-sm border border-gray-200"
              >
                <div className="flex items-center justify-between mb-2">
                  <Icon className="h-5 w-5" style={{ color: metric.color }} />
                  <span className={`text-sm font-medium ${change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {change >= 0 ? '+' : ''}{Math.round(change * 100)}%
                  </span>
                </div>
                <div className="text-2xl font-bold text-gray-900">{Math.round(latestScore * 100)}%</div>
                <div className="text-sm text-gray-500">{metric.name}</div>
              </motion.div>
            );
          })}
        </div>

        {/* Combined Timeline Chart */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <h4 className="font-medium text-gray-900 mb-4">Quality Evolution Timeline</h4>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={codeQuality.complexity_timeline?.slice(-12).map((item, index) => ({
                date: new Date(item.timestamp).toLocaleDateString(),
                complexity: item.score * 100,
                testCoverage: codeQuality.test_coverage_timeline?.[index]?.score * 100 || 0,
                security: codeQuality.security_score_timeline?.[index]?.score * 100 || 0,
                maintainability: codeQuality.maintainability_timeline?.[index]?.score * 100 || 0
              })) || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'white', 
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                  }}
                />
                <Line type="monotone" dataKey="complexity" stroke="#3B82F6" strokeWidth={2} name="Complexity" />
                <Line type="monotone" dataKey="testCoverage" stroke="#10B981" strokeWidth={2} name="Test Coverage" />
                <Line type="monotone" dataKey="security" stroke="#F59E0B" strokeWidth={2} name="Security" />
                <Line type="monotone" dataKey="maintainability" stroke="#8B5CF6" strokeWidth={2} name="Maintainability" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    );
  };

  const renderLearningVelocity = () => {
    const velocityData = isDemoData ? null : dashboardData?.learning_velocity;
    
    if (!velocityData) {
      return (
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Learning Velocity</h3>
          <p className="text-gray-600">Learning velocity data will be available for real developer analytics.</p>
        </div>
      );
    }

    return (
      <div className="space-y-6">
        <h3 className="text-lg font-semibold text-gray-900">Learning Velocity Analytics</h3>
        
        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <div className="flex items-center justify-between mb-2">
              <Zap className="h-5 w-5 text-blue-600" />
              <span className="text-sm text-green-600 font-medium">Active</span>
            </div>
            <div className="text-2xl font-bold text-gray-900">{velocityData.skills_per_month}</div>
            <div className="text-sm text-gray-500">Skills/Month</div>
          </div>
          
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <div className="flex items-center justify-between mb-2">
              <Brain className="h-5 w-5 text-purple-600" />
              <span className="text-sm text-blue-600 font-medium">High</span>
            </div>
            <div className="text-2xl font-bold text-gray-900">{Math.round(velocityData.learning_consistency_score * 100)}%</div>
            <div className="text-sm text-gray-500">Consistency</div>
          </div>
          
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <div className="flex items-center justify-between mb-2">
              <TrendingUp className="h-5 w-5 text-green-600" />
              <span className="text-sm text-orange-600 font-medium">Moderate</span>
            </div>
            <div className="text-2xl font-bold text-gray-900">{Math.round(velocityData.learning_efficiency * 100)}%</div>
            <div className="text-sm text-gray-500">Efficiency</div>
          </div>
        </div>

        {/* Velocity Timeline */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <h4 className="font-medium text-gray-900 mb-4">Learning Velocity Timeline</h4>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={velocityData.velocity_timeline?.map(item => ({
                date: new Date(item.timestamp).toLocaleDateString(),
                velocity: item.velocity,
                engagement: item.engagement * 100
              })) || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'white', 
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                  }}
                />
                <Area 
                  type="monotone" 
                  dataKey="velocity" 
                  stackId="1"
                  stroke="#3B82F6" 
                  fill="#3B82F6" 
                  fillOpacity={0.6}
                  name="Velocity"
                />
                <Area 
                  type="monotone" 
                  dataKey="engagement" 
                  stackId="2"
                  stroke="#10B981" 
                  fill="#10B981" 
                  fillOpacity={0.3}
                  name="Engagement %"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Resource Effectiveness */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <h4 className="font-medium text-gray-900 mb-4">Learning Resource Effectiveness</h4>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Object.entries(velocityData.resource_effectiveness || {}).map(([resource, effectiveness]) => (
              <div key={resource} className="text-center">
                <div className="text-2xl font-bold text-gray-900">{Math.round((effectiveness as number) * 100)}%</div>
                <div className="text-sm text-gray-500 capitalize">{resource}</div>
                <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                  <div 
                    className="bg-blue-600 h-2 rounded-full"
                    style={{ width: `${(effectiveness as number) * 100}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };

  const renderCoachingImpact = () => {
    const coachingData = isDemoData ? null : dashboardData?.coaching_impact;
    
    if (!coachingData) {
      return (
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Coaching Impact</h3>
          <p className="text-gray-600">Coaching impact data will be available for real developer analytics.</p>
        </div>
      );
    }

    return (
      <div className="space-y-6">
        <h3 className="text-lg font-semibold text-gray-900">DevEx Coaching Impact</h3>
        
        {/* Impact Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <div className="text-2xl font-bold text-gray-900">{coachingData.total_sessions}</div>
            <div className="text-sm text-gray-500">Total Sessions</div>
          </div>
          
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <div className="text-2xl font-bold text-green-600">{Math.round(coachingData.suggestions_acceptance_rate * 100)}%</div>
            <div className="text-sm text-gray-500">Acceptance Rate</div>
          </div>
          
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <div className="text-2xl font-bold text-blue-600">{Math.round(coachingData.skill_improvement_correlation * 100)}%</div>
            <div className="text-sm text-gray-500">Skill Correlation</div>
          </div>
          
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <div className="text-2xl font-bold text-purple-600">{coachingData.coaching_roi_score.toFixed(1)}x</div>
            <div className="text-sm text-gray-500">ROI Score</div>
          </div>
        </div>

        {/* Session Effectiveness Timeline */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <h4 className="font-medium text-gray-900 mb-4">Session Effectiveness Over Time</h4>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={coachingData.session_effectiveness_timeline?.map(session => ({
                date: new Date(session.timestamp).toLocaleDateString(),
                effectiveness: session.effectiveness_score,
                satisfaction: session.satisfaction
              })) || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'white', 
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                  }}
                />
                <Line 
                  type="monotone" 
                  dataKey="effectiveness" 
                  stroke="#3B82F6" 
                  strokeWidth={2}
                  name="Effectiveness Score"
                />
                <Line 
                  type="monotone" 
                  dataKey="satisfaction" 
                  stroke="#10B981" 
                  strokeWidth={2}
                  name="Satisfaction (1-5)"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Coaching Themes */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <h4 className="font-medium text-gray-900 mb-4">Focus Areas</h4>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Object.entries(coachingData.coaching_themes || {}).map(([theme, count]) => (
              <div key={theme} className="text-center">
                <div className="text-2xl font-bold text-gray-900">{count as number}</div>
                <div className="text-sm text-gray-500 capitalize">{theme.replace('_', ' ')}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Before/After Improvements */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <h4 className="font-medium text-gray-900 mb-4">Skill Improvements</h4>
          <div className="space-y-4">
            {Object.entries(coachingData.before_after_metrics || {}).map(([skill, metrics]: [string, any]) => (
              <div key={skill} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div className="flex-1">
                  <div className="font-medium text-gray-900 capitalize">{skill.replace('_', ' ')}</div>
                  <div className="text-sm text-gray-500">
                    {Math.round(metrics.before * 100)}% → {Math.round(metrics.after * 100)}%
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-lg font-bold text-green-600">+{Math.round(metrics.improvement * 100)}%</div>
                  <div className="text-xs text-gray-500">improvement</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };

  const renderOverview = () => {
    const profile = isDemoData ? data.developer_profile : null;
    const careerProgression = dashboardData?.career_stage_progression;
    const achievements = dashboardData?.key_achievements || [];

    return (
      <div className="space-y-6">
        {/* Developer Profile Header */}
        <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white p-6 rounded-xl">
          <div className="flex items-center space-x-4">
            <div className="h-16 w-16 bg-white/20 rounded-full flex items-center justify-center">
              <User className="h-8 w-8" />
            </div>
            <div>
              <h2 className="text-2xl font-bold">
                {isDemoData ? 'Alex Chen (Demo)' : `Developer ${developerId}`}
              </h2>
              <p className="text-blue-100">
                {profile?.career_stage || careerProgression?.current_stage || 'Developer'} • 
                {profile?.experience_years || '3+'} years experience
              </p>
              <div className="flex items-center mt-2 space-x-4">
                <div className="flex items-center">
                  <Star className="h-4 w-4 mr-1" />
                  <span className="text-sm">
                    Overall Progress: {Math.round((dashboardData?.overall_progress_score || 0.8) * 100)}%
                  </span>
                </div>
                {profile?.primary_languages && (
                  <div className="flex items-center">
                    <span className="text-sm">
                      Primary: {profile.primary_languages.join(', ')}
                    </span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-medium text-gray-900">Skills Mastered</h3>
              <Target className="h-5 w-5 text-blue-600" />
            </div>
            <div className="text-2xl font-bold text-gray-900">
              {Object.values(dashboardData?.skill_mastery_timeline || {}).filter(timeline => 
                timeline.includes('month')
              ).length}
            </div>
            <p className="text-sm text-gray-500">Near mastery level</p>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-medium text-gray-900">Career Progress</h3>
              <TrendingUp className="h-5 w-5 text-green-600" />
            </div>
            <div className="text-2xl font-bold text-gray-900">
              {Math.round((careerProgression?.progression_to_next || 0.65) * 100)}%
            </div>
            <p className="text-sm text-gray-500">To {careerProgression?.next_stage || 'next level'}</p>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-medium text-gray-900">Achievements</h3>
              <Award className="h-5 w-5 text-yellow-600" />
            </div>
            <div className="text-2xl font-bold text-gray-900">{achievements.length}</div>
            <p className="text-sm text-gray-500">Milestones reached</p>
          </div>
        </div>

        {/* Recent Achievements */}
        {achievements.length > 0 && (
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <h3 className="font-medium text-gray-900 mb-4">Recent Achievements</h3>
            <div className="space-y-3">
              {achievements.slice(0, 3).map((achievement, index) => (
                <motion.div
                  key={achievement.achievement}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg"
                >
                  <div className="h-8 w-8 bg-yellow-100 rounded-full flex items-center justify-center">
                    <Award className="h-4 w-4 text-yellow-600" />
                  </div>
                  <div className="flex-1">
                    <div className="font-medium text-gray-900">{achievement.achievement}</div>
                    <div className="text-sm text-gray-500">
                      {new Date(achievement.date).toLocaleDateString()} • {achievement.category}
                    </div>
                  </div>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    achievement.impact === 'high' ? 'bg-green-100 text-green-800' :
                    achievement.impact === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {achievement.impact} impact
                  </span>
                </motion.div>
              ))}
            </div>
          </div>
        )}

        {/* Career Progression Forecast */}
        {dashboardData?.career_progression_forecast && (
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <h3 className="font-medium text-gray-900 mb-4">Career Progression Forecast</h3>
            <div className="flex items-center justify-between p-4 bg-blue-50 rounded-lg">
              <div>
                <div className="font-medium text-gray-900">
                  Next Stage: {dashboardData.career_progression_forecast.next_career_stage}
                </div>
                <div className="text-sm text-gray-600">
                  Timeline: {dashboardData.career_progression_forecast.estimated_timeline}
                </div>
                <div className="text-sm text-gray-600 mt-1">
                  Probability: {Math.round(dashboardData.career_progression_forecast.probability * 100)}%
                </div>
              </div>
              <div className="text-3xl font-bold text-blue-600">
                {Math.round(dashboardData.career_progression_forecast.probability * 100)}%
              </div>
            </div>
            <div className="mt-4">
              <div className="text-sm font-medium text-gray-700 mb-2">Key Requirements:</div>
              <div className="flex flex-wrap gap-2">
                {dashboardData.career_progression_forecast.key_requirements?.map((req: string) => (
                  <span key={req} className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm">
                    {req}
                  </span>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    );
  };

  const tabs = [
    { id: 'overview', name: 'Overview', icon: User },
    { id: 'skills', name: 'Skills', icon: Target },
    { id: 'quality', name: 'Code Quality', icon: BarChart3 },
    { id: 'velocity', name: 'Learning', icon: Zap },
    { id: 'coaching', name: 'Coaching', icon: Brain }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between py-4">
            <div className="flex items-center space-x-4">
              <Link to="/" className="text-gray-600 hover:text-gray-900">
                <ArrowLeft className="h-5 w-5" />
              </Link>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Developer Analytics</h1>
                <p className="text-gray-600">
                  {isDemoData ? 'Alex Chen - 18-Month Journey Demo' : `Analytics for ${developerId}`}
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-2 text-sm text-gray-500">
              <Clock className="h-4 w-4" />
              <span>Updated {isDemoData ? 'Demo Data' : 'Recently'}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700'
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  <span>{tab.name}</span>
                </button>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'overview' && renderOverview()}
        {activeTab === 'skills' && renderSkillProgression()}
        {activeTab === 'quality' && renderCodeQuality()}
        {activeTab === 'velocity' && renderLearningVelocity()}
        {activeTab === 'coaching' && renderCoachingImpact()}
      </div>
    </div>
  );
};

export default DeveloperAnalytics; 
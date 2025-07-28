import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  User,
  TrendingUp,
  Target,
  BookOpen,
  Award,
  Calendar,
  Activity,
  Clock,
  Star,
  ChevronRight,
  BarChart3,
  Lightbulb,
  Zap,
  Brain,
  Play
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
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { motion } from 'framer-motion';

interface DashboardProps {}

interface DemoHighlights {
  career_progression: {
    title: string;
    metric: string;
    details: string;
    impact_score: number;
  };
  code_quality: {
    title: string;
    metric: string;
    details: any;
    impact_score: number;
  };
  coaching_effectiveness: {
    title: string;
    metric: string;
    details: string;
    impact_score: number;
  };
  learning_velocity: {
    title: string;
    metric: string;
    details: any;
    impact_score: number;
  };
}

const Dashboard: React.FC<DashboardProps> = () => {
  const [demoHighlights, setDemoHighlights] = useState<DemoHighlights | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDemoHighlights = async () => {
      try {
        const response = await fetch('/api/v1/demo/alex-chen/highlights');
        if (response.ok) {
          const data = await response.json();
          setDemoHighlights(data.demo_highlights);
        }
      } catch (error) {
        console.error('Failed to fetch demo highlights:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchDemoHighlights();
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">DevEx Analytics Dashboard</h1>
              <p className="text-gray-600 mt-1">
                AI-powered developer experience insights and career coaching
              </p>
            </div>
            <div className="flex items-center space-x-2 text-sm text-gray-500">
              <Clock className="h-4 w-4" />
              <span>Last updated: Just now</span>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-8 rounded-2xl mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold mb-2">Welcome to DevEx Analytics</h2>
              <p className="text-blue-100 mb-4">
                Explore developer journey analytics powered by AI coaching and SFIA framework
              </p>
              <div className="flex items-center space-x-6">
                <div className="flex items-center">
                  <Brain className="h-5 w-5 mr-2" />
                  <span className="text-sm">AI-Powered Coaching</span>
                </div>
                <div className="flex items-center">
                  <Target className="h-5 w-5 mr-2" />
                  <span className="text-sm">SFIA-Based Skills</span>
                </div>
                <div className="flex items-center">
                  <TrendingUp className="h-5 w-5 mr-2" />
                  <span className="text-sm">Career Progression</span>
                </div>
              </div>
            </div>
            <div className="text-right">
              <div className="text-4xl font-bold">18</div>
              <div className="text-sm text-blue-100">Month Demo Journey</div>
            </div>
          </div>
        </div>

        {/* Demo Showcase Section */}
        <div className="mb-12">
          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">🎬 Alex Chen Demo Journey</h2>
            <p className="text-gray-600">
              Experience an 18-month developer transformation story from Junior to Senior
            </p>
          </div>

          {/* Demo Highlights */}
          {!loading && demoHighlights && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              {Object.entries(demoHighlights).map(([key, highlight], index) => {
                const typedHighlight = highlight as DemoHighlights[keyof DemoHighlights];
                return (
                  <motion.div
                    key={key}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 hover:shadow-md transition-shadow"
                  >
                    <div className="flex items-center justify-between mb-3">
                      <div className="p-2 bg-blue-100 rounded-lg">
                        {key === 'career_progression' && <TrendingUp className="h-5 w-5 text-blue-600" />}
                        {key === 'code_quality' && <BarChart3 className="h-5 w-5 text-green-600" />}
                        {key === 'coaching_effectiveness' && <Brain className="h-5 w-5 text-purple-600" />}
                        {key === 'learning_velocity' && <Zap className="h-5 w-5 text-orange-600" />}
                      </div>
                      <div className="text-right">
                        <div className="text-xs text-gray-500">Impact Score</div>
                        <div className="text-lg font-bold text-gray-900">{typedHighlight.impact_score}</div>
                      </div>
                    </div>
                    <h3 className="font-semibold text-gray-900 mb-1">{typedHighlight.title}</h3>
                    <div className="text-2xl font-bold text-blue-600 mb-2">{typedHighlight.metric}</div>
                    <p className="text-sm text-gray-600">
                      {typeof typedHighlight.details === 'string' ? typedHighlight.details : typedHighlight.details?.complexity || 'Comprehensive improvement'}
                    </p>
                  </motion.div>
                );
              })}
            </div>
          )}

          {/* Demo CTA */}
          <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="h-16 w-16 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center">
                  <User className="h-8 w-8 text-white" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-gray-900">Alex Chen - Demo Developer</h3>
                  <p className="text-gray-600">Junior → Senior Developer in 18 months</p>
                  <div className="flex items-center mt-2 space-x-4">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      Demo Journey
                    </span>
                    <span className="text-sm text-gray-500">52 coaching sessions</span>
                    <span className="text-sm text-gray-500">9 milestones achieved</span>
                  </div>
                </div>
              </div>
              <Link
                to="/analytics/alex-chen"
                className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-medium rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all duration-200 shadow-lg hover:shadow-xl"
              >
                <Play className="h-5 w-5 mr-2" />
                Explore Demo Journey
                <ChevronRight className="h-4 w-4 ml-2" />
              </Link>
            </div>
          </div>
        </div>

        {/* Real Developer Analytics Section */}
        <div className="mb-12">
          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">👨‍💻 Real Developer Analytics</h2>
            <p className="text-gray-600">
              Explore actual developer progress, coaching impact, and skill development
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Chris Shayan - Real Developer */}
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 hover:shadow-md transition-shadow">
              <div className="flex items-center space-x-4 mb-4">
                <div className="h-12 w-12 bg-gray-100 rounded-full flex items-center justify-center">
                  <User className="h-6 w-6 text-gray-600" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">Chris Shayan</h3>
                  <p className="text-gray-600">Mid-Level Developer</p>
                </div>
              </div>
              
              <div className="space-y-3 mb-6">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Progress Score</span>
                  <span className="font-medium text-gray-900">85%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-blue-600 h-2 rounded-full" style={{ width: '85%' }}></div>
                </div>
                
                <div className="grid grid-cols-2 gap-4 mt-4">
                  <div className="text-center">
                    <div className="text-lg font-bold text-gray-900">12</div>
                    <div className="text-xs text-gray-500">Coaching Sessions</div>
                  </div>
                  <div className="text-center">
                    <div className="text-lg font-bold text-gray-900">2.2</div>
                    <div className="text-xs text-gray-500">Skills/Month</div>
                  </div>
                </div>
              </div>
              
              <Link
                to="/analytics/chrisshayan"
                className="w-full inline-flex items-center justify-center px-4 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
              >
                View Analytics
                <ChevronRight className="h-4 w-4 ml-2" />
              </Link>
            </div>

            {/* Add Your Developer */}
            <div className="bg-gray-50 p-6 rounded-xl border-2 border-dashed border-gray-300 hover:border-blue-400 transition-colors">
              <div className="text-center">
                <div className="h-12 w-12 bg-gray-200 rounded-full flex items-center justify-center mx-auto mb-4">
                  <User className="h-6 w-6 text-gray-400" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Your Developer Profile</h3>
                <p className="text-gray-600 mb-6">
                  Connect your development environment to get personalized analytics and AI coaching
                </p>
                
                <div className="space-y-2 mb-6">
                  <div className="flex items-center justify-center text-sm text-gray-500">
                    <Target className="h-4 w-4 mr-2" />
                    <span>Skill progression tracking</span>
                  </div>
                  <div className="flex items-center justify-center text-sm text-gray-500">
                    <Brain className="h-4 w-4 mr-2" />
                    <span>AI-powered coaching</span>
                  </div>
                  <div className="flex items-center justify-center text-sm text-gray-500">
                    <TrendingUp className="h-4 w-4 mr-2" />
                    <span>Career progression insights</span>
                  </div>
                </div>
                
                <button className="w-full inline-flex items-center justify-center px-4 py-2 bg-gray-600 text-white font-medium rounded-lg hover:bg-gray-700 transition-colors">
                  <span>Connect Developer</span>
                  <ChevronRight className="h-4 w-4 ml-2" />
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Feature Highlights */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <div className="flex items-center mb-4">
              <div className="p-2 bg-blue-100 rounded-lg mr-3">
                <Brain className="h-6 w-6 text-blue-600" />
              </div>
              <h3 className="font-semibold text-gray-900">AI Coaching</h3>
            </div>
            <p className="text-gray-600 text-sm mb-4">
              Personalized guidance powered by CodeBERT and career progression models
            </p>
            <ul className="text-sm text-gray-500 space-y-1">
              <li>• Real-time code analysis</li>
              <li>• Skill-based recommendations</li>
              <li>• Career milestone tracking</li>
            </ul>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <div className="flex items-center mb-4">
              <div className="p-2 bg-green-100 rounded-lg mr-3">
                <Target className="h-6 w-6 text-green-600" />
              </div>
              <h3 className="font-semibold text-gray-900">SFIA Skills Framework</h3>
            </div>
            <p className="text-gray-600 text-sm mb-4">
              Industry-standard competency levels from Awareness to Expert
            </p>
            <ul className="text-sm text-gray-500 space-y-1">
              <li>• Structured skill assessment</li>
              <li>• Clear progression paths</li>
              <li>• Industry benchmarking</li>
            </ul>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <div className="flex items-center mb-4">
              <div className="p-2 bg-purple-100 rounded-lg mr-3">
                <BarChart3 className="h-6 w-6 text-purple-600" />
              </div>
              <h3 className="font-semibold text-gray-900">Advanced Analytics</h3>
            </div>
            <p className="text-gray-600 text-sm mb-4">
              Comprehensive insights into code quality, learning velocity, and career growth
            </p>
            <ul className="text-sm text-gray-500 space-y-1">
              <li>• Code quality trends</li>
              <li>• Learning velocity metrics</li>
              <li>• Coaching effectiveness</li>
            </ul>
          </div>
        </div>

        {/* API Endpoints Reference */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <h3 className="font-semibold text-gray-900 mb-4">Available Analytics APIs</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <h4 className="font-medium text-gray-700 mb-2">Alex Chen Demo APIs:</h4>
              <ul className="space-y-1 text-gray-600 font-mono">
                <li>GET /api/v1/demo/alex-chen/journey</li>
                <li>GET /api/v1/demo/alex-chen/highlights</li>
                <li>GET /api/v1/demo/alex-chen/dashboard/{`{month}`}</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium text-gray-700 mb-2">Developer Analytics APIs:</h4>
              <ul className="space-y-1 text-gray-600 font-mono">
                <li>GET /api/v1/analytics/developer/{`{id}`}/dashboard</li>
                <li>GET /api/v1/analytics/developer/{`{id}`}/skills/timeline</li>
                <li>GET /api/v1/analytics/developer/{`{id}`}/coaching/impact</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 
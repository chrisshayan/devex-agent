// API service functions for the DevEx Analytics Dashboard

const API_BASE_URL = 'http://localhost:8000';

interface DashboardOverviewData {
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

interface DeveloperAnalyticsData {
  dashboard: {
    overall_progress_score: number
    skill_progression: Array<{
      skill_name: string
      current_level: number
      trend: string
    }>
    code_quality: {
      quality_trend: string
      improvement_rate: number
    }
    learning_velocity: {
      skills_per_month: number
      learning_efficiency: number
    }
    coaching_impact: {
      suggestions_acceptance_rate: number
      coaching_roi_score: number
    }
    key_achievements: Array<{
      title: string
      date: string
      description: string
    }>
    areas_of_strength: string[]
    improvement_opportunities: string[]
  }
}

// Helper function for API requests
async function apiRequest(endpoint: string) {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`API request failed for ${endpoint}:`, error);
    throw error;
  }
}

// Alex Chen Demo API calls
export async function fetchAlexChenJourney() {
  return await apiRequest('/api/v1/demo/alex-chen/journey');
}

export async function fetchAlexChenDashboard(month: number) {
  return await apiRequest(`/api/v1/demo/alex-chen/dashboard/${month}`);
}

export async function fetchAlexChenHighlights() {
  return await apiRequest('/api/v1/demo/alex-chen/highlights');
}

// Developer Analytics API calls
export async function fetchDeveloperDashboard(developerId: string) {
  return await apiRequest(`/api/v1/analytics/developer/${developerId}/dashboard`);
}

export async function fetchDeveloperSkillsTimeline(developerId: string) {
  return await apiRequest(`/api/v1/analytics/developer/${developerId}/skills/timeline`);
}

export async function fetchDeveloperCodeQualityTrends(developerId: string) {
  return await apiRequest(`/api/v1/analytics/developer/${developerId}/code-quality/trends`);
}

export async function fetchDeveloperLearningVelocity(developerId: string) {
  return await apiRequest(`/api/v1/analytics/developer/${developerId}/learning/velocity`);
}

export async function fetchDeveloperCoachingImpact(developerId: string) {
  return await apiRequest(`/api/v1/analytics/developer/${developerId}/coaching/impact`);
}

// Legacy API functions (kept for backward compatibility)
export async function fetchDashboardOverview(): Promise<DashboardOverviewData> {
  try {
    // Try to get real data from highlights API
    const highlights = await fetchAlexChenHighlights();
    
    return {
      totalDevelopers: highlights.total_developers || 42,
      activeCoachingSessions: highlights.active_coaching_sessions || 18,
      avgSkillImprovement: highlights.avg_skill_growth || 23.5,
      avgCareerAcceleration: highlights.career_acceleration || 1.8,
      recentActivity: highlights.recent_activity || [
        {
          id: '1',
          type: 'skill_improvement',
          message: 'Alex Chen improved Python skills by 15%',
          timestamp: '2 hours ago'
        },
        {
          id: '2',
          type: 'milestone',
          message: 'Sarah completed React fundamentals milestone',
          timestamp: '5 hours ago'
        },
        {
          id: '3',
          type: 'coaching',
          message: 'Michael had a coaching session on system design',
          timestamp: '1 day ago'
        }
      ]
    };
  } catch (error) {
    console.error('Failed to fetch dashboard overview, falling back to mock data:', error);
    // Fallback to mock data if API fails
    return {
      totalDevelopers: 42,
      activeCoachingSessions: 18,
      avgSkillImprovement: 23.5,
      avgCareerAcceleration: 1.8,
      recentActivity: [
        {
          id: '1',
          type: 'skill_improvement',
          message: 'Alex Chen improved Python skills by 15%',
          timestamp: '2 hours ago'
        },
        {
          id: '2',
          type: 'milestone',
          message: 'Sarah completed React fundamentals milestone',
          timestamp: '5 hours ago'
        },
        {
          id: '3',
          type: 'coaching',
          message: 'Michael had a coaching session on system design',
          timestamp: '1 day ago'
        }
      ]
    };
  }
}

export async function fetchDeveloperAnalytics(
  developerId: string, 
  timePeriod: number
): Promise<DeveloperAnalyticsData> {
  try {
    // Use real API endpoint
    const dashboard = await fetchDeveloperDashboard(developerId);
    return { dashboard };
  } catch (error) {
    console.error(`Failed to fetch developer analytics for ${developerId}, falling back to mock data:`, error);
    // Fallback to mock data if API fails
    return {
      dashboard: {
        overall_progress_score: 0.78,
        skill_progression: [
          { skill_name: 'Python', current_level: 85, trend: 'improving' },
          { skill_name: 'React', current_level: 75, trend: 'improving' },
          { skill_name: 'TypeScript', current_level: 68, trend: 'stable' },
          { skill_name: 'System Design', current_level: 60, trend: 'improving' }
        ],
        code_quality: {
          quality_trend: 'improving',
          improvement_rate: 0.25
        },
        learning_velocity: {
          skills_per_month: 2.4,
          learning_efficiency: 0.82
        },
        coaching_impact: {
          suggestions_acceptance_rate: 0.78,
          coaching_roi_score: 2.1
        },
        key_achievements: [
          {
            title: 'Completed Advanced React Patterns',
            date: '2024-01-15',
            description: 'Successfully mastered complex state management patterns'
          },
          {
            title: 'Led Code Review Sessions',
            date: '2024-01-10',
            description: 'Started mentoring junior developers in code review best practices'
          },
          {
            title: 'Performance Optimization Expert',
            date: '2024-01-05',
            description: 'Optimized application performance by 40%'
          }
        ],
        areas_of_strength: [
          'Frontend Development',
          'Code Quality & Testing',
          'Team Collaboration',
          'Problem Solving'
        ],
        improvement_opportunities: [
          'System Architecture',
          'DevOps & Deployment',
          'Security Best Practices',
          'Technical Leadership'
        ]
      }
    };
  }
}

export async function fetchSkillProgressionTimeline(
  developerId: string, 
  timePeriod: number
): Promise<any> {
  try {
    return await fetchDeveloperSkillsTimeline(developerId);
  } catch (error) {
    console.error(`Failed to fetch skill timeline for ${developerId}:`, error);
    return { error: 'Failed to load skill timeline data' };
  }
}

export async function fetchCodeQualityTrends(
  developerId: string, 
  timePeriod: number
): Promise<any> {
  try {
    return await fetchDeveloperCodeQualityTrends(developerId);
  } catch (error) {
    console.error(`Failed to fetch code quality trends for ${developerId}:`, error);
    return { error: 'Failed to load code quality data' };
  }
}

export async function fetchLearningVelocityAnalytics(
  developerId: string, 
  timePeriod: number
): Promise<any> {
  try {
    return await fetchDeveloperLearningVelocity(developerId);
  } catch (error) {
    console.error(`Failed to fetch learning velocity for ${developerId}:`, error);
    return { error: 'Failed to load learning velocity data' };
  }
}

export async function fetchCoachingImpactAnalysis(
  developerId: string, 
  timePeriod: number
): Promise<any> {
  try {
    return await fetchDeveloperCoachingImpact(developerId);
  } catch (error) {
    console.error(`Failed to fetch coaching impact for ${developerId}:`, error);
    return { error: 'Failed to load coaching impact data' };
  }
} 
// API service for DevEx Agent dashboard

const API_BASE_URL = 'http://localhost:8000';

async function apiRequest(endpoint: string, options: RequestInit = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    throw new Error(`API request failed: ${response.statusText}`);
  }

  return await response.json();
}

// Dashboard Overview
export async function fetchDashboardOverview() {
  // For now, return mock data - replace with real endpoint when available
  return {
    totalDevelopers: 247,
    activeCoachingSessions: 34,
    avgSkillImprovement: 23.5,
    avgCareerAcceleration: 1.8,
    recentActivity: [
      {
        id: '1',
        type: 'skill_improvement',
        message: 'React skills improved by 15% this week',
        timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
      },
      {
        id: '2', 
        type: 'coaching_session',
        message: 'Completed advanced TypeScript coaching session',
        timestamp: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(),
      },
      {
        id: '3',
        type: 'pattern_detection',
        message: 'New design pattern detected in recent commits',
        timestamp: new Date(Date.now() - 8 * 60 * 60 * 1000).toISOString(),
      },
    ],
  };
}

// Developer-specific data
export async function fetchDeveloperAnalytics(developerId: string) {
  return await apiRequest(`/api/v1/developers/${developerId}/analytics`);
}

// Morning Brief
export async function fetchMorningBrief(developerId: string) {
  return await apiRequest(`/brief/morning/${developerId}`);
}

// Knowledge Graph APIs
export async function fetchKnowledgeGraphInsights(developerId: string) {
  return await apiRequest(`/api/v1/knowledge-graph/insights/${developerId}`);
}

export async function fetchGoldenSourceAlignment(developerId: string) {
  return await apiRequest(`/api/v1/knowledge-graph/golden-sources/${developerId}`);
}

export async function fetchPatternMatches(developerId: string) {
  return await apiRequest(`/api/v1/knowledge-graph/patterns/${developerId}`);
}

// CodeBERT APIs
export async function fetchCodeBertAnalysis(developerId: string) {
  return await apiRequest(`/api/v1/codebert/analysis/${developerId}`);
}

export async function fetchCodeBertPatterns(developerId: string) {
  return await apiRequest(`/api/v1/codebert/patterns/${developerId}`);
}

export async function fetchCodeBertSimilarity(developerId: string) {
  return await apiRequest(`/api/v1/codebert/similarity/${developerId}`);
}

export async function fetchCodeBertPredictions(developerId: string) {
  return await apiRequest(`/api/v1/codebert/predictions/${developerId}`);
}

// NEW: Pattern History & Analytics APIs
export async function fetchPatternHistory(developerId: string, timeframe: string = '3months') {
  return await apiRequest(`/api/v1/analytics/pattern-history/${developerId}?timeframe=${timeframe}`);
}

export async function fetchSkillProgression(developerId: string, timeframe: string = '3months') {
  return await apiRequest(`/api/v1/analytics/skill-progression/${developerId}?timeframe=${timeframe}`);
}

export async function fetchCoachingMetrics(developerId: string) {
  return await apiRequest(`/api/v1/analytics/coaching-metrics/${developerId}`);
}

export async function fetchGoldenSourcesList(developerId: string) {
  return await apiRequest(`/api/v1/analytics/golden-sources-list/${developerId}`);
}

// Additional functions needed by DeveloperAnalytics component
export async function fetchDeveloperDashboard(developerId: string) {
  // This can use the analytics dashboard endpoint
  return await apiRequest(`/api/v1/analytics/pattern-history/${developerId}`);
}

export async function fetchDeveloperSkillsTimeline(developerId: string, timeframe: string = '6months') {
  return await apiRequest(`/api/v1/analytics/skill-progression/${developerId}?timeframe=${timeframe}`);
}

export async function fetchDeveloperCodeQualityTrends(developerId: string, timeframe: string = '6months') {
  // Use CodeBERT analysis for code quality trends
  return await apiRequest(`/api/v1/codebert/analysis/${developerId}`);
}

export async function fetchDeveloperLearningVelocity(developerId: string, timeframe: string = '6months') {
  // Use coaching metrics for learning velocity data
  return await apiRequest(`/api/v1/analytics/coaching-metrics/${developerId}`);
}

export async function fetchDeveloperCoachingImpact(developerId: string, timeframe: string = '6months') {
  return await apiRequest(`/api/v1/analytics/coaching-metrics/${developerId}`);
} 
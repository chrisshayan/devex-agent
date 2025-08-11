// API service for DevEx Agent dashboard

const API_BASE_URL = 'http://localhost:8000';

// Simple in-memory cache for GET requests
const __cache = new Map<string, { timestamp: number; data: any }>();

async function cachedGet(endpoint: string, ttlMs = 15000) {
  const url = `${API_BASE_URL}${endpoint}`;
  const now = Date.now();
  const key = `GET ${url}`;
  const cached = __cache.get(key);
  if (cached && now - cached.timestamp < ttlMs) {
    return cached.data;
  }
  const response = await apiRequest(endpoint);
  __cache.set(key, { timestamp: now, data: response });
  return response;
}

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
  return await cachedGet(`/brief/morning/${developerId}`, 30000);
}

// Knowledge Graph APIs
export async function fetchKnowledgeGraphInsights(developerId: string) {
  return await cachedGet(`/api/v1/knowledge-graph/insights/${developerId}`, 30000);
}

export async function fetchGoldenSourceAlignment(developerId: string) {
  return await cachedGet(`/api/v1/knowledge-graph/golden-sources/${developerId}`, 60000);
}

export async function fetchPatternMatches(developerId: string) {
  return await cachedGet(`/api/v1/knowledge-graph/patterns/${developerId}`, 60000);
}

// CodeBERT APIs
export async function fetchCodeBertAnalysis(developerId: string) {
  return await cachedGet(`/api/v1/codebert/analysis/${developerId}`, 30000);
}

export async function fetchCodeBertPatterns(developerId: string) {
  return await cachedGet(`/api/v1/codebert/patterns/${developerId}`, 30000);
}

export async function fetchCodeBertSimilarity(developerId: string) {
  return await cachedGet(`/api/v1/codebert/similarity/${developerId}`, 30000);
}

export async function fetchCodeBertPredictions(developerId: string) {
  return await cachedGet(`/api/v1/codebert/predictions/${developerId}`, 30000);
}

// NEW: Pattern History & Analytics APIs
export async function fetchPatternHistory(developerId: string, timeframe: string = '3months') {
  return await cachedGet(`/api/v1/analytics/pattern-history/${developerId}?timeframe=${timeframe}`, 60000);
}

export async function fetchSkillProgression(developerId: string, timeframe: string = '3months') {
  return await cachedGet(`/api/v1/analytics/skill-progression/${developerId}?timeframe=${timeframe}`, 60000);
}

export async function fetchCoachingMetrics(developerId: string) {
  return await cachedGet(`/api/v1/analytics/coaching-metrics/${developerId}`, 60000);
}

export async function fetchGoldenSourcesList(developerId: string) {
  return await cachedGet(`/api/v1/analytics/golden-sources-list/${developerId}`, 60000);
}

// Golden Source management APIs
export async function registerGoldenSource(payload: any) {
  return await apiRequest(`/api/v1/knowledge-graph/sources`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function updateGoldenSource(sourceId: string, updates: any) {
  return await apiRequest(`/api/v1/knowledge-graph/sources/${sourceId}`, {
    method: 'PUT',
    body: JSON.stringify(updates),
  });
}

export async function ingestGoldenSource(sourceId: string, force: boolean = true) {
  const query = force ? `?force=${encodeURIComponent(String(force))}` : ''
  return await apiRequest(`/api/v1/knowledge-graph/sources/${sourceId}/ingest${query}`, {
    method: 'POST',
  });
}

export async function getGoldenSourceHealth(sourceId: string) {
  return await apiRequest(`/api/v1/knowledge-graph/sources/${sourceId}/health`);
}

// Additional functions needed by DeveloperAnalytics component
export async function fetchDeveloperDashboard(developerId: string) {
  // This can use the analytics dashboard endpoint
  return await apiRequest(`/api/v1/analytics/pattern-history/${developerId}`);
}

export async function fetchDeveloperSkillsTimeline(developerId: string, timeframe: string = '6months') {
  return await cachedGet(`/api/v1/analytics/skill-progression/${developerId}?timeframe=${timeframe}`, 60000);
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
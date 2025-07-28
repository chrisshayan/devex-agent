# DevEx Analytics Dashboard

A modern React-based analytics dashboard for the DevEx Ambient Agent, showcasing developer progress tracking, AI-powered coaching insights, and the compelling Alex Chen journey demonstration.

## 🌟 Features

### 📊 **Core Analytics**
- **Real-time Developer Metrics**: Active developers, coaching sessions, skill growth rates
- **Interactive Visualizations**: Charts powered by Chart.js and Recharts
- **Responsive Design**: Mobile-friendly with Tailwind CSS
- **Performance Optimized**: Built with Vite for fast development and builds

### 🎭 **Alex Chen Journey Demo**
- **18-Month Interactive Timeline**: Watch Alex's transformation from Junior to Senior Developer
- **Auto-play Functionality**: Animated progression through career phases
- **Phase-based Navigation**: Foundation → Acceleration → Leadership → Senior Contributor
- **Skills Radar Chart**: Real-time visualization of skill development
- **Milestone Tracking**: Key achievements and coaching impact

### 📈 **Developer Analytics**
- **Skill Progression Timelines**: Detailed skill evolution tracking
- **Code Quality Trends**: Quality metrics over time
- **Learning Velocity Analytics**: Learning efficiency and consistency
- **Coaching Impact Analysis**: ROI and effectiveness measurement

### 👥 **Team Benchmarks**
- **Comparative Analytics**: Peer benchmarking and team metrics
- **Skill Distribution**: Team-wide skill analysis
- **Performance Insights**: Top performers and learning opportunities

## 🛠️ Technology Stack

- **Frontend**: React 18 + TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **Charts**: Chart.js + react-chartjs-2, Recharts
- **Icons**: Lucide React
- **Routing**: React Router DOM
- **HTTP Client**: Axios
- **Real-time**: WebSocket integration
- **Notifications**: React Hot Toast
- **Animations**: Framer Motion

## 🚀 Quick Start

### Prerequisites
- Node.js >= 18.0.0
- DevEx Ambient Agent backend running on localhost:8000

### Installation

```bash
# Navigate to dashboard directory
cd dashboard

# Install dependencies
npm install

# Start development server
npm run dev
```

The dashboard will be available at `http://localhost:3000`

### Build for Production

```bash
# Build optimized production bundle
npm run build

# Preview production build
npm run preview
```

## 📁 Project Structure

```
dashboard/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── charts/         # Chart components
│   │   ├── Layout.tsx      # Main layout with navigation
│   │   ├── MetricCard.tsx  # Metric display cards
│   │   └── LoadingSpinner.tsx
│   ├── pages/              # Page components
│   │   ├── Dashboard.tsx   # Main overview dashboard
│   │   ├── AlexChenJourney.tsx  # Alex Chen demo
│   │   ├── DeveloperAnalytics.tsx
│   │   └── TeamBenchmarks.tsx
│   ├── services/           # API and data services
│   │   └── api.ts         # Backend API integration
│   ├── App.tsx            # Main application component
│   ├── main.tsx           # Application entry point
│   └── index.css          # Global styles
├── package.json
├── vite.config.ts
├── tailwind.config.js
└── tsconfig.json
```

## 🔗 API Integration

The dashboard connects to the DevEx Ambient Agent backend via proxy:

- **Backend URL**: `http://localhost:8000`
- **API Endpoints**: `/api/v1/*`
- **Demo Endpoints**: `/api/v1/demo/alex-chen/*`
- **Analytics Endpoints**: `/api/v1/analytics/*`

### Key API Endpoints

```typescript
// Alex Chen Demo
GET /api/v1/demo/alex-chen/journey
GET /api/v1/demo/alex-chen/dashboard/{month}
GET /api/v1/demo/alex-chen/highlights

// Developer Analytics
GET /api/v1/analytics/developer/{id}/dashboard
GET /api/v1/analytics/developer/{id}/skills/timeline
GET /api/v1/analytics/developer/{id}/code-quality/trends
GET /api/v1/analytics/developer/{id}/learning/velocity
GET /api/v1/analytics/developer/{id}/coaching/impact

// Team Analytics
GET /api/v1/analytics/team/benchmarks
```

## 🎨 Design System

### Color Palette
- **Primary**: Blue (#3b82f6) - Main actions and highlights
- **Success**: Green (#22c55e) - Positive metrics and achievements
- **Warning**: Orange (#f59e0b) - Attention-needed areas
- **Danger**: Red (#ef4444) - Critical issues

### Components
- **Cards**: Clean white cards with subtle shadows
- **Metrics**: Large value displays with trend indicators
- **Charts**: Interactive visualizations with consistent styling
- **Navigation**: Clean sidebar with active state indicators

## 📊 Chart Types

### Skill Progression
- **Radar Chart**: Multi-dimensional skill visualization
- **Line Chart**: Skill evolution over time
- **Bar Chart**: Skill comparisons and benchmarks

### Learning Analytics
- **Velocity Chart**: Learning speed trends
- **Impact Chart**: Coaching effectiveness
- **Quality Chart**: Code quality improvements

### Timeline
- **Interactive Timeline**: Phase-based progression
- **Milestone Markers**: Achievement tracking
- **Progress Indicators**: Visual completion status

## 🔄 Real-time Features

- **WebSocket Integration**: Live data updates
- **Auto-refresh**: Periodic data synchronization
- **Status Indicators**: Connection and sync status
- **Progressive Loading**: Graceful data loading states

## 🎯 Demo Highlights

### Alex Chen Journey
- **Career Acceleration**: 1.8x faster than average progression
- **Coaching Success**: 78% suggestion acceptance rate
- **Quality Improvement**: 60% overall code quality enhancement
- **Test Coverage**: Improved from 20% to 85%

### Interactive Features
- **Play/Pause**: Auto-play through 18-month journey
- **Month Navigation**: Jump to any specific month
- **Phase Indicators**: Visual phase progression
- **Skill Animation**: Animated skill radar chart

## 🚧 Development

### Available Scripts

```bash
npm run dev        # Start development server
npm run build      # Build for production
npm run preview    # Preview production build
npm run lint       # Run ESLint
npm run type-check # Run TypeScript compiler
```

### Development Guidelines
- Use TypeScript for type safety
- Follow React best practices and hooks patterns
- Implement responsive design with Tailwind CSS
- Optimize performance with React.memo and useMemo
- Handle loading and error states gracefully

## 🔧 Configuration

### Environment Variables
```bash
VITE_API_BASE_URL=http://localhost:8000  # Backend API URL
VITE_WS_URL=ws://localhost:8000/ws       # WebSocket URL
```

### Proxy Configuration
Vite automatically proxies `/api` requests to the backend server.

## 📱 Responsive Design

The dashboard is fully responsive with breakpoints:
- **Mobile**: `< 768px` - Stacked layout, collapsible sidebar
- **Tablet**: `768px - 1024px` - Adapted grid layouts
- **Desktop**: `> 1024px` - Full grid layouts with sidebar

## 🎉 Getting Started with Demo

1. **Start Backend**: Ensure DevEx Ambient Agent is running
2. **Install Dashboard**: `npm install` in dashboard directory
3. **Start Dashboard**: `npm run dev`
4. **Visit Alex Chen Journey**: Navigate to `/alex-chen`
5. **Play Demo**: Click "Play Journey" to see 18-month progression

The dashboard showcases the power of AI-driven developer coaching through compelling visualizations and real data from our analytics APIs.

## 📄 License

This project is part of the DevEx Ambient Agent system. 
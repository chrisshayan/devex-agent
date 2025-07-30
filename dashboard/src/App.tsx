import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import AlexChenJourney from './pages/AlexChenJourney'
import DeveloperAnalytics from './pages/DeveloperAnalytics'
import GoldenSourcesManagement from './pages/GoldenSourcesManagement'
import PatternHistory from './pages/PatternHistory'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/alex-chen" element={<AlexChenJourney />} />
        <Route path="/developer/:developerId" element={<DeveloperAnalytics />} />
        <Route path="/golden-sources/:developerId" element={<GoldenSourcesManagement />} />
        <Route path="/patterns/:developerId" element={<PatternHistory />} />
        <Route path="/codebert/:developerId" element={<PatternHistory />} />
        <Route path="/codebert/:developerId/history" element={<PatternHistory />} />
      </Routes>
    </Layout>
  )
}

export default App 
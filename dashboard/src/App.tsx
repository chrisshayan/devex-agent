import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import AlexChenJourney from './pages/AlexChenJourney'
import DeveloperAnalytics from './pages/DeveloperAnalytics'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/alex-chen" element={<AlexChenJourney />} />
        <Route path="/developer/:developerId" element={<DeveloperAnalytics />} />
      </Routes>
    </Layout>
  )
}

export default App 
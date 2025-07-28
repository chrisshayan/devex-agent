import { useEffect, useState } from 'react'
import { Bar } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
)

interface CodeQualityChartProps {
  developerId?: string
  timePeriod?: number
}

export default function CodeQualityChart({ developerId, timePeriod }: CodeQualityChartProps) {
  const [chartData, setChartData] = useState<any>(null)

  useEffect(() => {
    const mockData = {
      labels: ['Complexity', 'Maintainability', 'Security', 'Test Coverage', 'Documentation'],
      datasets: [
        {
          label: 'Current Score',
          data: [75, 82, 88, 65, 70],
          backgroundColor: 'rgba(59, 130, 246, 0.8)',
          borderColor: 'rgb(59, 130, 246)',
          borderWidth: 1,
        },
        {
          label: 'Target Score',
          data: [85, 90, 95, 80, 85],
          backgroundColor: 'rgba(16, 185, 129, 0.8)',
          borderColor: 'rgb(16, 185, 129)',
          borderWidth: 1,
        },
      ],
    }

    setChartData(mockData)
  }, [developerId, timePeriod])

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 100,
      },
    },
  }

  if (!chartData) {
    return (
      <div className="chart-container flex items-center justify-center">
        <div className="loading-spinner" />
      </div>
    )
  }

  return (
    <div className="chart-container">
      <Bar data={chartData} options={options} />
    </div>
  )
} 
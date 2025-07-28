import { useEffect, useState } from 'react'
import { Line } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
)

interface LearningVelocityChartProps {
  developerId?: string
  timePeriod?: number
}

export default function LearningVelocityChart({ developerId, timePeriod }: LearningVelocityChartProps) {
  const [chartData, setChartData] = useState<any>(null)

  useEffect(() => {
    const mockData = {
      labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6'],
      datasets: [
        {
          label: 'Learning Velocity',
          data: [2.1, 2.8, 3.2, 2.9, 3.5, 4.1],
          borderColor: 'rgb(139, 92, 246)',
          backgroundColor: 'rgba(139, 92, 246, 0.1)',
          tension: 0.4,
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
        title: {
          display: true,
          text: 'Skills Improved/Month',
        },
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
      <Line data={chartData} options={options} />
    </div>
  )
} 
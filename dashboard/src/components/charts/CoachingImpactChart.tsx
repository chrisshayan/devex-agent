import { useEffect, useState } from 'react'
import { Doughnut } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend
} from 'chart.js'

ChartJS.register(ArcElement, Tooltip, Legend)

interface CoachingImpactChartProps {
  developerId?: string
  timePeriod?: number
}

export default function CoachingImpactChart({ developerId, timePeriod }: CoachingImpactChartProps) {
  const [chartData, setChartData] = useState<any>(null)

  useEffect(() => {
    const mockData = {
      labels: ['Suggestions Accepted', 'Suggestions Rejected', 'Pending Review'],
      datasets: [
        {
          data: [78, 15, 7],
          backgroundColor: [
            'rgba(34, 197, 94, 0.8)',
            'rgba(239, 68, 68, 0.8)',
            'rgba(245, 158, 11, 0.8)',
          ],
          borderColor: [
            'rgb(34, 197, 94)',
            'rgb(239, 68, 68)',
            'rgb(245, 158, 11)',
          ],
          borderWidth: 2,
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
        position: 'bottom' as const,
      },
      tooltip: {
        callbacks: {
          label: function(context: any) {
            return `${context.label}: ${context.parsed}%`
          }
        }
      }
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
      <Doughnut data={chartData} options={options} />
    </div>
  )
} 
import { useEffect, useState } from 'react'
import { Radar } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
} from 'chart.js'

ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
)

interface SkillRadarChartProps {
  skills: Record<string, number>
  month: number
}

export default function SkillRadarChart({ skills, month }: SkillRadarChartProps) {
  const [chartData, setChartData] = useState<any>(null)

  useEffect(() => {
    if (!skills || Object.keys(skills).length === 0) {
      // Use mock data if no skills provided
      const mockSkills = {
        'Python': 85,
        'React': 75,
        'TypeScript': 68,
        'System Design': 60,
        'Testing': 72,
        'DevOps': 55,
        'Leadership': 40,
        'Communication': 70
      }
      
      const data = {
        labels: Object.keys(mockSkills),
        datasets: [
          {
            label: `Skills - Month ${month}`,
            data: Object.values(mockSkills),
            fill: true,
            backgroundColor: 'rgba(59, 130, 246, 0.2)',
            borderColor: 'rgb(59, 130, 246)',
            pointBackgroundColor: 'rgb(59, 130, 246)',
            pointBorderColor: '#fff',
            pointHoverBackgroundColor: '#fff',
            pointHoverBorderColor: 'rgb(59, 130, 246)',
          },
        ],
      }
      
      setChartData(data)
    } else {
      const data = {
        labels: Object.keys(skills),
        datasets: [
          {
            label: `Skills - Month ${month}`,
            data: Object.values(skills).map(val => val * 100), // Convert 0-1 to 0-100
            fill: true,
            backgroundColor: 'rgba(59, 130, 246, 0.2)',
            borderColor: 'rgb(59, 130, 246)',
            pointBackgroundColor: 'rgb(59, 130, 246)',
            pointBorderColor: '#fff',
            pointHoverBackgroundColor: '#fff',
            pointHoverBorderColor: 'rgb(59, 130, 246)',
          },
        ],
      }
      
      setChartData(data)
    }
  }, [skills, month])

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
    },
    scales: {
      r: {
        angleLines: {
          display: true,
        },
        suggestedMin: 0,
        suggestedMax: 100,
        ticks: {
          stepSize: 20,
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
      <Radar data={chartData} options={options} />
    </div>
  )
} 
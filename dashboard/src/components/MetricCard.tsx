import { LucideIcon, TrendingUp, TrendingDown, Minus } from 'lucide-react'

interface Trend {
  value: number
  direction: 'up' | 'down' | 'neutral'
}

interface MetricCardProps {
  title: string
  value: string
  icon: LucideIcon
  trend?: Trend
  description?: string
  className?: string
}

export default function MetricCard({ 
  title, 
  value, 
  icon: Icon, 
  trend, 
  description,
  className = '' 
}: MetricCardProps) {
  const getTrendColor = (direction: string) => {
    switch (direction) {
      case 'up':
        return 'text-green-600'
      case 'down':
        return 'text-red-600'
      default:
        return 'text-gray-500'
    }
  }

  const getTrendIcon = (direction: string) => {
    switch (direction) {
      case 'up':
        return TrendingUp
      case 'down':
        return TrendingDown
      default:
        return Minus
    }
  }

  const TrendIcon = trend ? getTrendIcon(trend.direction) : null

  return (
    <div className={`bg-white rounded-lg border border-gray-200 shadow-sm p-6 transition-all duration-200 hover:shadow-md ${className}`}>
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-500">{title}</h3>
            <Icon className="h-5 w-5 text-gray-400" />
          </div>
          
          <div className="text-2xl font-bold text-gray-900">{value}</div>
          
          {trend && (
            <div className={`text-sm font-medium mt-2 flex items-center ${getTrendColor(trend.direction)}`}>
              {TrendIcon && <TrendIcon className="h-4 w-4 mr-1" />}
              <span>
                {trend.direction === 'neutral' ? '±' : trend.direction === 'up' ? '+' : ''}
                {Math.abs(trend.value).toFixed(1)}%
              </span>
            </div>
          )}
          
          {description && (
            <p className="text-sm font-medium text-gray-500 mt-1">{description}</p>
          )}
        </div>
      </div>
    </div>
  )
} 
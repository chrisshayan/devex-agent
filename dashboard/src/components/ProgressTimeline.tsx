interface Phase {
  name: string
  months: string
  focus: string
}

interface Milestone {
  title: string
  month: number
  description: string
}

interface ProgressTimelineProps {
  phases: Phase[]
  currentMonth: number
  milestones: Milestone[]
}

export default function ProgressTimeline({ phases, currentMonth, milestones }: ProgressTimelineProps) {
  const getPhaseProgress = (phaseMonths: string, currentMonth: number) => {
    const [start, end] = phaseMonths.split('-').map(m => parseInt(m))
    if (currentMonth < start) return 0
    if (currentMonth > end) return 100
    return ((currentMonth - start + 1) / (end - start + 1)) * 100
  }

  const isPhaseActive = (phaseMonths: string, currentMonth: number) => {
    const [start, end] = phaseMonths.split('-').map(m => parseInt(m))
    return currentMonth >= start && currentMonth <= end
  }

  const isPhaseCompleted = (phaseMonths: string, currentMonth: number) => {
    const [start, end] = phaseMonths.split('-').map(m => parseInt(m))
    return currentMonth > end
  }

  return (
    <div className="space-y-8">
      {/* Timeline Header */}
      <div className="text-center">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">18-Month Journey Timeline</h3>
        <p className="text-sm text-gray-600">Track progress through each phase of development</p>
      </div>

      {/* Phase Timeline */}
      <div className="relative">
        {/* Timeline Line */}
        <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-gray-200"></div>

        {/* Phases */}
        <div className="space-y-8">
          {phases.map((phase, index) => {
            const progress = getPhaseProgress(phase.months, currentMonth)
            const isActive = isPhaseActive(phase.months, currentMonth)
            const isCompleted = isPhaseCompleted(phase.months, currentMonth)

            return (
              <div key={index} className="relative flex items-start">
                {/* Phase Indicator */}
                <div className={`relative z-10 flex items-center justify-center w-16 h-16 rounded-full border-4 ${
                  isCompleted 
                    ? 'bg-success-500 border-success-500' 
                    : isActive 
                    ? 'bg-primary-500 border-primary-500' 
                    : 'bg-white border-gray-300'
                }`}>
                  <span className={`text-sm font-bold ${
                    isCompleted || isActive ? 'text-white' : 'text-gray-500'
                  }`}>
                    {index + 1}
                  </span>
                </div>

                {/* Phase Content */}
                <div className="ml-6 flex-1">
                  <div className={`p-6 rounded-lg border-2 transition-all duration-200 ${
                    isActive 
                      ? 'border-primary-500 bg-primary-50' 
                      : isCompleted 
                      ? 'border-success-500 bg-success-50' 
                      : 'border-gray-200 bg-white'
                  }`}>
                    <div className="flex items-center justify-between mb-3">
                      <h4 className="text-lg font-semibold text-gray-900">{phase.name}</h4>
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                        isCompleted 
                          ? 'bg-success-100 text-success-800' 
                          : isActive 
                          ? 'bg-primary-100 text-primary-800' 
                          : 'bg-gray-100 text-gray-600'
                      }`}>
                        Months {phase.months}
                      </span>
                    </div>

                    <p className="text-sm text-gray-600 mb-4">
                      Focus: <span className="font-medium">{phase.focus.replace('_', ' ')}</span>
                    </p>

                    {/* Progress Bar */}
                    <div className="w-full bg-gray-200 rounded-full h-2 mb-3">
                      <div 
                        className={`h-2 rounded-full transition-all duration-300 ${
                          isCompleted 
                            ? 'bg-success-500' 
                            : isActive 
                            ? 'bg-primary-500' 
                            : 'bg-gray-300'
                        }`}
                        style={{ width: `${progress}%` }}
                      />
                    </div>

                    <div className="flex items-center justify-between text-xs text-gray-500">
                      <span>{progress.toFixed(0)}% Complete</span>
                      {isActive && (
                        <span className="font-medium text-primary-600">Currently Active</span>
                      )}
                      {isCompleted && (
                        <span className="font-medium text-success-600">✓ Completed</span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Milestones Section */}
      {milestones && milestones.length > 0 && (
        <div className="mt-12">
          <h4 className="text-lg font-semibold text-gray-900 mb-6">Key Milestones</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {milestones.slice(0, 6).map((milestone, index) => (
              <div 
                key={index} 
                className={`p-4 rounded-lg border-2 transition-all duration-200 ${
                  milestone.month <= currentMonth
                    ? 'border-success-500 bg-success-50'
                    : 'border-gray-200 bg-white'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className={`text-xs font-medium px-2 py-1 rounded-full ${
                    milestone.month <= currentMonth
                      ? 'bg-success-100 text-success-800'
                      : 'bg-gray-100 text-gray-600'
                  }`}>
                    Month {milestone.month}
                  </span>
                  {milestone.month <= currentMonth && (
                    <span className="text-success-500">✓</span>
                  )}
                </div>
                <h5 className="font-medium text-gray-900 mb-1">{milestone.title}</h5>
                <p className="text-xs text-gray-600">{milestone.description}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
} 
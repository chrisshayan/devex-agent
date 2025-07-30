import { useState, useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import {
  BarChart3,
  TrendingUp,
  User,
  Users,
  Settings,
  Brain,
  Activity,
  X,
  Menu
} from 'lucide-react'

interface LayoutProps {
  children: React.ReactNode
}

interface NavigationItem {
  name: string
  href: string
  icon: any
}

// Dynamic navigation based on current user and available developers
const getNavigationItems = (currentUser: string): NavigationItem[] => {
  return [
    { name: 'Overview', href: '/dashboard', icon: BarChart3 },
    { name: 'Alex Chen Journey', href: '/alex-chen', icon: TrendingUp },
    { name: 'Alex Chen Analytics', href: '/developer/alex-chen', icon: User },
    { name: `${currentUser} Analytics`, href: `/developer/${currentUser.toLowerCase().replace(' ', '')}`, icon: Users },
    { name: 'Morning Brief', href: `/brief/${currentUser.toLowerCase().replace(' ', '')}`, icon: Brain },
  ]
}

// Get current user - in production this would come from authentication
const getCurrentUser = (): string => {
  // Try to get from localStorage first (set by user preference)
  const savedUser = localStorage.getItem('currentDeveloper')
  if (savedUser) return savedUser
  
  // For demo purposes, return a sensible default
  // In real implementation, this would come from:
  // - Authentication context
  // - JWT token
  // - API call to get current user
  return 'Chris Shayan'
}

export default function Layout({ children }: LayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [currentUser, setCurrentUser] = useState<string>('')
  const [navigationItems, setNavigationItems] = useState<NavigationItem[]>([])
  const location = useLocation()

  useEffect(() => {
    const user = getCurrentUser()
    setCurrentUser(user)
    setNavigationItems(getNavigationItems(user))
  }, [])

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Mobile sidebar */}
      {sidebarOpen && (
        <div className="fixed inset-0 z-40 lg:hidden">
          <div className="fixed inset-0 bg-gray-600 bg-opacity-75" onClick={() => setSidebarOpen(false)} />
          <div className="fixed inset-y-0 left-0 flex w-64 flex-col bg-white">
            <div className="flex items-center justify-between px-4 py-6 border-b border-gray-200">
              <div className="flex items-center">
                <Activity className="h-8 w-8 text-primary-600" />
                <span className="ml-2 text-xl font-bold text-gray-900">DevEx Analytics</span>
              </div>
              <button
                onClick={() => setSidebarOpen(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="h-6 w-6" />
              </button>
            </div>
            <nav className="flex-1 px-4 py-6 space-y-1">
              {navigationItems.map((item) => (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`nav-link ${location.pathname === item.href ? 'active' : ''}`}
                  onClick={() => setSidebarOpen(false)}
                >
                  <item.icon className="mr-3 h-5 w-5" />
                  {item.name}
                </Link>
              ))}
            </nav>
          </div>
        </div>
      )}

      {/* Desktop sidebar */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-64 lg:flex-col">
        <div className="flex flex-col flex-grow bg-white border-r border-gray-200">
          <div className="flex items-center px-4 py-6 border-b border-gray-200">
            <Activity className="h-8 w-8 text-primary-600" />
            <span className="ml-2 text-xl font-bold text-gray-900">DevEx Analytics</span>
          </div>
          <nav className="flex-1 px-4 py-6 space-y-1">
            {navigationItems.map((item) => (
              <Link
                key={item.name}
                to={item.href}
                className={`nav-link ${location.pathname === item.href ? 'active' : ''}`}
              >
                <item.icon className="mr-3 h-5 w-5" />
                {item.name}
              </Link>
            ))}
          </nav>
          
          {/* User info section */}
          <div className="px-4 py-4 border-t border-gray-200">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                  <span className="text-sm font-medium text-blue-600">
                    {currentUser.split(' ').map(n => n[0]).join('')}
                  </span>
                </div>
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-700">{currentUser}</p>
                <p className="text-xs text-gray-500">Developer</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="lg:pl-64 flex flex-col flex-1">
        {/* Top navigation */}
        <div className="sticky top-0 z-10 bg-white border-b border-gray-200 px-4 py-4 lg:px-8">
          <div className="flex items-center justify-between">
            <button
              onClick={() => setSidebarOpen(true)}
              className="text-gray-500 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-indigo-500 lg:hidden"
            >
              <Menu className="h-6 w-6" />
            </button>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-500">
                Welcome back, {currentUser}
              </span>
            </div>
          </div>
        </div>

        {/* Page content */}
        <main className="flex-1 p-4 lg:p-8">
          {children}
        </main>
      </div>
    </div>
  )
} 
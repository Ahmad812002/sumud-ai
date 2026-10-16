import { Link, useLocation } from 'react-router-dom'
import { LayoutDashboard, Briefcase, FileText, MessageSquare, Settings } from 'lucide-react'

const navItems = [
  { path: '/',             label: 'Dashboard',     icon: LayoutDashboard },
  { path: '/scorer',       label: 'Job Scorer',    icon: Briefcase },
  { path: '/chat',         label: 'Chat',          icon: MessageSquare },
  { path: '/settings',     label: 'Settings',      icon: Settings },
]

export default function Sidebar() {
  const location = useLocation()

  return (
    <div className="w-64 h-full bg-gray-900 border-r border-gray-800 flex flex-col p-4">
      
      {/* Logo */}
      <div className="mb-8 px-2">
        <h1 className="text-xl font-bold text-white">Sumud AI</h1>
        <p className="text-xs text-[#A0A0A0]">Your career, your resilience.</p>
      </div>

      {/* Navigation */}
      <nav className="flex flex-col gap-1">
        {navItems.map((item) => {
          const Icon = item.icon
          const isActive = location.pathname === item.path

          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors
                ${isActive 
                  ? 'bg-palestine-red text-white' 
                  : 'text-[#A0A0A0] hover:bg-palestine-red hover:text-white'
                }`}
            >
              <Icon size={18} />
              {item.label}
            </Link>
          )
        })}
      </nav>
    </div>
  )
}
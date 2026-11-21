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
    <aside className="sidebar">
      <Link className="brand" to="/">
        <div className="brand-copy">
          <span className="brand-name">SUMUD AI</span>
          <span className="brand-tag">Career / 001</span>
        </div>
      </Link>
      <p className="nav-label">Workspace</p>
      <nav className="nav-stack">
        {navItems.map((item) => {
          const Icon = item.icon
          const isActive = location.pathname === item.path
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`nav-link ${isActive ? 'active' : ''}`}
              title={item.label}
            >
              <Icon size={18} />
              <span>{item.label}</span>
            </Link>
          )
        })}
      </nav>
    </aside>
  )
}
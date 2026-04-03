import { useRouter } from 'next/router'
import Link from 'next/link'
import { useAuth } from '../lib/auth'
import {
  LayoutDashboard, FileText, Search, MessageSquare,
  BarChart3, Shield, LogOut, Brain, Menu, X
} from 'lucide-react'
import { useState } from 'react'

const navItems = [
  { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/documents', label: 'Documents', icon: FileText },
  { href: '/search', label: 'Search', icon: Search },
  { href: '/ask', label: 'Ask AI', icon: MessageSquare },
  { href: '/stats', label: 'Analytics', icon: BarChart3 },
]

const adminItems = [
  { href: '/admin', label: 'Admin Panel', icon: Shield },
]

export default function Layout({ children }) {
  const router = useRouter()
  const { user, logout } = useAuth()
  const [open, setOpen] = useState(false)

  const isActive = (href) => router.pathname === href

  const NavLink = ({ href, label, icon: Icon }) => (
    <Link href={href}
      className={`flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition-colors
        ${isActive(href)
          ? 'bg-indigo-600 text-white'
          : 'text-gray-400 hover:bg-gray-800 hover:text-gray-100'}`}
      onClick={() => setOpen(false)}
    >
      <Icon size={18} />
      {label}
    </Link>
  )

  return (
    <div className="flex h-screen bg-gray-950 overflow-hidden">
      {/* Mobile overlay */}
      {open && (
        <div className="fixed inset-0 bg-black/60 z-20 lg:hidden" onClick={() => setOpen(false)} />
      )}

      {/* Sidebar */}
      <aside className={`fixed lg:static inset-y-0 left-0 z-30 w-64 bg-gray-900 border-r border-gray-800
        flex flex-col transition-transform duration-200
        ${open ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}`}>

        {/* Logo */}
        <div className="flex items-center gap-3 px-6 py-5 border-b border-gray-800">
          <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center">
            <Brain size={18} className="text-white" />
          </div>
          <div>
            <p className="font-bold text-white text-sm">DevHive</p>
            <p className="text-xs text-gray-500">Knowledge Platform</p>
          </div>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
          {navItems.map((item) => <NavLink key={item.href} {...item} />)}
          {user?.role === 'admin' && (
            <>
              <div className="pt-4 pb-2 px-4">
                <p className="text-xs font-semibold text-gray-600 uppercase tracking-wider">Admin</p>
              </div>
              {adminItems.map((item) => <NavLink key={item.href} {...item} />)}
            </>
          )}
        </nav>

        {/* User footer */}
        <div className="px-3 py-4 border-t border-gray-800">
          <div className="flex items-center gap-3 px-3 py-2 mb-2">
            <div className="w-8 h-8 bg-indigo-700 rounded-full flex items-center justify-center text-xs font-bold text-white">
              {user?.full_name?.[0]?.toUpperCase() || user?.email?.[0]?.toUpperCase() || 'U'}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-200 truncate">{user?.full_name || 'User'}</p>
              <p className="text-xs text-gray-500 truncate">{user?.role}</p>
            </div>
          </div>
          <button onClick={logout}
            className="flex items-center gap-3 px-4 py-2 rounded-lg text-sm text-gray-400 hover:bg-gray-800 hover:text-red-400 w-full transition-colors">
            <LogOut size={16} />
            Logout
          </button>
        </div>
      </aside>

      {/* Main */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Mobile topbar */}
        <div className="lg:hidden flex items-center gap-3 px-4 py-3 bg-gray-900 border-b border-gray-800">
          <button onClick={() => setOpen(true)} className="text-gray-400 hover:text-white">
            <Menu size={22} />
          </button>
          <div className="flex items-center gap-2">
            <Brain size={18} className="text-indigo-500" />
            <span className="font-bold text-white text-sm">DevHive</span>
          </div>
        </div>

        <main className="flex-1 overflow-y-auto p-6">
          {children}
        </main>
      </div>
    </div>
  )
}

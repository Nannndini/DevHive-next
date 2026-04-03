import { useEffect, useState } from 'react'
import Layout from '../components/Layout'
import withAuth from '../components/withAuth'
import { useAuth } from '../lib/auth'
import api from '../lib/api'
import { FileText, Search, MessageSquare, Database, Upload, ArrowRight } from 'lucide-react'
import Link from 'next/link'

function StatCard({ icon: Icon, label, value, color }) {
  return (
    <div className="card flex items-center gap-4">
      <div className={`w-12 h-12 ${color} rounded-xl flex items-center justify-center shrink-0`}>
        <Icon size={22} className="text-white" />
      </div>
      <div>
        <p className="text-2xl font-bold text-white">{value ?? '—'}</p>
        <p className="text-sm text-gray-400">{label}</p>
      </div>
    </div>
  )
}

function DashboardPage() {
  const { user } = useAuth()
  const [stats, setStats] = useState(null)

  useEffect(() => {
    api.get('/stats').then(r => setStats(r.data)).catch(() => {})
  }, [])

  const quickActions = [
    { href: '/documents', label: 'Upload Document', icon: Upload, desc: 'Add PDFs, DOCX, or text files' },
    { href: '/search', label: 'Search Knowledge', icon: Search, desc: 'Semantic search across all docs' },
    { href: '/ask', label: 'Ask AI', icon: MessageSquare, desc: 'Get AI-powered answers' },
  ]

  return (
    <Layout>
      <div className="max-w-5xl mx-auto space-y-8">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-white">
            Welcome back, {user?.full_name?.split(' ')[0] || 'there'} 👋
          </h1>
          <p className="text-gray-400 mt-1">Here's what's happening in your knowledge base.</p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard icon={FileText} label="Documents" value={stats?.total_documents} color="bg-indigo-600" />
          <StatCard icon={Database} label="Embeddings" value={stats?.total_embeddings} color="bg-violet-600" />
          <StatCard icon={Search} label="Searches" value={stats?.total_searches} color="bg-blue-600" />
          <StatCard icon={MessageSquare} label="Q&A Sessions" value={stats?.total_qa} color="bg-emerald-600" />
        </div>

        {/* Quick actions */}
        <div>
          <h2 className="text-lg font-semibold text-white mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {quickActions.map(({ href, label, icon: Icon, desc }) => (
              <Link key={href} href={href}
                className="card hover:border-indigo-500 hover:bg-gray-800 transition-all group cursor-pointer">
                <div className="flex items-start gap-4">
                  <div className="w-10 h-10 bg-indigo-600/20 rounded-lg flex items-center justify-center shrink-0 group-hover:bg-indigo-600 transition-colors">
                    <Icon size={18} className="text-indigo-400 group-hover:text-white" />
                  </div>
                  <div className="flex-1">
                    <p className="font-semibold text-white text-sm">{label}</p>
                    <p className="text-xs text-gray-500 mt-0.5">{desc}</p>
                  </div>
                  <ArrowRight size={16} className="text-gray-600 group-hover:text-indigo-400 mt-1 transition-colors" />
                </div>
              </Link>
            ))}
          </div>
        </div>

        {/* Source breakdown */}
        {stats?.source_breakdown && Object.keys(stats.source_breakdown).length > 0 && (
          <div>
            <h2 className="text-lg font-semibold text-white mb-4">Document Sources</h2>
            <div className="card">
              <div className="space-y-3">
                {Object.entries(stats.source_breakdown).map(([source, count]) => (
                  <div key={source} className="flex items-center gap-3">
                    <span className="text-sm text-gray-400 w-20 capitalize">{source}</span>
                    <div className="flex-1 bg-gray-800 rounded-full h-2">
                      <div className="bg-indigo-500 h-2 rounded-full"
                        style={{ width: `${Math.round((count / stats.total_documents) * 100)}%` }} />
                    </div>
                    <span className="text-sm font-medium text-white w-6">{count}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </Layout>
  )
}

export default withAuth(DashboardPage)

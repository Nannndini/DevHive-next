import { useEffect, useState } from 'react'
import Layout from '../components/Layout'
import withAuth from '../components/withAuth'
import api from '../lib/api'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend } from 'recharts'
import { FileText, Database, Search, MessageSquare, Users } from 'lucide-react'
import { useAuth } from '../lib/auth'

const COLORS = ['#6366f1', '#8b5cf6', '#3b82f6', '#10b981', '#f59e0b', '#ef4444']

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

function StatsPage() {
  const [stats, setStats] = useState(null)
  const { user } = useAuth()

  useEffect(() => {
    api.get('/stats').then(r => setStats(r.data)).catch(() => {})
  }, [])

  const sourceData = stats?.source_breakdown
    ? Object.entries(stats.source_breakdown).map(([name, value]) => ({ name, value }))
    : []

  const typeData = stats?.type_breakdown
    ? Object.entries(stats.type_breakdown).map(([name, value]) => ({ name: name.toUpperCase(), value }))
    : []

  const activityData = [
    { name: 'Documents', value: stats?.total_documents || 0 },
    { name: 'Embeddings', value: stats?.total_embeddings || 0 },
    { name: 'Searches', value: stats?.total_searches || 0 },
    { name: 'Q&A', value: stats?.total_qa || 0 },
  ]

  return (
    <Layout>
      <div className="max-w-5xl mx-auto space-y-8">
        <div>
          <h1 className="text-2xl font-bold text-white">Analytics</h1>
          <p className="text-gray-400 text-sm mt-1">Insights into your knowledge base usage</p>
        </div>

        {/* Summary stats */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard icon={FileText} label="Documents" value={stats?.total_documents} color="bg-indigo-600" />
          <StatCard icon={Database} label="Embeddings" value={stats?.total_embeddings} color="bg-violet-600" />
          <StatCard icon={Search} label="Searches" value={stats?.total_searches} color="bg-blue-600" />
          <StatCard icon={MessageSquare} label="Q&A Sessions" value={stats?.total_qa} color="bg-emerald-600" />
          {user?.role === 'admin' && stats?.total_users != null && (
            <StatCard icon={Users} label="Total Users" value={stats.total_users} color="bg-orange-600" />
          )}
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Activity bar chart */}
          <div className="card">
            <h3 className="font-semibold text-white mb-4">Platform Activity</h3>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={activityData} barSize={32}>
                <XAxis dataKey="name" tick={{ fill: '#9ca3af', fontSize: 12 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: '#9ca3af', fontSize: 12 }} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={{ background: '#1f2937', border: '1px solid #374151', borderRadius: 8, color: '#f3f4f6' }} />
                <Bar dataKey="value" fill="#6366f1" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Source breakdown pie */}
          {sourceData.length > 0 && (
            <div className="card">
              <h3 className="font-semibold text-white mb-4">Document Sources</h3>
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie data={sourceData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={75} label={({ name, percent }) => `${name} ${Math.round(percent * 100)}%`}>
                    {sourceData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                  </Pie>
                  <Tooltip contentStyle={{ background: '#1f2937', border: '1px solid #374151', borderRadius: 8, color: '#f3f4f6' }} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* File type breakdown */}
          {typeData.length > 0 && (
            <div className="card">
              <h3 className="font-semibold text-white mb-4">File Types</h3>
              <div className="space-y-3">
                {typeData.map(({ name, value }, i) => (
                  <div key={name} className="flex items-center gap-3">
                    <span className="text-sm text-gray-400 w-12">{name}</span>
                    <div className="flex-1 bg-gray-800 rounded-full h-2">
                      <div className="h-2 rounded-full" style={{
                        width: `${Math.round((value / stats.total_documents) * 100)}%`,
                        background: COLORS[i % COLORS.length]
                      }} />
                    </div>
                    <span className="text-sm font-medium text-white w-6">{value}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </Layout>
  )
}

export default withAuth(StatsPage)

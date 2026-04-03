import { useEffect, useState } from 'react'
import Layout from '../components/Layout'
import withAuth from '../components/withAuth'
import api from '../lib/api'
import toast from 'react-hot-toast'
import { Shield, Users, Activity, ChevronDown } from 'lucide-react'

function AdminPage() {
  const [users, setUsers] = useState([])
  const [logs, setLogs] = useState([])
  const [tab, setTab] = useState('users')

  useEffect(() => {
    api.get('/admin/users').then(r => setUsers(r.data.users)).catch(() => toast.error('Failed to load users'))
    api.get('/audit-logs').then(r => setLogs(r.data.logs)).catch(() => {})
  }, [])

  const handleRoleChange = async (userId, newRole) => {
    try {
      await api.patch(`/admin/users/${userId}/role?role=${newRole}`)
      setUsers(users.map(u => u.id === userId ? { ...u, role: newRole } : u))
      toast.success('Role updated')
    } catch { toast.error('Failed to update role') }
  }

  return (
    <Layout>
      <div className="max-w-4xl mx-auto space-y-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-orange-600 rounded-xl flex items-center justify-center">
            <Shield size={20} className="text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white">Admin Panel</h1>
            <p className="text-gray-400 text-sm">Manage users and review audit logs</p>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-1 bg-gray-900 border border-gray-800 rounded-xl p-1 w-fit">
          {[['users', Users, 'Users'], ['logs', Activity, 'Audit Logs']].map(([key, Icon, label]) => (
            <button key={key} onClick={() => setTab(key)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors
                ${tab === key ? 'bg-indigo-600 text-white' : 'text-gray-400 hover:text-white'}`}>
              <Icon size={15} />
              {label}
            </button>
          ))}
        </div>

        {/* Users tab */}
        {tab === 'users' && (
          <div className="card">
            <h2 className="font-semibold text-white mb-4">{users.length} Users</h2>
            <div className="space-y-2">
              {users.map(u => (
                <div key={u.id} className="flex items-center gap-4 p-3 bg-gray-800 rounded-lg">
                  <div className="w-9 h-9 bg-indigo-700 rounded-full flex items-center justify-center text-sm font-bold text-white shrink-0">
                    {u.full_name?.[0]?.toUpperCase() || u.email[0].toUpperCase()}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-white text-sm truncate">{u.full_name || 'No name'}</p>
                    <p className="text-xs text-gray-500 truncate">{u.email}</p>
                  </div>
                  <p className="text-xs text-gray-500 hidden sm:block">{new Date(u.created_at).toLocaleDateString()}</p>
                  <select
                    value={u.role}
                    onChange={e => handleRoleChange(u.id, e.target.value)}
                    className="bg-gray-700 border border-gray-600 rounded-lg text-sm text-gray-200 px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-indigo-500">
                    <option value="user">User</option>
                    <option value="admin">Admin</option>
                  </select>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Logs tab */}
        {tab === 'logs' && (
          <div className="card">
            <h2 className="font-semibold text-white mb-4">Recent Audit Logs</h2>
            {logs.length === 0 ? (
              <p className="text-gray-500 text-sm">No audit logs yet.</p>
            ) : (
              <div className="space-y-2">
                {logs.map(log => (
                  <div key={log.id} className="flex items-center gap-4 p-3 bg-gray-800 rounded-lg">
                    <span className="text-xs font-mono bg-gray-700 text-indigo-300 px-2 py-1 rounded capitalize shrink-0">
                      {log.action.replace('_', ' ')}
                    </span>
                    <p className="text-sm text-gray-300 flex-1 truncate">{log.resource || '—'}</p>
                    <p className="text-xs text-gray-500 shrink-0">{new Date(log.created_at).toLocaleString()}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </Layout>
  )
}

export default withAuth(AdminPage, { adminOnly: true })

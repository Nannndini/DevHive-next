import { useEffect } from 'react'
import { useRouter } from 'next/router'
import { useAuth } from '../lib/auth'

export default function withAuth(Component, { adminOnly = false } = {}) {
  return function ProtectedPage(props) {
    const { user, loading } = useAuth()
    const router = useRouter()

    useEffect(() => {
      if (!loading) {
        if (!user) router.replace('/login')
        else if (adminOnly && user.role !== 'admin') router.replace('/dashboard')
      }
    }, [user, loading])

    if (loading || !user) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-950">
          <div className="flex flex-col items-center gap-3">
            <div className="w-10 h-10 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin" />
            <p className="text-gray-400 text-sm">Loading...</p>
          </div>
        </div>
      )
    }

    return <Component {...props} />
  }
}

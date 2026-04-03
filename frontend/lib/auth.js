import { createContext, useContext, useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import api from './api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    const stored = localStorage.getItem('devhive_user')
    const token = localStorage.getItem('devhive_token')
    if (stored && token) setUser(JSON.parse(stored))
    setLoading(false)
  }, [])

  const login = async (email, password) => {
    const { data } = await api.post('/auth/login', { email, password })
    localStorage.setItem('devhive_token', data.token)
    localStorage.setItem('devhive_user', JSON.stringify(data.user))
    setUser(data.user)
    return data.user
  }

  const register = async (email, password, full_name) => {
    const { data } = await api.post('/auth/register', { email, password, full_name })
    localStorage.setItem('devhive_token', data.token)
    localStorage.setItem('devhive_user', JSON.stringify(data.user))
    setUser(data.user)
    return data.user
  }

  const logout = () => {
    localStorage.removeItem('devhive_token')
    localStorage.removeItem('devhive_user')
    setUser(null)
    router.push('/login')
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)

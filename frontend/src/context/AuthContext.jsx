import { createContext, useContext, useEffect, useState } from 'react'
import api from '../services/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => JSON.parse(localStorage.getItem('user') || 'null'))
  const [token, setToken] = useState(() => localStorage.getItem('access_token'))
  const [loading, setLoading] = useState(Boolean(token))
  useEffect(() => {
    if (!token) { setLoading(false); return }
    api.get('/auth/me').then(({ data }) => { setUser(data); localStorage.setItem('user', JSON.stringify(data)) }).catch(() => { localStorage.removeItem('access_token'); localStorage.removeItem('user'); setToken(null); setUser(null) }).finally(() => setLoading(false))
  }, [token])
  const login = (data) => { localStorage.setItem('access_token', data.access_token); localStorage.setItem('user', JSON.stringify(data.user)); setToken(data.access_token); setUser(data.user) }
  const logout = () => { localStorage.removeItem('access_token'); localStorage.removeItem('user'); setToken(null); setUser(null) }
  return <><AuthContext.Provider value={{ user, token, loading, isAuthenticated: Boolean(user && token), login, logout }}>{children}</AuthContext.Provider>{user && <div className="account-control"><div><strong>{user.store_name || 'My Store'}</strong><span>{user.full_name}</span></div><button onClick={logout}>Logout</button></div>}</>
}

export function useAuth() { return useContext(AuthContext) }

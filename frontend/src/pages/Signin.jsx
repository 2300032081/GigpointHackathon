import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Eye, EyeOff, Mic } from 'lucide-react'
import api from '../services/api'
import { useAuth } from '../context/AuthContext'

export default function Signin() {
  const { login } = useAuth(); const navigate = useNavigate(); const [form, setForm] = useState({ email: '', password: '' }); const [show, setShow] = useState(false); const [error, setError] = useState(''); const [loading, setLoading] = useState(false)
  const submit = async (event) => { event.preventDefault(); setLoading(true); setError(''); try { const { data } = await api.post('/auth/signin', form); login(data); navigate('/dashboard') } catch { setError('Invalid email or password.') } finally { setLoading(false) } }
  return <div className="auth-page"><div className="auth-brand"><span className="brand-mark"><Mic size={18}/></span><strong>VyaparVoice</strong></div><div className="auth-card"><span className="section-kicker">WELCOME BACK</span><h1>Sign in to your store.</h1><p>Pick up where you left off and keep your shelves moving.</p><form onSubmit={submit}><label>Email address<input type="email" required value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} placeholder="you@example.com"/></label><label>Password<div className="password-input"><input type={show ? 'text' : 'password'} required value={form.password} onChange={e => setForm({ ...form, password: e.target.value })} placeholder="Your password"/><button type="button" onClick={() => setShow(!show)}>{show ? <EyeOff size={16}/> : <Eye size={16}/>}</button></div></label>{error && <div className="form-error">{error}</div>}<button className="primary-button full" disabled={loading}>{loading ? 'Signing in...' : 'Sign In'}</button></form><div className="auth-switch">Don't have an account? <Link to="/signup">Create one</Link></div></div></div>
}

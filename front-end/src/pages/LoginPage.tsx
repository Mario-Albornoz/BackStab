import { type FormEvent, useState } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import { API_BASE_URL, apiFetch, toFriendlyError } from '../api'
import { useAuth } from '../contexts/AuthContext'

type NoticeType = 'info' | 'success' | 'error'

export function LoginPage() {
  const { tokens, setTokens } = useAuth()
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [notice, setNotice] = useState('')
  const [noticeType, setNoticeType] = useState<NoticeType>('info')

  if (tokens?.access) {
    return <Navigate to="/" replace />
  }

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()
    setLoading(true)
    setNoticeType('info')
    setNotice('Logging you in...')
    try {
      const payload = (await apiFetch('/api/auth/login/', null, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      })) as { access: string; refresh: string }
      setTokens(payload)
      navigate('/', { replace: true })
    } catch (error) {
      setNoticeType('error')
      setNotice(toFriendlyError(error, 'login'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="auth-shell">
      <div className="auth-card">
        <h1>Log in</h1>
        <p className="hint">BackStab Tracker · {API_BASE_URL}</p>
        {notice && <p className={`notice ${noticeType}`}>{notice}</p>}
        <form className="grid" onSubmit={handleSubmit}>
          <label>
            Username
            <input
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              autoComplete="username"
              required
            />
          </label>
          <label>
            Password
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
              minLength={8}
              required
            />
          </label>
          <button type="submit" disabled={loading}>
            {loading ? 'Logging in…' : 'Log in'}
          </button>
        </form>
        <p className="auth-footer">
          No account? <Link to="/sign-up">Create one</Link>
        </p>
      </div>
    </main>
  )
}

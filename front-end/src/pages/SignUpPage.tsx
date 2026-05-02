import { type FormEvent, useState } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import { API_BASE_URL, apiFetch, toFriendlyError } from '../api'
import { useAuth } from '../contexts/AuthContext'

type NoticeType = 'info' | 'success' | 'error'

export function SignUpPage() {
  const { tokens } = useAuth()
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
    setNotice('Creating your account...')
    try {
      await apiFetch('/api/auth/signup/', null, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      })
      setNoticeType('success')
      setNotice('Account created successfully. You can log in now.')
      setTimeout(() => navigate('/login', { replace: true }), 900)
    } catch (error) {
      setNoticeType('error')
      setNotice(toFriendlyError(error, 'signup'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="auth-shell">
      <div className="auth-card">
        <h1>Create account</h1>
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
              autoComplete="new-password"
              minLength={8}
              required
            />
          </label>
          <button type="submit" disabled={loading}>
            {loading ? 'Creating…' : 'Sign up'}
          </button>
        </form>
        <p className="auth-footer">
          Already have an account? <Link to="/login">Log in</Link>
        </p>
      </div>
    </main>
  )
}

import { useMemo, useState } from 'react'
import { Navigate } from 'react-router-dom'
import type { ApiResult, ContactItem } from '../trackerTypes'
import { apiFetch, toFriendlyError } from '../api'
import { useAuth } from '../contexts/AuthContext'
import '../App.css'

type NoticeType = 'info' | 'success' | 'error'

export function TrackerPage() {
  const { tokens, logout } = useAuth()
  const [followersFile, setFollowersFile] = useState<File | null>(null)
  const [followingFile, setFollowingFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('Ready.')
  const [noticeType, setNoticeType] = useState<NoticeType>('info')
  const [result, setResult] = useState<ApiResult | null>(null)

  const isAuthenticated = useMemo(() => Boolean(tokens?.access), [tokens])

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  const setNotice = (text: string, type: NoticeType = 'info') => {
    setMessage(text)
    setNoticeType(type)
  }

  const request = async (path: string, init?: RequestInit) =>
    apiFetch(path, tokens!.access, init)

  const handleLogout = async () => {
    setNotice('Logging out...', 'info')
    if (tokens?.refresh) {
      try {
        await request('/api/auth/logout/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ refresh: tokens.refresh }),
        })
      } catch {
        /* ignore */
      }
    }
    logout()
    setResult(null)
  }

  const submitFollowers = async (
    path: '/contacts/tracking/lost-followers' | '/contacts/tracking/followers/submit',
  ) => {
    if (!followersFile) {
      setNotice('Please choose a followers JSON file first.', 'error')
      return
    }
    const formData = new FormData()
    formData.append('file', followersFile)

    setLoading(true)
    setNotice('Uploading followers file...', 'info')
    try {
      const payload = await request(path, {
        method: 'POST',
        body: formData,
      })
      if (path === '/contacts/tracking/followers/submit') {
        const response = payload as { total_followers?: number }
        setResult({
          kind: 'override',
          count: Number(response.total_followers ?? 0),
          note: 'Your followers list has been saved.',
        })
        setNotice('Followers list updated successfully.', 'success')
      } else {
        const response = payload as {
          lost_followers?: ContactItem[]
          baseline_initialized?: boolean
        }
        const items = response.lost_followers ?? []
        setResult({
          kind: 'lost',
          items,
          note: response.baseline_initialized
            ? 'First upload detected. We saved your baseline list and found no lost followers yet.'
            : undefined,
        })
        setNotice('Lost followers check completed.', 'success')
      }
    } catch (error) {
      setNotice(toFriendlyError(error, 'followers'), 'error')
    } finally {
      setLoading(false)
    }
  }

  const submitFollowing = async () => {
    if (!followingFile) {
      setNotice('Please choose a following JSON file first.', 'error')
      return
    }
    const formData = new FormData()
    formData.append('file', followingFile)

    setLoading(true)
    setNotice('Uploading following file...', 'info')
    try {
      const payload = await request('/contacts/tracking/non-followers', {
        method: 'POST',
        body: formData,
      })
      const response = payload as { non_followers?: ContactItem[] }
      setResult({
        kind: 'nonFollowers',
        items: response.non_followers ?? [],
      })
      setNotice('Non-followers check completed.', 'success')
    } catch (error) {
      setNotice(toFriendlyError(error, 'following'), 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="app-shell">
      <header className="tracker-header">
        <h1>BackStab Tracker</h1>
        <nav className="tracker-nav">
          <button type="button" disabled={loading} onClick={handleLogout}>
            Log out
          </button>
        </nav>
      </header>

      <section className="card">
        <h2>Followers JSON</h2>
        <input
          type="file"
          accept="application/json,.json"
          onChange={(event) => setFollowersFile(event.target.files?.[0] ?? null)}
        />
        <div className="actions">
          <button
            disabled={loading || !isAuthenticated}
            onClick={() => submitFollowers('/contacts/tracking/lost-followers')}
          >
            Check lost followers
          </button>
          <button
            disabled={loading || !isAuthenticated}
            onClick={() => submitFollowers('/contacts/tracking/followers/submit')}
          >
            Override followers in DB
          </button>
        </div>
      </section>

      <section className="card">
        <h2>Following JSON</h2>
        <input
          type="file"
          accept="application/json,.json"
          onChange={(event) => setFollowingFile(event.target.files?.[0] ?? null)}
        />
        <div className="actions">
          <button disabled={loading || !isAuthenticated} onClick={submitFollowing}>
            Find non-followers
          </button>
        </div>
      </section>

      <section className="card">
        <h2>Status</h2>
        <p className={`notice ${noticeType}`}>{message}</p>
        {!result && <p>No results yet. Upload a file and run an action.</p>}

        {result?.kind === 'override' && (
          <div>
            <p>{result.note}</p>
            <p>
              Total followers saved: <strong>{result.count}</strong>
            </p>
          </div>
        )}

        {result?.kind === 'lost' && (
          <div>
            <p>{result.note ?? 'These people are no longer following you:'}</p>
            {result.items.length === 0 ? (
              <p>No lost followers found.</p>
            ) : (
              <ul className="result-list">
                {result.items.map((item) => (
                  <li key={`${item.username}-${item.link_to_account ?? ''}`}>
                    <span>{item.username}</span>
                    {item.link_to_account && (
                      <a href={item.link_to_account} target="_blank" rel="noreferrer">
                        Open profile
                      </a>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}

        {result?.kind === 'nonFollowers' && (
          <div>
            <p>These accounts do not follow you back:</p>
            {result.items.length === 0 ? (
              <p>Great news - everyone in this list follows you back.</p>
            ) : (
              <ul className="result-list">
                {result.items.map((item) => (
                  <li key={`${item.username}-${item.link_to_account ?? ''}`}>
                    <span>{item.username}</span>
                    {item.link_to_account && (
                      <a href={item.link_to_account} target="_blank" rel="noreferrer">
                        Open profile
                      </a>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}
      </section>
    </main>
  )
}

import {
  createContext,
  type ReactNode,
  useCallback,
  useContext,
  useMemo,
  useState,
} from 'react'
import type { AuthTokens } from '../api'
import { clearStoredTokens, loadStoredTokens, saveTokens } from '../api'

type AuthContextValue = {
  tokens: AuthTokens | null
  setTokens: (tokens: AuthTokens | null) => void
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [tokens, setTokensState] = useState<AuthTokens | null>(() => loadStoredTokens())

  const setTokens = useCallback((next: AuthTokens | null) => {
    setTokensState(next)
    if (next) saveTokens(next)
    else clearStoredTokens()
  }, [])

  const logout = useCallback(() => {
    clearStoredTokens()
    setTokensState(null)
  }, [])

  const value = useMemo(
    () => ({
      tokens,
      setTokens,
      logout,
    }),
    [tokens, setTokens, logout],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}

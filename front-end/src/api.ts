// In Docker the frontend and backend share the same origin via nginx proxy.
// In local dev VITE_API_BASE_URL points to the Django dev server directly.
export const API_BASE_URL =
  (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? ''

export type AuthTokens = {
  access: string
  refresh: string
}

export async function apiFetch(path: string, accessToken: string | null, init?: RequestInit) {
  const headers = new Headers(init?.headers ?? {})
  if (accessToken) {
    headers.set('Authorization', `Bearer ${accessToken}`)
  }
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers,
  })
  const contentType = response.headers.get('content-type') ?? ''
  const payload = contentType.includes('application/json') ? await response.json() : await response.text()

  if (!response.ok) {
    const detail =
      typeof payload === 'object' && payload !== null && 'detail' in payload
        ? String((payload as { detail: unknown }).detail)
        : `Request failed with status ${response.status}`
    throw new Error(detail || `Request failed with status ${response.status}`)
  }
  return payload
}

export function toFriendlyError(
  error: unknown,
  action: 'signup' | 'login' | 'followers' | 'following',
): string {
  const fallbackMap = {
    signup: 'Could not create your account. Please try again.',
    login: 'Could not log in. Please check your username and password.',
    followers: 'Could not process your followers file.',
    following: 'Could not process your following file.',
  }
  const fallback = fallbackMap[action]
  if (!(error instanceof Error)) return fallback
  const msg = error.message.toLowerCase()

  if (msg.includes('failed to fetch') || msg.includes('network')) {
    return 'Cannot connect to the server. Please make sure the app backend is running.'
  }
  if (msg.includes('401') || msg.includes('not authenticated') || msg.includes('credentials')) {
    return 'Your session expired or login details are invalid. Please log in again.'
  }
  if (msg.includes('json') || msg.includes('relationships_following') || msg.includes('array')) {
    return 'The uploaded file format is not valid. Please export and upload the correct Instagram JSON file.'
  }
  if (msg.includes('already exists') || msg.includes('unique')) {
    return 'That username is already taken. Try another one.'
  }
  if (msg.includes('min_length') || msg.includes('at least 8')) {
    return 'Password must be at least 8 characters.'
  }
  return error.message || fallback
}

const AUTH_STORAGE_KEY = 'backstab_auth'

export function loadStoredTokens(): AuthTokens | null {
  try {
    const raw = localStorage.getItem(AUTH_STORAGE_KEY)
    if (!raw) return null
    const parsed = JSON.parse(raw) as Partial<AuthTokens>
    if (parsed.access && parsed.refresh) {
      return { access: parsed.access, refresh: parsed.refresh }
    }
  } catch {
    /* ignore */
  }
  return null
}

export function saveTokens(tokens: AuthTokens): void {
  localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(tokens))
}

export function clearStoredTokens(): void {
  localStorage.removeItem(AUTH_STORAGE_KEY)
}

import { createClient } from 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js/+esm'

const supabaseUrl = 'https://pprhoevhbpjiucubsmlw.supabase.co'
const supabaseKey = 'sb_publishable_gejpN-iGtqsKYwo8Aq8PVQ_zpnOd-ZT'

export const supabase = createClient(supabaseUrl, supabaseKey)

// Utility to check session and redirect if not logged in
export async function requireAuth() {
    const { data: { session }, error } = await supabase.auth.getSession()
    if (error || !session) {
        if (!window.location.pathname.endsWith('/login.html')) {
            window.location.replace('index.html')
        }
        return null
    }
    return session
}

export async function getAccessToken() {
    const session = await requireAuth()
    return session?.access_token || null
}

export async function authenticatedFetch(url, options = {}) {
    const token = await getAccessToken()
    if (!token) throw new Error('Authentication is required.')
    const headers = new Headers(options.headers || {})
    headers.set('Authorization', `Bearer ${token}`)
    return fetch(url, { ...options, headers })
}

export async function getCurrentUserProfile() {
    const response = await authenticatedFetch('/api/auth/me')
    if (!response.ok) return null
    return response.json()
}

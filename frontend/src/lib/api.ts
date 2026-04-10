import { GWAConfig, WorkspaceStats, WorkspaceData } from './types'

const BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

// Generate a session ID once per browser tab and persist it for the tab's lifetime.
function getSessionId(): string {
  const KEY = 'gwa_session_id'
  let id = sessionStorage.getItem(KEY)
  if (!id) {
    id = crypto.randomUUID()
    sessionStorage.setItem(KEY, id)
  }
  return id
}

function sessionHeaders(): Record<string, string> {
  return {
    'Content-Type': 'application/json',
    'X-Session-ID': getSessionId(),
  }
}

export async function getHealth(): Promise<{ status: string; engine_ready: boolean }> {
  const res = await fetch(`${BASE}/api/health`, {
    headers: { 'X-Session-ID': getSessionId() },
  })
  return res.json()
}

export async function postConfig(config: GWAConfig): Promise<{ status: string }> {
  const res = await fetch(`${BASE}/api/config`, {
    method: 'POST',
    headers: sessionHeaders(),
    body: JSON.stringify(config),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err?.detail ?? `HTTP ${res.status}`)
  }
  return res.json()
}

export async function getConfig(): Promise<GWAConfig> {
  const res = await fetch(`${BASE}/api/config`, {
    headers: { 'X-Session-ID': getSessionId() },
  })
  return res.json()
}

export async function getStats(): Promise<WorkspaceStats> {
  const res = await fetch(`${BASE}/api/stats`, {
    headers: { 'X-Session-ID': getSessionId() },
  })
  return res.json()
}

export async function deleteSession(): Promise<{ status: string }> {
  const res = await fetch(`${BASE}/api/session`, {
    method: 'DELETE',
    headers: { 'X-Session-ID': getSessionId() },
  })
  return res.json()
}

export function chatStream(message: string): Response {
  return fetch(`${BASE}/api/chat`, {
    method: 'POST',
    headers: sessionHeaders(),
    body: JSON.stringify({ message }),
  }) as unknown as Response
}

export async function enableIdle(): Promise<void> {
  await fetch(`${BASE}/api/idle/enable`, {
    method: 'POST',
    headers: { 'X-Session-ID': getSessionId() },
  })
}

export async function disableIdle(): Promise<void> {
  await fetch(`${BASE}/api/idle/disable`, {
    method: 'POST',
    headers: { 'X-Session-ID': getSessionId() },
  })
}

export async function getWorkspace(): Promise<WorkspaceData> {
  const res = await fetch(`${BASE}/api/workspace`, {
    headers: { 'X-Session-ID': getSessionId() },
  })
  return res.json()
}

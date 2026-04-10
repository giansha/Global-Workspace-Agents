import { GWAConfig, WorkspaceStats, WorkspaceData } from './types'

const BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

export async function getHealth(): Promise<{ status: string; engine_ready: boolean }> {
  const res = await fetch(`${BASE}/api/health`)
  return res.json()
}

export async function postConfig(config: GWAConfig): Promise<{ status: string }> {
  const res = await fetch(`${BASE}/api/config`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(config),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err?.detail ?? `HTTP ${res.status}`)
  }
  return res.json()
}

export async function getConfig(): Promise<GWAConfig> {
  const res = await fetch(`${BASE}/api/config`)
  return res.json()
}

export async function getStats(): Promise<WorkspaceStats> {
  const res = await fetch(`${BASE}/api/stats`)
  return res.json()
}

export async function deleteSession(): Promise<{ status: string }> {
  const res = await fetch(`${BASE}/api/session`, { method: 'DELETE' })
  return res.json()
}

export function chatStream(message: string): Response {
  return fetch(`${BASE}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message }),
  }) as unknown as Response
}

export async function enableIdle(): Promise<void> {
  await fetch(`${BASE}/api/idle/enable`, { method: 'POST' })
}

export async function disableIdle(): Promise<void> {
  await fetch(`${BASE}/api/idle/disable`, { method: 'POST' })
}

export async function getWorkspace(): Promise<WorkspaceData> {
  const res = await fetch(`${BASE}/api/workspace`)
  return res.json()
}

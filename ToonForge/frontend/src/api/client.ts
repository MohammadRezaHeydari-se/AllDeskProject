import type { Project, MappingOverride, SceneManifest, ExportFormat, RenderQuality } from '@/types'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'

async function fetchJSON<T>(url: string, options?: RequestInit): Promise<T> {
  const body = options?.body
  const skipContentType = body instanceof FormData || body instanceof URLSearchParams
  const headers: Record<string, string> = {}
  if (!skipContentType) headers['Content-Type'] = 'application/json'
  const res = await fetch(`${API_BASE}${url}`, {
    headers: { ...headers, ...(options?.headers as Record<string, string>) },
    ...options,
  })
  if (!res.ok) {
    const err = await res.text()
    throw new Error(`API error ${res.status}: ${err}`)
  }
  return res.json()
}

export const api = {
  // Projects
  listProjects: () => fetchJSON<Project[]>('/projects/'),

  createProject: (name: string) =>
    fetchJSON<Project>('/projects/', {
      method: 'POST',
      body: new URLSearchParams({ name }),
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    }),

  getProject: (id: string) => fetchJSON<Project>(`/projects/${id}`),

  updateProject: (id: string, project: Project) =>
    fetchJSON<Project>(`/projects/${id}`, {
      method: 'PUT',
      body: JSON.stringify(project),
    }),

  importAudio: (projectId: string, files: File[]) => {
    const form = new FormData()
    files.forEach(f => form.append('files', f))
    return fetchJSON<Project>(`/projects/${projectId}/import/audio`, {
      method: 'POST',
      body: form,
    })
  },

  importCharacters: (projectId: string, files: File[]) => {
    const form = new FormData()
    files.forEach(f => form.append('files', f))
    return fetchJSON<Project>(`/projects/${projectId}/import/characters`, {
      method: 'POST',
      body: form,
    })
  },

  importBackground: (projectId: string, file: File) => {
    const form = new FormData()
    form.append('file', file)
    return fetchJSON<Project>(`/projects/${projectId}/import/background`, {
      method: 'POST',
      body: form,
    })
  },

  // Scenes
  generateScene: (projectId: string) =>
    fetchJSON<Project>(`/scenes/generate/${projectId}`, { method: 'POST' }),

  updateMapping: (projectId: string, overrides: MappingOverride[]) =>
    fetchJSON<Project>(`/scenes/mapping/${projectId}`, {
      method: 'POST',
      body: JSON.stringify(overrides),
    }),

  getManifest: (projectId: string) =>
    fetchJSON<SceneManifest>(`/scenes/manifest/${projectId}`),

  // Render
  exportScene: (sceneId: string, format: ExportFormat, includeSubtitles: boolean, quality: RenderQuality) =>
    fetchJSON<{ status: string; render_id: string; output_path: string }>('/render/export', {
      method: 'POST',
      body: JSON.stringify({ scene_id: sceneId, format, include_subtitles: includeSubtitles, quality }),
    }),

  renderStatus: (renderId: string) =>
    fetchJSON<{ status: string; output?: string; error?: string; progress?: number }>(`/render/status/${renderId}`),
}

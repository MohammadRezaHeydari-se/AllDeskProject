'use client'

import { useRef, useState } from 'react'
import { api } from '@/api/client'
import type { Project } from '@/types'

interface Props {
  onProjectLoad: (project: Project) => void
  onLog?: (message: string, type?: 'info' | 'success' | 'error' | 'warning') => void
  variant?: 'default' | 'large'
  currentProject?: Project | null
}

export function ImportPanel({ onProjectLoad, onLog, variant = 'default', currentProject }: Props) {
  const [loading, setLoading] = useState(false)
  const audioRef = useRef<HTMLInputElement>(null)
  const charRef = useRef<HTMLInputElement>(null)
  const bgRef = useRef<HTMLInputElement>(null)

  const getOrCreateProject = async () => {
    if (currentProject) {
      onLog?.(`Reusing project ${currentProject.id.slice(0, 8)}...`, 'info')
      return currentProject
    }
    onLog?.('Creating new project...', 'info')
    return api.createProject('Untitled Project')
  }

  const handleImport = async (type: 'audio' | 'characters' | 'background', files: FileList | null) => {
    if (!files || files.length === 0) return
    setLoading(true)
    const fileNames = Array.from(files).map(f => f.name).join(', ')
    onLog?.(`Importing ${type}: ${fileNames}`, 'info')
    try {
      let project = await getOrCreateProject()

      if (type === 'audio') {
        onLog?.(`Uploading ${files.length} audio file(s)...`, 'info')
        project = await api.importAudio(project.id, Array.from(files))
        onLog?.(`Audio imported: ${files.length} file(s)`, 'success')
      } else if (type === 'characters') {
        onLog?.(`Uploading ${files.length} character image(s)...`, 'info')
        project = await api.importCharacters(project.id, Array.from(files))
        onLog?.(`Characters imported: ${files.length} file(s)`, 'success')
      } else if (type === 'background') {
        onLog?.('Uploading background image...', 'info')
        project = await api.importBackground(project.id, files[0])
        onLog?.('Background imported', 'success')
      }

      onLog?.('Generating scene...', 'info')
      project = await api.generateScene(project.id)
      onLog?.(`Scene generated: ${project.characters.length} characters, ${project.audio_clips.length} audio clips`, 'success')
      onProjectLoad(project)
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err)
      onLog?.(`Import failed: ${msg}`, 'error')
      console.error('Import failed:', err)
      alert('Failed to import files. Make sure the backend server is running.')
    } finally {
      setLoading(false)
    }
  }

  if (variant === 'large') {
    return (
      <div className="flex flex-col items-center gap-4">
        <div className="flex gap-4">
          <button
            onClick={() => audioRef.current?.click()}
            disabled={loading}
            className="px-6 py-3 bg-surface-alt hover:bg-surface-hover border border-white/10 rounded-xl text-sm text-white/80 transition-colors"
          >
            <span className="block text-lg mb-1">🎵</span>
            Import Audio
          </button>
          <button
            onClick={() => charRef.current?.click()}
            disabled={loading}
            className="px-6 py-3 bg-surface-alt hover:bg-surface-hover border border-white/10 rounded-xl text-sm text-white/80 transition-colors"
          >
            <span className="block text-lg mb-1">🧑</span>
            Import Characters
          </button>
          <button
            onClick={() => bgRef.current?.click()}
            disabled={loading}
            className="px-6 py-3 bg-surface-alt hover:bg-surface-hover border border-white/10 rounded-xl text-sm text-white/80 transition-colors"
          >
            <span className="block text-lg mb-1">🖼️</span>
            Import Background
          </button>
        </div>
        <input ref={audioRef} type="file" multiple accept=".wav,.mp3,.ogg" className="hidden" onChange={e => handleImport('audio', e.target.files)} />
        <input ref={charRef} type="file" multiple accept=".png,.jpg" className="hidden" onChange={e => handleImport('characters', e.target.files)} />
        <input ref={bgRef} type="file" accept=".png,.jpg" className="hidden" onChange={e => handleImport('background', e.target.files)} />
        {loading && <p className="text-sm text-white/40 animate-pulse">Importing and analyzing...</p>}
      </div>
    )
  }

  return (
    <div className="flex items-center gap-2">
      <button
        onClick={() => audioRef.current?.click()}
        disabled={loading}
        className="px-3 py-1.5 bg-surface-alt hover:bg-surface-hover border border-white/10 rounded-lg text-xs text-white/60 transition-colors"
      >
        + Audio
      </button>
      <button
        onClick={() => charRef.current?.click()}
        disabled={loading}
        className="px-3 py-1.5 bg-surface-alt hover:bg-surface-hover border border-white/10 rounded-lg text-xs text-white/60 transition-colors"
      >
        + Characters
      </button>
      <button
        onClick={() => bgRef.current?.click()}
        disabled={loading}
        className="px-3 py-1.5 bg-surface-alt hover:bg-surface-hover border border-white/10 rounded-lg text-xs text-white/60 transition-colors"
      >
        + Background
      </button>
      <input ref={audioRef} type="file" multiple accept=".wav,.mp3,.ogg" className="hidden" onChange={e => handleImport('audio', e.target.files)} />
      <input ref={charRef} type="file" multiple accept=".png,.jpg" className="hidden" onChange={e => handleImport('characters', e.target.files)} />
      <input ref={bgRef} type="file" accept=".png,.jpg" className="hidden" onChange={e => handleImport('background', e.target.files)} />
    </div>
  )
}

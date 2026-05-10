'use client'

import { useState } from 'react'
import { api } from '@/api/client'
import type { Project, MappingOverride } from '@/types'

interface Props {
  project: Project
  onUpdate: (p: Project) => void
}

export function CharacterPanel({ project, onUpdate }: Props) {
  const [editingId, setEditingId] = useState<string | null>(null)

  const handleMappingChange = async (audioId: string, characterId: string) => {
    const overrides: MappingOverride[] = project.audio_clips.map(clip => ({
      audio_id: clip.id,
      character_id: clip.id === audioId ? characterId : (clip.character_id || ''),
      order: clip.order,
      subtitle: clip.subtitle,
    }))
    try {
      const updated = await api.updateMapping(project.id, overrides)
      onUpdate(updated)
    } catch (err) {
      console.error('Failed to update mapping:', err)
    }
  }

  return (
    <div className="p-4 space-y-4">
      <div className="space-y-1">
        <h3 className="text-sm font-medium text-white">Character Mapping</h3>
        <p className="text-xs text-white/40">Assign audio clips to characters</p>
      </div>

      <div className="space-y-2">
        {project.characters.map(char => (
          <div
            key={char.id}
            className="flex items-center gap-3 p-3 rounded-lg bg-surface-alt border border-white/5"
          >
            <div
              className="w-10 h-10 rounded-lg bg-cover bg-center border border-white/10"
              style={{ backgroundColor: char.color + '30' }}
            />
            <div className="flex-1 min-w-0">
              <p className="text-sm text-white font-medium truncate">{char.name}</p>
              <p className="text-xs text-white/40 truncate">{char.image_path.split('/').pop()}</p>
            </div>
            <div className="w-2 h-2 rounded-full" style={{ backgroundColor: char.color }} />
          </div>
        ))}
      </div>

      <div className="space-y-1 pt-4 border-t border-white/5">
        <h3 className="text-sm font-medium text-white">Audio Assignments</h3>
        <p className="text-xs text-white/40">Reorder and reassign audio to characters</p>
      </div>

      <div className="space-y-2">
        {project.audio_clips
          .sort((a, b) => a.order - b.order)
          .map((clip, idx) => (
            <div
              key={clip.id}
              className="flex items-center gap-2 p-2.5 rounded-lg bg-surface-alt border border-white/5"
            >
              <span className="text-xs text-white/30 w-5">{idx + 1}</span>
              <div className="flex-1 min-w-0">
                <p className="text-xs text-white truncate">{clip.filename}</p>
                <p className="text-[10px] text-white/30">{clip.duration.toFixed(1)}s</p>
              </div>
              <select
                value={clip.character_id || ''}
                onChange={e => handleMappingChange(clip.id, e.target.value)}
                className="text-xs bg-surface border border-white/10 rounded px-2 py-1 text-white/70 outline-none focus:border-primary/50"
              >
                <option value="">Unassigned</option>
                {project.characters.map(char => (
                  <option key={char.id} value={char.id}>{char.name}</option>
                ))}
              </select>
            </div>
          ))}
      </div>

      {project.audio_clips.length === 0 && (
        <p className="text-xs text-white/30 text-center py-8">No audio clips imported yet</p>
      )}
    </div>
  )
}

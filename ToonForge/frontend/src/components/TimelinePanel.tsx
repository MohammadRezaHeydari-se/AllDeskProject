'use client'

import { useState, useRef } from 'react'
import { api } from '@/api/client'
import type { Project, MappingOverride } from '@/types'

interface Props {
  project: Project
  onUpdate: (p: Project) => void
}

export function TimelinePanel({ project, onUpdate }: Props) {
  const [draggedIdx, setDraggedIdx] = useState<number | null>(null)
  const [subtitles, setSubtitles] = useState<Record<string, string>>({})

  const sortedClips = [...project.audio_clips].sort((a, b) => a.order - b.order)

  const getCharacterName = (charId: string | null) => {
    if (!charId) return 'Unassigned'
    return project.characters.find(c => c.id === charId)?.name || charId
  }

  const getCharacterColor = (charId: string | null) => {
    if (!charId) return '#555'
    return project.characters.find(c => c.id === charId)?.color || '#555'
  }

  const handleDragStart = (idx: number) => {
    setDraggedIdx(idx)
  }

  const handleDrop = async (targetIdx: number) => {
    if (draggedIdx === null || draggedIdx === targetIdx) return

    const reordered = [...sortedClips]
    const [moved] = reordered.splice(draggedIdx, 1)
    reordered.splice(targetIdx, 0, moved)

    const overrides: MappingOverride[] = reordered.map((clip, i) => ({
      audio_id: clip.id,
      character_id: clip.character_id || '',
      order: i,
      subtitle: subtitles[clip.id] || clip.subtitle,
    }))

    try {
      const updated = await api.updateMapping(project.id, overrides)
      onUpdate(updated)
    } catch (err) {
      console.error('Failed to reorder:', err)
    }
    setDraggedIdx(null)
  }

  const handleSubtitleChange = async (clipId: string, text: string) => {
    setSubtitles(prev => ({ ...prev, [clipId]: text }))

    const overrides: MappingOverride[] = project.audio_clips.map(clip => ({
      audio_id: clip.id,
      character_id: clip.character_id || '',
      order: clip.order,
      subtitle: clip.id === clipId ? text : (subtitles[clip.id] || clip.subtitle),
    }))

    try {
      await api.updateMapping(project.id, overrides)
    } catch (err) {
      console.error('Failed to update subtitle:', err)
    }
  }

  const maxDuration = sortedClips.reduce((max, c) => Math.max(max, c.duration), 1)

  return (
    <div className="p-4 space-y-4">
      <div className="space-y-1">
        <h3 className="text-sm font-medium text-white">Timeline</h3>
        <p className="text-xs text-white/40">Drag clips to reorder, edit subtitles</p>
      </div>

      <div className="space-y-1">
        {sortedClips.map((clip, idx) => (
          <div
            key={clip.id}
            draggable
            onDragStart={() => handleDragStart(idx)}
            onDragOver={e => e.preventDefault()}
            onDrop={() => handleDrop(idx)}
            className={`group relative p-3 rounded-lg border transition-all ${
              draggedIdx === idx
                ? 'opacity-50 border-primary/30 bg-primary/5'
                : 'border-white/5 bg-surface-alt hover:border-white/10'
            }`}
          >
            <div className="flex items-center gap-3 mb-2">
              <span className="text-xs text-white/30 w-5 shrink-0">{idx + 1}</span>
              <div
                className="w-3 h-3 rounded-full shrink-0"
                style={{ backgroundColor: getCharacterColor(clip.character_id) }}
              />
              <div className="flex-1 min-w-0">
                <p className="text-xs text-white truncate">{clip.filename}</p>
              </div>
              <span className="text-[10px] text-white/30 shrink-0">{clip.duration.toFixed(1)}s</span>
              <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <button className="p-1 rounded hover:bg-white/5 text-white/30 hover:text-white/60">
                  <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>

            <div className="relative h-6 bg-black/20 rounded overflow-hidden ml-8">
              <div
                className="absolute inset-y-0 left-0 rounded transition-all"
                style={{
                  width: `${(clip.duration / maxDuration) * 100}%`,
                  backgroundColor: getCharacterColor(clip.character_id) + '40',
                }}
              >
                <div
                  className="h-full w-full"
                  style={{
                    background: `linear-gradient(90deg, transparent 0%, ${getCharacterColor(clip.character_id)}20 50%, transparent 100%)`,
                    backgroundSize: '200% 100%',
                    animation: 'shimmer 2s infinite',
                  }}
                />
              </div>
            </div>

            <div className="ml-8 mt-2">
              <input
                type="text"
                placeholder="Add subtitle..."
                value={subtitles[clip.id] ?? clip.subtitle ?? ''}
                onChange={e => handleSubtitleChange(clip.id, e.target.value)}
                className="w-full text-xs bg-black/20 border border-white/5 rounded px-2 py-1 text-white/50 placeholder:text-white/20 outline-none focus:border-primary/30"
              />
            </div>

            <div className="ml-8 mt-1.5 flex items-center gap-2">
              <span className="text-[10px] text-white/20">{getCharacterName(clip.character_id)}</span>
            </div>
          </div>
        ))}
      </div>

      {sortedClips.length === 0 && (
        <p className="text-xs text-white/30 text-center py-8">Import audio files to build your timeline</p>
      )}
    </div>
  )
}

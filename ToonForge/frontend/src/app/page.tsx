'use client'

import { useState, useCallback } from 'react'
import { ImportPanel } from '@/components/ImportPanel'
import { CharacterPanel } from '@/components/CharacterPanel'
import { TimelinePanel } from '@/components/TimelinePanel'
import { ScenePreview } from '@/components/ScenePreview'
import { ExportButton } from '@/components/ExportButton'
import { StatusLog, createLogEntry } from '@/components/StatusLog'
import type { Project } from '@/types'
import type { LogEntry } from '@/components/StatusLog'

export default function Home() {
  const [project, setProject] = useState<Project | null>(null)
  const [activeTab, setActiveTab] = useState<'timeline' | 'characters'>('timeline')
  const [logs, setLogs] = useState<LogEntry[]>([])

  const addLog = useCallback((message: string, type: LogEntry['type'] = 'info') => {
    setLogs(prev => [...prev, createLogEntry(message, type)])
  }, [])

  const handleProjectLoad = useCallback((p: Project) => {
    setProject(p)
    addLog(`Project loaded: ${p.name} (${p.id.slice(0, 8)}...)`, 'success')
    addLog(`Characters: ${p.characters.length}, Audio clips: ${p.audio_clips.length}`, 'info')
  }, [addLog])

  return (
    <div className="h-screen flex flex-col overflow-hidden">
      <header className="h-14 bg-surface border-b border-white/5 flex items-center justify-between px-6 shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
            <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 4v16M17 4v16M3 8h4m10 0h4M3 12h18M3 16h4m10 0h4M4 20h16a1 1 0 001-1V5a1 1 0 00-1-1H4a1 1 0 00-1 1v14a1 1 0 001 1z" />
            </svg>
          </div>
          <h1 className="text-lg font-semibold text-white">ToonForge</h1>
          {project && (
            <span className="text-sm text-white/40 ml-2">/ {project.name}</span>
          )}
        </div>
        <div className="flex items-center gap-3">
          {project && <ExportButton project={project} onLog={addLog} />}
          <ImportPanel onProjectLoad={handleProjectLoad} onLog={addLog} currentProject={project} />
        </div>
      </header>

      {!project ? (
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center max-w-md">
            <div className="w-20 h-20 rounded-2xl bg-surface mx-auto mb-6 flex items-center justify-center">
              <svg className="w-10 h-10 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15.182 15.182a4.5 4.5 0 01-6.364 0M21 12a9 9 0 11-18 0 9 9 0 0118 0zM9.75 9.75c0 .414-.168.75-.375.75S9 10.164 9 9.75 9.168 9 9.375 9s.375.336.375.75zm-.375 0h.008v.015h-.008V9.75zm5.625 0c0 .414-.168.75-.375.75s-.375-.336-.375-.75.168-.75.375-.75.375.336.375.75zm-.375 0h.008v.015h-.008V9.75z" />
              </svg>
            </div>
            <h2 className="text-xl font-semibold text-white mb-2">Welcome to ToonForge</h2>
            <p className="text-white/50 text-sm mb-8 leading-relaxed">
              Import character images, audio dialogue files, and a background to automatically generate animated dialogue scenes.
            </p>
            <ImportPanel onProjectLoad={handleProjectLoad} onLog={addLog} variant="large" />
          </div>
          <div className="absolute bottom-4 left-4 right-4 max-w-md mx-auto">
            <StatusLog logs={logs} />
          </div>
        </div>
      ) : (
        <div className="flex-1 flex overflow-hidden">
          <div className="flex-1 flex flex-col min-w-0">
            <ScenePreview project={project} />
          </div>
          <div className="w-96 bg-surface border-l border-white/5 flex flex-col shrink-0">
            <div className="flex border-b border-white/5">
              <button
                onClick={() => setActiveTab('timeline')}
                className={`flex-1 py-3 text-sm font-medium transition-colors ${
                  activeTab === 'timeline'
                    ? 'text-white border-b-2 border-primary'
                    : 'text-white/40 hover:text-white/60'
                }`}
              >
                Timeline
              </button>
              <button
                onClick={() => setActiveTab('characters')}
                className={`flex-1 py-3 text-sm font-medium transition-colors ${
                  activeTab === 'characters'
                    ? 'text-white border-b-2 border-primary'
                    : 'text-white/40 hover:text-white/60'
                }`}
              >
                Characters
              </button>
              <button
                onClick={() => setActiveTab('logs')}
                className={`px-3 py-3 text-sm font-medium transition-colors ${
                  activeTab === 'logs'
                    ? 'text-white border-b-2 border-primary'
                    : 'text-white/40 hover:text-white/60'
                }`}
              >
                Logs
              </button>
            </div>
            <div className="flex-1 overflow-y-auto scrollbar-thin">
              {activeTab === 'timeline' ? (
                <TimelinePanel project={project} onUpdate={setProject} />
              ) : activeTab === 'characters' ? (
                <CharacterPanel project={project} onUpdate={setProject} />
              ) : (
                <div className="p-2">
                  <StatusLog logs={logs} />
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

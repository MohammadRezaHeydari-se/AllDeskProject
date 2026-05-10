'use client'

import { useState } from 'react'
import { api } from '@/api/client'
import type { Project, ExportFormat, RenderQuality } from '@/types'

interface Props {
  project: Project
  onLog?: (message: string, type?: 'info' | 'success' | 'error' | 'warning') => void
}

export function ExportButton({ project, onLog }: Props) {
  const [open, setOpen] = useState(false)
  const [format, setFormat] = useState<ExportFormat>('horizontal')
  const [quality, setQuality] = useState<RenderQuality>('high')
  const [subtitles, setSubtitles] = useState(true)
  const [exporting, setExporting] = useState(false)
  const [progress, setProgress] = useState(0)
  const [status, setStatus] = useState<string | null>(null)

  const handleExport = async () => {
    setExporting(true)
    setProgress(0)
    setStatus('Starting render...')
    onLog?.('Starting export...', 'info')
    try {
      const result = await api.exportScene(project.id, format, subtitles, quality)
      onLog?.(`Render job started (ID: ${result.render_id.slice(0, 8)}...)`, 'info')
      setStatus('Rendering...')

      const poll = setInterval(async () => {
        try {
          const rs = await api.renderStatus(result.render_id)
          if (rs.progress !== undefined) {
            setProgress(rs.progress)
            if (rs.progress % 25 === 0) {
              onLog?.(`Rendering... ${rs.progress}%`, 'info')
            }
          }
          if (rs.status === 'completed') {
            clearInterval(poll)
            setProgress(100)
            setStatus('Export completed!')
            onLog?.('Export completed successfully', 'success')
            setExporting(false)
          } else if (rs.status === 'failed') {
            clearInterval(poll)
            const errMsg = rs.error || 'Unknown error'
            setStatus(`Failed: ${errMsg}`)
            onLog?.(`Export failed: ${errMsg}`, 'error')
            setExporting(false)
          }
        } catch {
          clearInterval(poll)
          setStatus('Error checking status')
          onLog?.('Error polling render status', 'error')
          setExporting(false)
        }
      }, 500)
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err)
      setStatus(`Export failed: ${msg}`)
      onLog?.(`Export failed: ${msg}`, 'error')
      setExporting(false)
    }
  }

  return (
    <div className="relative">
      <button
        onClick={() => setOpen(!open)}
        disabled={exporting}
        className="px-4 py-1.5 bg-primary hover:bg-primary-hover text-white text-sm font-medium rounded-lg transition-colors disabled:opacity-50"
      >
        {exporting ? 'Exporting...' : 'Export'}
      </button>

      {open && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setOpen(false)} />
          <div className="absolute right-0 top-10 w-80 bg-surface border border-white/10 rounded-xl shadow-2xl z-50 p-4 space-y-4">
            <h3 className="text-sm font-medium text-white">Export Scene</h3>

            <div className="space-y-2">
              <label className="text-xs text-white/50 block">Format</label>
              <div className="grid grid-cols-3 gap-2">
                {(['horizontal', 'vertical', 'both'] as ExportFormat[]).map(f => (
                  <button
                    key={f}
                    onClick={() => setFormat(f)}
                    className={`px-3 py-2 text-xs rounded-lg border transition-colors ${
                      format === f
                        ? 'border-primary bg-primary/10 text-white'
                        : 'border-white/10 text-white/50 hover:border-white/20'
                    }`}
                  >
                    {f === 'horizontal' ? '16:9' : f === 'vertical' ? '9:16' : 'Both'}
                  </button>
                ))}
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-xs text-white/50 block">Quality</label>
              <div className="grid grid-cols-3 gap-2">
                {(['high', 'medium', 'low'] as RenderQuality[]).map(q => (
                  <button
                    key={q}
                    onClick={() => setQuality(q)}
                    className={`px-3 py-2 text-xs rounded-lg border transition-colors ${
                      quality === q
                        ? 'border-primary bg-primary/10 text-white'
                        : 'border-white/10 text-white/50 hover:border-white/20'
                    }`}
                  >
                    {q.charAt(0).toUpperCase() + q.slice(1)}
                  </button>
                ))}
              </div>
            </div>

            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={subtitles}
                onChange={e => setSubtitles(e.target.checked)}
                className="rounded border-white/20 bg-surface-alt"
              />
              <span className="text-xs text-white/70">Include subtitles</span>
            </label>

            <button
              onClick={handleExport}
              disabled={exporting}
              className="w-full py-2 bg-primary hover:bg-primary-hover text-white text-sm font-medium rounded-lg transition-colors disabled:opacity-50"
            >
              {exporting ? `Rendering ${progress}%` : 'Start Export'}
            </button>

            {exporting && (
              <div className="space-y-1">
                <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-primary rounded-full transition-all duration-300"
                    style={{ width: `${progress}%` }}
                  />
                </div>
                <p className="text-xs text-white/40 text-right">{progress}%</p>
              </div>
            )}

            {status && !exporting && (
              <p className="text-xs text-white/40 text-center">{status}</p>
            )}
          </div>
        </>
      )}
    </div>
  )
}

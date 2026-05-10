'use client'

import { useEffect, useRef } from 'react'

export interface LogEntry {
  id: number
  time: string
  message: string
  type: 'info' | 'success' | 'error' | 'warning'
}

interface Props {
  logs: LogEntry[]
}

export function StatusLog({ logs }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [logs.length])

  const colors = {
    info: 'text-blue-400',
    success: 'text-green-400',
    error: 'text-red-400',
    warning: 'text-yellow-400',
  }

  const icons = {
    info: 'ℹ',
    success: '✓',
    error: '✗',
    warning: '⚠',
  }

  return (
    <div className="bg-[#0a0b1a] rounded-lg border border-white/5 overflow-hidden">
      <div className="px-3 py-2 border-b border-white/5 flex items-center gap-2">
        <div className="w-2 h-2 rounded-full bg-green-400" />
        <span className="text-xs font-medium text-white/60">Status Log</span>
        <span className="text-[10px] text-white/30 ml-auto">{logs.length} entries</span>
      </div>
      <div className="h-48 overflow-y-auto p-2 font-mono text-[11px] leading-relaxed scrollbar-thin">
        {logs.length === 0 ? (
          <p className="text-white/20 text-center pt-16">No activity yet</p>
        ) : (
          logs.map(entry => (
            <div key={entry.id} className="flex gap-2 py-0.5">
              <span className="text-white/20 shrink-0 w-[60px]">{entry.time}</span>
              <span className={colors[entry.type] + ' shrink-0'}>{icons[entry.type]}</span>
              <span className="text-white/70 break-all">{entry.message}</span>
            </div>
          ))
        )}
        <div ref={bottomRef} />
      </div>
    </div>
  )
}

let logId = 0

export function createLogEntry(message: string, type: LogEntry['type'] = 'info'): LogEntry {
  const now = new Date()
  const time = now.toLocaleTimeString('en-US', { hour12: false })
  return { id: ++logId, time, message, type }
}

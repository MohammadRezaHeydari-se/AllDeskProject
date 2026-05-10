'use client'

import { useEffect, useRef, useState, useCallback } from 'react'
import { api } from '@/api/client'
import type { Project, SceneManifest, TimelineClip } from '@/types'

const API_HOST = process.env.NEXT_PUBLIC_API_URL?.replace('/api', '') || 'http://localhost:8001'

export function ScenePreview({ project }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [manifest, setManifest] = useState<SceneManifest | null>(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const animRef = useRef<number>(0)
  const startTimeRef = useRef<number>(0)
  const charactersRef = useRef<Map<string, HTMLImageElement>>(new Map())
  const backgroundRef = useRef<HTMLImageElement | null>(null)
  const activeClipRef = useRef<TimelineClip | null>(null)

  const charStateRef = useRef<Record<string, {
    blinkTimer: number
    isBlinking: boolean
    blinkFrame: number
    headOffset: number
    mouthOpen: number
  }>>({})

  useEffect(() => {
    api.getManifest(project.id).then(setManifest).catch(console.error)
  }, [project.id])

  useEffect(() => {
    if (!manifest) return

    const loadImages = async () => {
      const loaded = new Map<string, HTMLImageElement>()

      for (const [cid, cdata] of Object.entries(manifest.characters)) {
        if (cdata.image) {
          try {
            const res = await fetch(`${API_HOST}/${cdata.image}`)
            const blob = await res.blob()
            const url = URL.createObjectURL(blob)
            const img = new Image()
            await new Promise<void>((resolve, reject) => {
              img.onload = () => resolve()
              img.onerror = reject
              img.src = url
            })
            loaded.set(cid, img)
          } catch {
            const img = new Image()
            img.src = cdata.image
            loaded.set(cid, img)
          }
        }
      }

      if (manifest.background) {
        try {
          const res = await fetch(`${API_HOST}/${manifest.background}`)
          const blob = await res.blob()
          const url = URL.createObjectURL(blob)
          const bg = new Image()
          await new Promise<void>((resolve, reject) => {
            bg.onload = () => resolve()
            bg.onerror = reject
            bg.src = url
          })
          backgroundRef.current = bg
        } catch {
          const bg = new Image()
          bg.src = manifest.background
          backgroundRef.current = bg
        }
      }

      charactersRef.current = loaded

      for (const cid of Object.keys(manifest.characters)) {
        if (!charStateRef.current[cid]) {
          charStateRef.current[cid] = {
            blinkTimer: Math.floor(Math.random() * 60) + 30,
            isBlinking: false,
            blinkFrame: 0,
            headOffset: 0,
            mouthOpen: 0,
          }
        }
      }
    }

    loadImages()
  }, [manifest])

  const drawFrame = useCallback((time: number) => {
    const canvas = canvasRef.current
    if (!canvas || !manifest) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const { width, height } = canvas
    const fps = manifest.fps
    const frameIdx = Math.floor(time * fps)

    ctx.clearRect(0, 0, width, height)

    if (backgroundRef.current) {
      ctx.drawImage(backgroundRef.current, 0, 0, width, height)
    } else {
      ctx.fillStyle = '#1a1b2e'
      ctx.fillRect(0, 0, width, height)
    }

    let activeClip: TimelineClip | null = null
    for (const clip of manifest.timeline) {
      if (time >= clip.start_time && time < clip.end_time) {
        activeClip = clip
        break
      }
    }
    activeClipRef.current = activeClip

    const charIds = Object.keys(manifest.characters)
    const activeCharId = activeClip?.character_id || null

    for (const cid of charIds) {
      const img = charactersRef.current.get(cid)
      if (!img) continue

      const isActive = cid === activeCharId
      const state = charStateRef.current[cid]
      if (!state) continue

      state.blinkTimer--
      if (state.blinkTimer <= 0 && !state.isBlinking) {
        state.isBlinking = true
        state.blinkFrame = 0
      }
      if (state.isBlinking) {
        state.blinkFrame++
        if (state.blinkFrame > 4) {
          state.isBlinking = false
          state.blinkTimer = Math.floor(Math.random() * 120) + 60
        }
      }

      if (isActive && activeClip) {
        const localFrameIdx = Math.max(0, frameIdx - Math.round(activeClip.start_time * fps))
        const phonemeIdx = Math.min(localFrameIdx, activeClip.phoneme_data.length - 1)
        if (phonemeIdx >= 0) {
          state.mouthOpen = activeClip.phoneme_data[phonemeIdx].mouth_open
          state.headOffset = Math.sin(time * 3.0) * 0.02
        }
      } else {
        state.mouthOpen = 0
        state.headOffset = Math.sin(time * 1.5 + cid.charCodeAt(0)) * 0.01
      }

      const aspect = img.naturalWidth / img.naturalHeight || 1
      let charW = width * 0.22
      let charH = charW / aspect
      if (charH > height * 0.75) {
        charH = height * 0.75
        charW = charH * aspect
      }

      const isLeft = charIds.indexOf(cid) % 2 === 0
      const baseX = isLeft ? width * 0.18 : width * 0.82
      const offsetX = state.headOffset * width
      const x = baseX - charW / 2 + offsetX
      const y = height - charH - height * 0.05

      if (state.isBlinking) {
        const blinkScale = 1 - (state.blinkFrame / 4) * 0.3
        const newH = charH * blinkScale
        ctx.drawImage(img, x, y + (charH - newH), charW, Math.max(newH, 1))
      } else {
        ctx.drawImage(img, x, y, charW, charH)
      }

      if (isActive && activeClip?.subtitle) {
        ctx.font = '24px sans-serif'
        ctx.textAlign = 'center'
        const subX = x + charW / 2
        const subY = y + charH + 30
        ctx.fillStyle = 'rgba(0,0,0,0.6)'
        const tw = ctx.measureText(activeClip.subtitle).width
        ctx.fillRect(subX - tw / 2 - 10, subY - 22, tw + 20, 34)
        ctx.fillStyle = '#ffffff'
        ctx.fillText(activeClip.subtitle, subX, subY)
      }
    }
  }, [manifest])

  const animate = useCallback((timestamp: number) => {
    if (!startTimeRef.current) startTimeRef.current = timestamp
    const elapsed = (timestamp - startTimeRef.current) / 1000

    if (manifest && elapsed < manifest.total_duration) {
      setCurrentTime(elapsed)
      drawFrame(elapsed)
      animRef.current = requestAnimationFrame(animate)
    } else {
      setIsPlaying(false)
      if (manifest) drawFrame(manifest.total_duration)
    }
  }, [manifest, drawFrame])

  useEffect(() => {
    if (isPlaying) {
      startTimeRef.current = 0
      animRef.current = requestAnimationFrame(animate)
    }
    return () => cancelAnimationFrame(animRef.current)
  }, [isPlaying, animate])

  const handlePlayPause = () => {
    if (isPlaying) {
      setIsPlaying(false)
      cancelAnimationFrame(animRef.current)
    } else {
      if (!startTimeRef.current || (manifest && currentTime >= manifest.total_duration)) {
        startTimeRef.current = 0
        setCurrentTime(0)
      }
      setIsPlaying(true)
    }
  }

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const time = parseFloat(e.target.value)
    setCurrentTime(time)
    startTimeRef.current = 0
    drawFrame(time)
  }

  if (!manifest) {
    return (
      <div className="flex-1 flex items-center justify-center bg-surface-alt/50">
        <p className="text-sm text-white/30">Generate scene to see preview</p>
      </div>
    )
  }

  const progress = manifest.total_duration > 0 ? (currentTime / manifest.total_duration) * 100 : 0

  return (
    <div className="flex-1 flex flex-col items-center justify-center p-6 bg-[#0a0b1a]">
      <canvas
        ref={canvasRef}
        width={854}
        height={480}
        className="rounded-xl border border-white/5 shadow-2xl max-w-full"
        style={{ aspectRatio: '854/480' }}
      />

      <div className="w-full max-w-[854px] mt-4 px-2 space-y-2">
        <div className="relative">
          <input
            type="range"
            min={0}
            max={manifest.total_duration}
            step={0.01}
            value={currentTime}
            onChange={handleSeek}
            className="w-full h-1.5 bg-white/10 rounded-full appearance-none cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-3 [&::-webkit-slider-thumb]:h-3 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-primary"
          />
          <div className="absolute top-0 left-0 h-full rounded-full bg-primary/30 pointer-events-none" style={{ width: `${progress}%` }} />
        </div>

        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              onClick={handlePlayPause}
              className="w-8 h-8 rounded-full bg-primary hover:bg-primary-hover flex items-center justify-center transition-colors"
            >
              {isPlaying ? (
                <svg className="w-3.5 h-3.5 text-white" fill="currentColor" viewBox="0 0 24 24">
                  <rect x="6" y="4" width="4" height="16" />
                  <rect x="14" y="4" width="4" height="16" />
                </svg>
              ) : (
                <svg className="w-3.5 h-3.5 text-white ml-0.5" fill="currentColor" viewBox="0 0 24 24">
                  <polygon points="5,3 19,12 5,21" />
                </svg>
              )}
            </button>
            <span className="text-xs text-white/40 font-mono">
              {currentTime.toFixed(1)}s / {manifest.total_duration.toFixed(1)}s
            </span>
          </div>

          {activeClipRef.current && (
            <div className="flex items-center gap-2">
              <div
                className="w-2 h-2 rounded-full"
                style={{
                  backgroundColor: manifest.characters[activeClipRef.current.character_id]?.color || '#666'
                }}
              />
              <span className="text-xs text-white/50">
                {manifest.characters[activeClipRef.current.character_id]?.name || 'Unknown'}
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

import { useState, useEffect, useRef } from 'react'
import type { SceneManifest } from '@/types'

interface Props {
  manifest: SceneManifest
}

export function SceneComposition({ manifest }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [time, setTime] = useState(0)
  const [playing, setPlaying] = useState(false)
  const animRef = useRef<number>(0)

  useEffect(() => {
    if (!playing) return
    let start = performance.now()
    const animate = (now: number) => {
      const elapsed = (now - start) / 1000
      if (elapsed >= manifest.total_duration) {
        setPlaying(false)
        drawFrame(manifest.total_duration)
        return
      }
      setTime(elapsed)
      drawFrame(elapsed)
      animRef.current = requestAnimationFrame(animate)
    }
    animRef.current = requestAnimationFrame(animate)
    return () => cancelAnimationFrame(animRef.current)
  }, [playing, manifest])

  const drawFrame = (t: number) => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const { width, height } = canvas
    const fps = manifest.fps
    const frameIdx = Math.floor(t * fps)

    ctx.fillStyle = '#1a1b2e'
    ctx.fillRect(0, 0, width, height)

    let activeClip = manifest.timeline.find(
      c => t >= c.start_time && t < c.end_time
    ) || null

    const charIds = Object.keys(manifest.characters)
    for (const cid of charIds) {
      const cdata = manifest.characters[cid]
      const isActive = cid === activeClip?.character_id
      const isLeft = charIds.indexOf(cid) % 2 === 0

      const charW = width * 0.2
      const charH = height * 0.6
      const baseX = isLeft ? width * 0.2 : width * 0.8
      const headBob = Math.sin(t * (isActive ? 3 : 1.5)) * 5
      const x = baseX - charW / 2 + headBob
      const y = height - charH - height * 0.05

      ctx.fillStyle = cdata.color + '40'
      ctx.beginPath()
      ctx.roundRect(x, y, charW, charH, 12)
      ctx.fill()

      ctx.fillStyle = cdata.color
      ctx.font = '16px sans-serif'
      ctx.textAlign = 'center'
      ctx.fillText(cdata.name, x + charW / 2, y - 10)

      const mouthOpen = isActive && activeClip
        ? (activeClip.phoneme_data[Math.min(frameIdx, activeClip.phoneme_data.length - 1)]?.mouth_open || 0)
        : 0

      const blink = Math.sin(t * 2) > 0.95 ? 1 : 0
      const eyeY = y + charH * 0.25
      const eyeOffset = charW * 0.15

      ctx.fillStyle = '#222'
      ctx.beginPath()
      ctx.arc(x + charW / 2 - eyeOffset, eyeY, 6 * (1 - blink * 0.5), 0, Math.PI * 2)
      ctx.fill()
      ctx.beginPath()
      ctx.arc(x + charW / 2 + eyeOffset, eyeY, 6 * (1 - blink * 0.5), 0, Math.PI * 2)
      ctx.fill()

      if (mouthOpen > 0.1) {
        const mouthH = mouthOpen * 20
        ctx.fillStyle = '#333'
        ctx.beginPath()
        ctx.ellipse(x + charW / 2, y + charH * 0.45, 10, mouthH / 2, 0, 0, Math.PI * 2)
        ctx.fill()
      }

      if (isActive && activeClip?.subtitle) {
        ctx.font = '14px sans-serif'
        ctx.textAlign = 'center'
        ctx.fillStyle = 'rgba(0,0,0,0.7)'
        const sw = ctx.measureText(activeClip.subtitle).width
        ctx.fillRect(x + charW / 2 - sw / 2 - 8, y + charH + 10, sw + 16, 26)
        ctx.fillStyle = '#fff'
        ctx.fillText(activeClip.subtitle, x + charW / 2, y + charH + 28)
      }
    }

    ctx.fillStyle = 'rgba(255,255,255,0.3)'
    ctx.font = '12px monospace'
    ctx.textAlign = 'left'
    ctx.fillText(`${t.toFixed(1)}s / ${manifest.total_duration.toFixed(1)}s`, 10, 20)
  }

  return (
    <div className="flex flex-col items-center gap-4">
      <canvas
        ref={canvasRef}
        width={854}
        height={480}
        className="rounded-lg border border-white/10"
      />
      <div className="flex items-center gap-4">
        <button
          onClick={() => setPlaying(!playing)}
          className="px-4 py-2 bg-primary text-white text-sm rounded-lg hover:bg-primary-hover"
        >
          {playing ? 'Pause' : 'Play'}
        </button>
        <span className="text-sm text-white/50">
          {time.toFixed(1)}s
        </span>
      </div>
    </div>
  )
}

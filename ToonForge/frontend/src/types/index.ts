export interface Character {
  id: string
  name: string
  image_path: string
  color: string
  is_active: boolean
}

export interface AudioClip {
  id: string
  filename: string
  filepath: string
  character_id: string | null
  duration: number
  amplitude_data: number[] | null
  order: number
  subtitle: string | null
}

export interface SceneClip {
  audio_id: string
  character_id: string
  order: number
  subtitle: string | null
}

export interface SceneConfig {
  id: string
  name: string
  background_path: string | null
  clips: SceneClip[]
  width: number
  height: number
  fps: number
  total_duration: number
}

export interface Project {
  id: string
  name: string
  characters: Character[]
  audio_clips: AudioClip[]
  scene: SceneConfig | null
}

export interface MappingOverride {
  audio_id: string
  character_id: string
  order: number
  subtitle: string | null
}

export interface PhonemeFrame {
  amplitude: number
  mouth_open: number
  energy: number
}

export interface TimelineClip {
  audio_id: string
  audio_file: string
  audio_duration: number
  character_id: string
  start_time: number
  end_time: number
  order: number
  subtitle: string
  phoneme_data: PhonemeFrame[]
}

export interface SceneManifest {
  project_id: string
  project_name: string
  width: number
  height: number
  fps: number
  background: string | null
  total_duration: number
  characters: Record<string, {
    name: string
    image: string
    color: string
  }>
  timeline: TimelineClip[]
}

export type ExportFormat = 'horizontal' | 'vertical' | 'both'
export type RenderQuality = 'high' | 'medium' | 'low'

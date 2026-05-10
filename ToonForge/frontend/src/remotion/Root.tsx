import { SceneComposition } from './SceneComposition'
import type { SceneManifest } from '@/types'

const manifest: SceneManifest = {
  project_id: 'demo',
  project_name: 'Demo Scene',
  width: 1920,
  height: 1080,
  fps: 30,
  background: null,
  total_duration: 10,
  characters: {
    char_a: { name: 'Character A', image: '', color: '#6c5ce7' },
    char_b: { name: 'Character B', image: '', color: '#00cec9' },
  },
  timeline: [
    {
      audio_id: 'a1',
      audio_file: '',
      audio_duration: 5,
      character_id: 'char_a',
      start_time: 0,
      end_time: 5,
      order: 0,
      subtitle: 'Hello, how are you?',
      phoneme_data: Array.from({ length: 150 }, (_, i) => ({
        amplitude: Math.abs(Math.sin(i * 0.1)),
        mouth_open: Math.abs(Math.sin(i * 0.15)),
        energy: Math.random() * 100,
      })),
    },
    {
      audio_id: 'a2',
      audio_file: '',
      audio_duration: 5,
      character_id: 'char_b',
      start_time: 5,
      end_time: 10,
      order: 1,
      subtitle: "I'm doing great, thanks!",
      phoneme_data: Array.from({ length: 150 }, (_, i) => ({
        amplitude: Math.abs(Math.sin(i * 0.12)),
        mouth_open: Math.abs(Math.sin(i * 0.18)),
        energy: Math.random() * 100,
      })),
    },
  ],
}

export default function RemotionRoot() {
  return <SceneComposition manifest={manifest} />
}

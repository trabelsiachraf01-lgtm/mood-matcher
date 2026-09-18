import { useEffect, useRef, useState } from 'react'
import { PauseIcon, PlayIcon, WaveformIcon } from './icons'
import type { NowPlaying } from '../api/types'

interface NowPlayingBarProps {
  nowPlaying: NowPlaying
  isGenerating?: boolean
}

function formatTime(seconds: number): string {
  if (!Number.isFinite(seconds)) return '0:00'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

export function NowPlayingBar({ nowPlaying, isGenerating }: NowPlayingBarProps) {
  const audioRef = useRef<HTMLAudioElement>(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)

  // The `key={assetUrl}` on this component in App.tsx remounts it (and resets all state
  // above) on a new track — this effect only needs to handle the actual side effect:
  // starting playback, like background music picking up as soon as the result is in.
  useEffect(() => {
    void audioRef.current?.play()
  }, [])

  function togglePlayback() {
    const audio = audioRef.current
    if (!audio) return
    if (isPlaying) {
      audio.pause()
    } else {
      void audio.play()
    }
  }

  function seekBy(seconds: number) {
    const audio = audioRef.current
    if (!audio) return
    audio.currentTime = Math.min(Math.max(audio.currentTime + seconds, 0), duration || Infinity)
  }

  const progressPercent = duration > 0 ? (currentTime / duration) * 100 : 0

  return (
    <div className="flex w-full items-center gap-4 bg-ink px-6 py-4">
      <audio
        ref={audioRef}
        src={nowPlaying.assetUrl || undefined}
        preload="metadata"
        onPlay={() => setIsPlaying(true)}
        onPause={() => setIsPlaying(false)}
        onEnded={() => setIsPlaying(false)}
        onTimeUpdate={(e) => setCurrentTime(e.currentTarget.currentTime)}
        onLoadedMetadata={(e) => setDuration(e.currentTarget.duration)}
      />

      <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-lg bg-teal-bg">
        <WaveformIcon className="h-5 w-5 text-teal-fg" />
      </div>

      <div className="min-w-0">
        <p className="font-mono text-[11px] uppercase tracking-wide text-teal-fg">
          {isGenerating ? 'Generating…' : 'Now playing'}
        </p>
        <p className="truncate font-body text-sm text-white/90">
          {isGenerating ? 'ElevenLabs is composing your track' : `${nowPlaying.title} · ${nowPlaying.album}`}
        </p>
      </div>

      <div className="flex shrink-0 items-center gap-2">
        <button
          type="button"
          onClick={() => seekBy(-10)}
          disabled={!nowPlaying.assetUrl}
          aria-label="Back 10 seconds"
          className="flex h-8 w-8 items-center justify-center rounded-full text-white/70 hover:text-white disabled:opacity-40"
        >
          <span className="font-mono text-[10px]">−10</span>
        </button>

        <button
          type="button"
          onClick={togglePlayback}
          disabled={!nowPlaying.assetUrl}
          aria-label={isPlaying ? 'Pause' : 'Play'}
          className="flex h-9 w-9 items-center justify-center rounded-full bg-teal-fg text-teal-bg disabled:opacity-40"
        >
          {isPlaying ? <PauseIcon className="h-4 w-4" /> : <PlayIcon className="h-4 w-4" />}
        </button>

        <button
          type="button"
          onClick={() => seekBy(10)}
          disabled={!nowPlaying.assetUrl}
          aria-label="Forward 10 seconds"
          className="flex h-8 w-8 items-center justify-center rounded-full text-white/70 hover:text-white disabled:opacity-40"
        >
          <span className="font-mono text-[10px]">+10</span>
        </button>
      </div>

      <div className="hidden flex-1 items-center gap-2 sm:flex">
        <span className="font-mono text-xs text-white/60">{formatTime(currentTime)}</span>
        <div className="h-1 flex-1 rounded-full bg-white/15">
          <div className="h-1 rounded-full bg-teal-fg" style={{ width: `${progressPercent}%` }} />
        </div>
        <span className="font-mono text-xs text-white/60">{formatTime(duration)}</span>
      </div>

      <span className="hidden shrink-0 font-mono text-xs text-white/60 sm:inline">
        {nowPlaying.attribution.source} · {nowPlaying.attribution.license}
      </span>
    </div>
  )
}

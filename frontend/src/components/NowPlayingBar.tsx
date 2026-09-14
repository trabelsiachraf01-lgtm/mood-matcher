import { useEffect, useRef, useState } from 'react'
import { PauseIcon, PlayIcon, WaveformIcon } from './icons'
import type { NowPlaying } from '../api/types'

interface NowPlayingBarProps {
  nowPlaying: NowPlaying
}

function formatTime(seconds: number): string {
  if (!Number.isFinite(seconds)) return '0:00'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

export function NowPlayingBar({ nowPlaying }: NowPlayingBarProps) {
  const audioRef = useRef<HTMLAudioElement>(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)

  // A new match means a new track — reset playback state instead of carrying the old one over.
  useEffect(() => {
    setIsPlaying(false)
    setCurrentTime(0)
    setDuration(0)
  }, [nowPlaying.assetUrl])

  function togglePlayback() {
    const audio = audioRef.current
    if (!audio) return
    if (isPlaying) {
      audio.pause()
    } else {
      void audio.play()
    }
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
        <p className="font-mono text-[11px] uppercase tracking-wide text-teal-fg">Now playing</p>
        <p className="truncate font-body text-sm text-white/90">
          {nowPlaying.title} · {nowPlaying.album}
        </p>
      </div>

      <button
        type="button"
        onClick={togglePlayback}
        disabled={!nowPlaying.assetUrl}
        aria-label={isPlaying ? 'Pause' : 'Play'}
        className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-teal-fg text-teal-bg disabled:opacity-40"
      >
        {isPlaying ? <PauseIcon className="h-4 w-4" /> : <PlayIcon className="h-4 w-4" />}
      </button>

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

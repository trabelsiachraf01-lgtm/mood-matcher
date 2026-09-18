import { useEffect, useState } from 'react'

interface ProgressBarProps {
  /** Cycles through these on a timer so a slow request reads as active work, not a freeze. */
  messages: string[]
}

export function ProgressBar({ messages }: ProgressBarProps) {
  const [index, setIndex] = useState(0)

  useEffect(() => {
    const id = setInterval(() => setIndex((i) => (i + 1) % messages.length), 2200)
    return () => clearInterval(id)
  }, [messages])

  return (
    <div>
      <div className="h-1.5 w-full overflow-hidden rounded-full bg-border">
        <div className="h-full w-1/3 rounded-full bg-coral [animation:progress-slide_1.4s_ease-in-out_infinite]" />
      </div>
      <p className="mt-3 text-right font-mono text-xs text-ink-dim">{messages[index]}</p>
    </div>
  )
}

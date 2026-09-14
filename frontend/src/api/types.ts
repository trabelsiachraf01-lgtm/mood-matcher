// Shape of what the wizard sends to / receives from the (future) /suggestions
// backend endpoint. Kept independent of any UI component so the mock client
// and the real client can share these types unchanged.

export type InputMode = 'image' | 'song' | 'text'

export interface SuggestionRequest {
  /** Which of the three Step 1 input modes the user picked. */
  inputMode: InputMode
  /**
   * The raw input value. For `text` this is the mood description; for
   * `song` it's the pasted link; for `image` it would be a file reference
   * (kept as a string placeholder until upload is wired up).
   */
  inputValue: string
  /** Selected mood/style chips from Step 2, e.g. ["Melancholy", "Golden hour"]. */
  moodTags: string[]
  /** Energy slider value from Step 2, 0 (calm) to 100 (energetic). */
  energy: number
}

export type MediaKind = 'image' | 'song'

/** A licensed, attributable real-world match (never AI-generated media). */
export interface Attribution {
  creator: string
  source: string
  license: string
  sourceUrl: string
}

export interface RelatedMatch {
  id: string
  title: string
  creator: string
  kind: MediaKind
}

export interface NowPlaying {
  title: string
  artist: string
  album: string
  currentTimeLabel: string
  durationLabel: string
  /** 0-100 playback progress. */
  progressPercent: number
  attribution: Attribution
}

export interface SuggestionResponse {
  caption: string
  matchedMedia: {
    kind: MediaKind
    label: string
  }
  /** Human-readable echo of the search inputs, e.g. "Melancholy, Golden hour". */
  searchSummary: string
  attribution: Attribution
  relatedMatches: RelatedMatch[]
  nowPlaying: NowPlaying
}

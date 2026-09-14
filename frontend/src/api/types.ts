// Shape of what the wizard sends to / receives from the (future) /suggestions
// backend endpoint. Kept independent of any UI component so the mock client
// and the real client can share these types unchanged.

export type InputMode = 'image' | 'song' | 'text'

export interface SuggestionRequest {
  /** Which of the three Step 1 input modes the user picked. */
  inputMode: InputMode
  /** The mood description, when `inputMode` is `text`. */
  text?: string
  /** The uploaded image or audio file, when `inputMode` is `image` or `song`. */
  file?: File
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
  /** Source/landing page — what "View source" style links point to. */
  url: string
}

export interface NowPlaying {
  title: string
  artist: string
  album: string
  /** Direct, playable audio URL — real playback, not a mock. */
  assetUrl: string
  attribution: Attribution
}

export interface SuggestionResponse {
  caption: string
  matchedMedia: {
    kind: MediaKind
    label: string
    /** Direct, viewable file — the real matched photo, or empty for a song match. */
    assetUrl: string
  }
  /** Human-readable echo of the search inputs, e.g. "Melancholy, Golden hour". */
  searchSummary: string
  attribution: Attribution
  relatedMatches: RelatedMatch[]
  nowPlaying: NowPlaying
}

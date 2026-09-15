// Shape of what the wizard sends to / receives from the (future) /suggestions
// backend endpoint. Kept independent of any UI component so the mock client
// and the real client can share these types unchanged.

export type InputMode = 'image' | 'song' | 'text'

export interface SuggestionRequest {
  /** Which input mode the user picked. */
  inputMode: InputMode
  /** The mood description, when `inputMode` is `text`. */
  text?: string
  /** The uploaded image or audio file, when `inputMode` is `image` or `song`. */
  file?: File
}

export type MediaKind = 'image' | 'song'

/** A licensed, attributable real-world match (never AI-generated media). */
export interface Attribution {
  creator: string
  source: string
  license: string
  sourceUrl: string
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
  attribution: Attribution
  nowPlaying: NowPlaying
}

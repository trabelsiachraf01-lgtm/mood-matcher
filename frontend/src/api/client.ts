import type { SuggestionRequest, SuggestionResponse } from './types'

const MOCK_RESPONSE: SuggestionResponse = {
  caption:
    'A quiet, wistful stretch of empty road at golden hour — the kind of stillness right before dusk.',
  matchedMedia: {
    kind: 'image',
    label: 'Matched image · Empty Highway at Dusk',
  },
  searchSummary: 'Melancholy, Golden hour',
  attribution: {
    creator: 'Mika Torres',
    source: 'Openverse',
    license: 'CC BY 2.0',
    sourceUrl: 'https://openverse.org',
  },
  relatedMatches: [
    { id: 'rm-1', title: 'Dust and Distance', creator: 'Priya Nair', kind: 'image' },
    { id: 'rm-2', title: 'Amber Fields', creator: 'Solene Voss', kind: 'song' },
    { id: 'rm-3', title: 'Low Static, High Sky', creator: 'Reverie Thread', kind: 'song' },
    { id: 'rm-4', title: 'Golden Hour, Two-Lane Road', creator: 'Callum Ash', kind: 'image' },
  ],
  nowPlaying: {
    title: 'Wandering Static',
    artist: 'Loft & Rye',
    album: 'Loft & Rye',
    currentTimeLabel: '1:02',
    durationLabel: '2:41',
    progressPercent: 38,
    attribution: {
      creator: 'Loft & Rye',
      source: 'Jamendo',
      license: 'CC BY-NC 4.0',
      sourceUrl: 'https://jamendo.com',
    },
  },
}

/**
 * Fetches a cross-modal mood match for the given request.
 *
 * There is no `/suggestions` backend yet — this resolves to fixed mock data
 * after a short artificial delay so loading states are visible in the UI.
 * Every caller should treat this as the real network boundary; swapping in
 * `fetch('/suggestions', { method: 'POST', body: JSON.stringify(request) })`
 * later is a change confined to this file.
 */
export async function getSuggestion(request: SuggestionRequest): Promise<SuggestionResponse> {
  void request
  await new Promise((resolve) => setTimeout(resolve, 900))
  return MOCK_RESPONSE
}

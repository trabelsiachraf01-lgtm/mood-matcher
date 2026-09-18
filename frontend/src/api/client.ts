import type { SuggestionRequest, SuggestionResponse } from './types'

const API_BASE_URL = 'http://localhost:8000'

/**
 * Fetches a cross-modal mood match for the given request from the real backend
 * (src/api/app.py), matched against the real pgvector catalog. Sent as
 * multipart form data — text mode sends `text`, image/song mode sends `file`.
 */
export async function getSuggestion(request: SuggestionRequest): Promise<SuggestionResponse> {
  const form = new FormData()
  form.set('inputMode', request.inputMode)
  if (request.text) form.set('text', request.text)
  if (request.file) form.set('file', request.file)
  if (request.songSource) form.set('songSource', request.songSource)

  const response = await fetch(`${API_BASE_URL}/suggestions`, {
    method: 'POST',
    body: form,
  })

  if (!response.ok) {
    throw new Error(`Suggestion request failed: ${response.status} ${response.statusText}`)
  }

  return response.json() as Promise<SuggestionResponse>
}

/**
 * Generates a short original track for the given mood caption via ElevenLabs Music
 * (src/api/app.py `/generate-music`) — opt-in, not part of the catalog match above.
 */
export async function generateMusic(prompt: string): Promise<Blob> {
  const form = new FormData()
  form.set('prompt', prompt)

  const response = await fetch(`${API_BASE_URL}/generate-music`, {
    method: 'POST',
    body: form,
  })

  if (!response.ok) {
    throw new Error(`Music generation failed: ${response.status} ${response.statusText}`)
  }

  return response.blob()
}

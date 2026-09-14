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
  form.set('moodTags', request.moodTags.join(','))
  form.set('energy', String(request.energy))
  if (request.text) form.set('text', request.text)
  if (request.file) form.set('file', request.file)

  const response = await fetch(`${API_BASE_URL}/suggestions`, {
    method: 'POST',
    body: form,
  })

  if (!response.ok) {
    throw new Error(`Suggestion request failed: ${response.status} ${response.statusText}`)
  }

  return response.json() as Promise<SuggestionResponse>
}

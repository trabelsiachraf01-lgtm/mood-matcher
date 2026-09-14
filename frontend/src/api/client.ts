import type { SuggestionRequest, SuggestionResponse } from './types'

const API_BASE_URL = 'http://localhost:8000'

/**
 * Fetches a cross-modal mood match for the given request from the real backend
 * (src/api/app.py). That backend currently matches against a 2-item in-memory
 * catalog — one image, one placeholder song — since the real ingestion
 * pipeline doesn't exist yet; captioning and embedding themselves are real.
 */
export async function getSuggestion(request: SuggestionRequest): Promise<SuggestionResponse> {
  const response = await fetch(`${API_BASE_URL}/suggestions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  })

  if (!response.ok) {
    throw new Error(`Suggestion request failed: ${response.status} ${response.statusText}`)
  }

  return response.json() as Promise<SuggestionResponse>
}

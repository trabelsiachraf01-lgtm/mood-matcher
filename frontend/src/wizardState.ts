import type { InputMode } from './api/types'

export interface WizardState {
  inputMode: InputMode
  text: string
  file: File | null
  moodTags: string[]
  energy: number
}

export const INITIAL_MOOD_TAGS = ['Melancholy', 'Golden hour', 'Nostalgic', 'Chill', 'Cinematic', 'Lo-fi']

export const initialWizardState: WizardState = {
  inputMode: 'text',
  text: 'golden hour, empty highway, a little wistful',
  file: null,
  moodTags: ['Melancholy', 'Golden hour'],
  energy: 32,
}

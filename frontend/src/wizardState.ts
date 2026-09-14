import type { InputMode } from './api/types'

export interface WizardState {
  inputMode: InputMode
  inputValue: string
  moodTags: string[]
  energy: number
}

export const INITIAL_MOOD_TAGS = ['Melancholy', 'Golden hour', 'Nostalgic', 'Chill', 'Cinematic', 'Lo-fi']

export const initialWizardState: WizardState = {
  inputMode: 'text',
  inputValue: 'golden hour, empty highway, a little wistful',
  moodTags: ['Melancholy', 'Golden hour'],
  energy: 32,
}

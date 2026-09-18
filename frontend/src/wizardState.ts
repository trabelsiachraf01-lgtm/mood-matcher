import type { InputMode, SongSource } from './api/types'

export interface WizardState {
  inputMode: InputMode
  text: string
  file: File | null
  songSource: SongSource
}

export const initialWizardState: WizardState = {
  inputMode: 'text',
  text: 'golden hour, empty highway, a little wistful',
  file: null,
  songSource: 'catalog',
}

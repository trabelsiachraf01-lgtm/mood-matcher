import type { InputMode } from './api/types'

export interface WizardState {
  inputMode: InputMode
  text: string
  file: File | null
}

export const initialWizardState: WizardState = {
  inputMode: 'text',
  text: 'golden hour, empty highway, a little wistful',
  file: null,
}

import { useState } from 'react'
import { getSuggestion } from './api/client'
import type { SuggestionResponse } from './api/types'
import { Header } from './components/Header'
import { NowPlayingBar } from './components/NowPlayingBar'
import { StepInput } from './steps/StepInput'
import { StepPreferences } from './steps/StepPreferences'
import { StepResults } from './steps/StepResults'
import { initialWizardState, type WizardState } from './wizardState'

type Step = 1 | 2 | 3

function App() {
  const [step, setStep] = useState<Step>(1)
  const [wizardState, setWizardState] = useState<WizardState>(initialWizardState)
  const [result, setResult] = useState<SuggestionResponse | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  function updateWizardState(patch: Partial<WizardState>) {
    setWizardState((prev) => ({ ...prev, ...patch }))
  }

  async function handleSubmit() {
    setIsLoading(true)
    try {
      const response = await getSuggestion({
        inputMode: wizardState.inputMode,
        text: wizardState.text,
        file: wizardState.file ?? undefined,
        moodTags: wizardState.moodTags,
        energy: wizardState.energy,
      })
      setResult(response)
      setStep(3)
    } finally {
      setIsLoading(false)
    }
  }

  function handleBackToSearch() {
    setResult(null)
    setStep(1)
  }

  return (
    <div className="flex min-h-screen flex-col bg-bg">
      <div className="mx-auto w-full max-w-2xl flex-1 px-4 pb-16">
        <Header currentStep={step} />

        {step === 1 && (
          <StepInput
            state={wizardState}
            onChange={updateWizardState}
            onContinue={() => setStep(2)}
          />
        )}

        {step === 2 && (
          <StepPreferences
            state={wizardState}
            onChange={updateWizardState}
            onBack={() => setStep(1)}
            onContinue={handleSubmit}
          />
        )}

        {step === 2 && isLoading && (
          <p className="mt-6 font-mono text-xs uppercase tracking-wide text-ink-dim">
            Finding your match…
          </p>
        )}

        {step === 3 && result && <StepResults result={result} onBack={handleBackToSearch} />}
      </div>

      {step === 3 && result && (
        <div className="sticky bottom-0 w-full">
          <NowPlayingBar nowPlaying={result.nowPlaying} />
        </div>
      )}
    </div>
  )
}

export default App

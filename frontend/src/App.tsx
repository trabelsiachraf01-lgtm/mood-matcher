import { useState } from 'react'
import { getSuggestion } from './api/client'
import type { SuggestionResponse } from './api/types'
import { Header } from './components/Header'
import { NowPlayingBar } from './components/NowPlayingBar'
import { StepInput } from './steps/StepInput'
import { StepResults } from './steps/StepResults'
import { initialWizardState, type WizardState } from './wizardState'

type Step = 1 | 2

function App() {
  const [step, setStep] = useState<Step>(1)
  const [wizardState, setWizardState] = useState<WizardState>(initialWizardState)
  const [result, setResult] = useState<SuggestionResponse | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  function updateWizardState(patch: Partial<WizardState>) {
    setWizardState((prev) => ({ ...prev, ...patch }))
  }

  async function handleSubmit() {
    setIsLoading(true)
    setError(null)
    try {
      const response = await getSuggestion({
        inputMode: wizardState.inputMode,
        text: wizardState.text,
        file: wizardState.file ?? undefined,
      })
      setResult(response)
      setStep(2)
    } catch {
      setError('Could not find a match — check the backend is running and try again.')
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
            onContinue={handleSubmit}
            isLoading={isLoading}
            error={error}
          />
        )}

        {step === 2 && result && <StepResults result={result} onBack={handleBackToSearch} />}
      </div>

      {step === 2 && result && (
        <div className="sticky bottom-0 w-full">
          <NowPlayingBar nowPlaying={result.nowPlaying} />
        </div>
      )}
    </div>
  )
}

export default App

import { useRef, useState } from 'react'
import { generateMusic, getSuggestion } from './api/client'
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
  const [isGeneratingMusic, setIsGeneratingMusic] = useState(false)
  const [generateError, setGenerateError] = useState<string | null>(null)
  const generatedUrlRef = useRef<string | null>(null)

  function updateWizardState(patch: Partial<WizardState>) {
    setWizardState((prev) => ({ ...prev, ...patch }))
  }

  async function withGeneratedSong(current: SuggestionResponse): Promise<SuggestionResponse> {
    const blob = await generateMusic(current.caption)
    if (generatedUrlRef.current) URL.revokeObjectURL(generatedUrlRef.current)
    const assetUrl = URL.createObjectURL(blob)
    generatedUrlRef.current = assetUrl
    return {
      ...current,
      nowPlaying: {
        title: 'Generated for this mood',
        artist: 'Eleven Music',
        album: 'AI-generated, not from the catalog',
        assetUrl,
        attribution: { creator: 'Eleven Music', source: 'ElevenLabs', license: 'AI-generated', sourceUrl: 'https://elevenlabs.io/music' },
      },
    }
  }

  async function handleSubmit() {
    setIsLoading(true)
    setError(null)
    try {
      const response = await getSuggestion({
        inputMode: wizardState.inputMode,
        text: wizardState.text,
        file: wizardState.file ?? undefined,
        songSource: wizardState.songSource,
      })
      // songSource=generate told the backend to skip the catalog lookup entirely (see
      // suggestion_service.py) — wait for the real track before showing step 2 at all,
      // instead of landing on a "generating…" placeholder the user didn't ask to see.
      const finalResult = wizardState.songSource === 'generate' ? await withGeneratedSong(response) : response
      setResult(finalResult)
      setStep(2)
    } catch {
      setError(
        wizardState.songSource === 'generate'
          ? 'Could not generate a track — check the backend and ELEVENLABS_API_KEY.'
          : 'Could not find a match — check the backend is running and try again.',
      )
    } finally {
      setIsLoading(false)
    }
  }

  function handleBackToSearch() {
    setResult(null)
    setStep(1)
  }

  async function handleGenerateMusic() {
    if (!result) return
    setIsGeneratingMusic(true)
    setGenerateError(null)
    try {
      setResult(await withGeneratedSong(result))
    } catch {
      setGenerateError('Could not generate a track — check the backend and ELEVENLABS_API_KEY.')
    } finally {
      setIsGeneratingMusic(false)
    }
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

        {step === 2 && result && (
          <StepResults
            result={result}
            onBack={handleBackToSearch}
            songSource={wizardState.songSource}
            onGenerateMusic={handleGenerateMusic}
            isGeneratingMusic={isGeneratingMusic}
            generateError={generateError}
          />
        )}
      </div>

      {step === 2 && result && (
        <div className="sticky bottom-0 w-full">
          <NowPlayingBar
            key={result.nowPlaying.assetUrl}
            nowPlaying={result.nowPlaying}
            isGenerating={isGeneratingMusic}
          />
        </div>
      )}
    </div>
  )
}

export default App

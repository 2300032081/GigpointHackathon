import { useCallback, useEffect, useRef, useState } from 'react'

const browserError = (code) => ({
  'not-allowed': 'Microphone permission was denied. Please allow microphone access in your browser settings.',
  'service-not-allowed': 'Microphone permission is required.',
  'no-speech': 'No speech was detected. Please try again.',
  'audio-capture': 'No microphone was detected.',
  network: 'Speech recognition network error. Please try again.',
  aborted: 'Voice input was stopped.'
}[code] || 'Voice recognition failed. Please try again.')

export function useSpeechRecognition(languageOrOptions = 'en-IN') {
  const language = typeof languageOrOptions === 'string' ? languageOrOptions : languageOrOptions.language
  const recognitionRef = useRef(null)
  const listeningRef = useRef(false)
  const [browserSupported, setBrowserSupported] = useState(false)
  const [transcript, setTranscript] = useState('')
  const [interimTranscript, setInterimTranscript] = useState('')
  const [isListening, setIsListening] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition
    if (!Recognition) return undefined
    setBrowserSupported(true)
    const recognition = new Recognition()
    recognition.continuous = false
    recognition.interimResults = true
    recognition.lang = language || 'en-IN'
    recognition.onstart = () => { listeningRef.current = true; setIsListening(true); setError('') }
    recognition.onresult = (event) => {
      let finalText = ''
      let interimText = ''
      for (let index = event.resultIndex; index < event.results.length; index += 1) {
        const value = event.results[index][0].transcript
        if (event.results[index].isFinal) finalText += value
        else interimText += value
      }
      if (finalText) setTranscript((current) => `${current} ${finalText}`.trim())
      setInterimTranscript(interimText)
    }
    recognition.onerror = (event) => { listeningRef.current = false; setIsListening(false); setError(browserError(event.error)) }
    recognition.onend = () => { listeningRef.current = false; setIsListening(false); setInterimTranscript('') }
    recognitionRef.current = recognition
    return () => { recognition.onstart = null; recognition.onresult = null; recognition.onerror = null; recognition.onend = null; recognition.abort(); recognitionRef.current = null }
  }, [language])

  const startListening = useCallback(() => {
    const recognition = recognitionRef.current
    if (!recognition || listeningRef.current) return
    setTranscript(''); setInterimTranscript(''); setError(''); recognition.lang = language || 'en-IN'
    try { recognition.start() } catch (startError) { if (startError.name !== 'InvalidStateError') setError('Could not start voice recognition.') }
  }, [language])

  const stopListening = useCallback(() => {
    if (!recognitionRef.current || !listeningRef.current) return
    recognitionRef.current.stop()
  }, [])

  const resetTranscript = useCallback(() => { setTranscript(''); setInterimTranscript(''); setError('') }, [])
  return { transcript, interimTranscript, isListening, error, startListening, stopListening, resetTranscript, browserSupported, supported: browserSupported, listening: isListening, start: startListening }
}

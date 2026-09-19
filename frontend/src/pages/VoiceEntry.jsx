import { useEffect, useRef, useState } from 'react'
import { Bell, Check, ChevronRight, Mic, Sparkles } from 'lucide-react'
import { parseCommand, postTransaction } from '../services/api'
import { useSpeechRecognition } from '../hooks/useSpeechRecognition'

const languageNames = { 'en-IN': 'English', 'hi-IN': 'Hindi', 'te-IN': 'Telugu' }

export default function VoiceEntry({ lang, refresh, notify }) {
  const [text, setText] = useState('')
  const [parsed, setParsed] = useState(null)
  const [processing, setProcessing] = useState(false)
  const [success, setSuccess] = useState('')
  const lastProcessed = useRef('')
  const speech = useSpeechRecognition(lang)

  useEffect(() => { if (speech.transcript) setText(speech.transcript) }, [speech.transcript])
  useEffect(() => {
    if (!speech.transcript || speech.isListening || speech.transcript === lastProcessed.current) return
    lastProcessed.current = speech.transcript
    processText(speech.transcript)
  }, [speech.transcript, speech.isListening])

  async function processText(value = text) {
    const command = value.trim()
    if (!command) { notify('Please speak or enter a command first.'); return }
    setProcessing(true); setParsed(null); setSuccess('')
    try {
      const result = await parseCommand({ text: command, language: lang })
      setParsed(result.data)
    } catch (error) {
      notify(error.response?.data?.detail || 'Could not understand that command')
    } finally { setProcessing(false) }
  }

  async function confirmTransaction() {
    if (!parsed?.product_id || !parsed.quantity || !parsed.transaction_type) return
    setProcessing(true)
    try {
      await postTransaction(parsed.transaction_type === 'IN' ? 'in' : 'out', { product_id: parsed.product_id, quantity: parsed.quantity, unit: parsed.unit, price: parsed.price, source: 'VOICE', language: parsed.language, raw_text: text })
      await refresh()
      const action = parsed.transaction_type === 'IN' ? 'added to' : 'removed from'
      setSuccess(`${parsed.quantity} ${parsed.unit} ${parsed.product} successfully ${action} stock.`)
      setParsed(null); setText(''); lastProcessed.current = ''
    } catch (error) { notify(error.response?.data?.detail || 'Could not update stock') } finally { setProcessing(false) }
  }

  const displayText = speech.interimTranscript ? `${text} ${speech.interimTranscript}`.trim() : text
  return <div className="page-content"><section className="voice-layout"><div className="voice-main"><span className="section-kicker">SAY IT. WE'LL TRACK IT.</span><h2>Your stock, in your words.</h2><p className="lead">Speak naturally in English, Hindi, Telugu, or a mix. We’ll turn it into a stock update.</p><button type="button" className={speech.isListening ? 'mic-orb listening' : 'mic-orb'} onClick={speech.isListening ? speech.stopListening : speech.startListening} disabled={processing}><div className="mic-ring"/><Mic size={42}/><span>{processing ? 'Processing...' : speech.isListening ? 'Listening...' : 'Tap to speak'}</span></button>{!speech.browserSupported && <div className="fallback-note"><Bell size={16}/> Voice recognition is unavailable in this browser. Use the text input below.</div>}{speech.error && <div className="fallback-note"><Bell size={16}/>{speech.error}</div>}<div className="command-box"><input value={text} onChange={event => { setText(event.target.value); setParsed(null); setSuccess('') }} onKeyDown={event => event.key === 'Enter' && processText()} placeholder="Try: 20 kilo rice add karo"/><button type="button" onClick={() => processText()} disabled={processing}>{processing ? 'Processing...' : 'Process'} <ChevronRight size={16}/></button></div><div className="voice-examples"><span>Try saying</span><button type="button" onClick={() => { setText('20 kilo rice add karo'); processText('20 kilo rice add karo') }}>20 kilo rice add karo</button><button type="button" onClick={() => { setText('5 boxes biscuits sold'); processText('5 boxes biscuits sold') }}>5 boxes biscuits sold</button></div>{success && <div className="success-note"><Check size={16}/>{success}</div>}</div><aside className="voice-side"><div className="panel activity-card"><div className="panel-heading"><div><span className="section-kicker">VOICE ACTIVITY</span><h3>What we heard</h3></div><Mic size={18}/></div>{displayText && <div className="heard-text">“{displayText}”</div>}{parsed ? <><div className="detected-grid"><div><span>Intent</span><strong>{parsed.intent?.replace('_', ' ')}</strong></div><div><span>Language</span><strong>{languageNames[lang] || parsed.language}</strong></div><div><span>Product</span><strong>{parsed.product || 'Not found'}</strong></div><div><span>Quantity</span><strong>{parsed.quantity || '—'} {parsed.unit || ''}</strong></div><div><span>Action</span><strong>{parsed.transaction_type === 'IN' ? 'Stock In' : parsed.transaction_type === 'OUT' ? 'Stock Out' : '—'}</strong></div></div><div className="confidence"><span>Confidence</span><b>{Math.round((parsed.confidence || 0) * 100)}%</b><div><i style={{ width: `${(parsed.confidence || 0) * 100}%` }}/></div></div>{parsed.confidence < 0.75 && <div className="fallback-note">I’m not fully sure about this command. Please review it carefully.</div>}{parsed.product_id && parsed.quantity && parsed.transaction_type && <div className="confirm-actions"><button type="button" className="primary-button" onClick={confirmTransaction} disabled={processing}><Check size={17}/> Confirm</button><button type="button" className="secondary-button" onClick={() => setParsed(null)}>Cancel</button></div>}</> : !displayText && <div className="empty-state voice-empty"><Sparkles size={22}/>Your recognized command will appear here.</div>}</div><div className="language-tip"><span>LANGUAGE</span><strong>{languageNames[lang] || lang}</strong><small>Microphone uses {lang}. Change the language selector before speaking.</small></div></aside></section></div>
}

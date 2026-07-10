import { useState, useRef, useEffect } from 'react'
import { Send, Sparkles, Bot, User } from 'lucide-react'
import './AIChat.css'
import API from '../../config'

export default function AIChat() {
  const [message, setMessage] = useState('')
  const [messages, setMessages] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [sessionId, setSessionId] = useState(null)
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, isLoading])

  const sendToGemini = async (text) => {
    try {
      const res = await fetch(`${API}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text, session_id: sessionId }),
      })

      if (!res.ok) {
        const err = await res.json().catch(() => ({}))
        throw new Error(err.detail || `Server error (${res.status})`)
      }

      const data = await res.json()
      // Store session_id from backend for follow-up questions
      if (data.session_id) setSessionId(data.session_id)
      return data.reply
    } catch (err) {
      return `⚠️ ${err.message}`
    }
  }

  const handleSend = async () => {
    const text = message.trim()
    if (!text || isLoading) return

    const userMsg = { id: Date.now(), role: 'user', content: text }
    setMessages(prev => [...prev, userMsg])
    setMessage('')
    setIsLoading(true)

    const reply = await sendToGemini(text)

    const assistantMsg = { id: Date.now() + 1, role: 'assistant', content: reply }
    setMessages(prev => [...prev, assistantMsg])
    setIsLoading(false)
    inputRef.current?.focus()
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleSuggestion = async (text) => {
    if (isLoading) return

    const userMsg = { id: Date.now(), role: 'user', content: text }
    setMessages(prev => [...prev, userMsg])
    setMessage('')
    setIsLoading(true)

    const reply = await sendToGemini(text)

    const assistantMsg = { id: Date.now() + 1, role: 'assistant', content: reply }
    setMessages(prev => [...prev, assistantMsg])
    setIsLoading(false)
    inputRef.current?.focus()
  }

  const isEmpty = messages.length === 0

  return (
    <div className="chat-page animate-fade-in">
      <div className="page-header">
        <h1 className="page-title">AI Chat</h1>
        <p className="page-subtitle">Ask questions about your fleet, customers, and operations</p>
      </div>

      <div className="chat-container">
        {/* Messages Area */}
        <div className="chat-messages" id="chat-messages">
          {isEmpty && !isLoading && (
            <div className="chat-empty">
              <div className="chat-empty-icon">
                <Sparkles size={32} />
              </div>
              <h2>How can I help?</h2>
              <p>
                I can look up scooter statuses, battery health, customer info,
                rental history, and more. I'm read-only — I never modify your data.
              </p>

              <div className="chat-suggestions">
                <button className="chat-suggestion" onClick={() => handleSuggestion('How many scooters are active right now?')}>
                  Active scooters
                </button>
                <button className="chat-suggestion" onClick={() => handleSuggestion('Which batteries need replacement?')}>
                  Battery health
                </button>
                <button className="chat-suggestion" onClick={() => handleSuggestion("Show today's rentals")}>
                  Today's rentals
                </button>
                <button className="chat-suggestion" onClick={() => handleSuggestion('Top customers by revenue')}>
                  Top customers
                </button>
              </div>
            </div>
          )}

          {messages.map((msg) => (
            <div key={msg.id} className={`chat-bubble-row ${msg.role}`}>
              <div className="chat-bubble-avatar">
                {msg.role === 'user' ? <User size={16} /> : <Bot size={16} />}
              </div>
              <div className={`chat-bubble ${msg.role}`}>
                <div className="chat-bubble-label">
                  {msg.role === 'user' ? 'You' : 'VoltRide AI'}
                </div>
                <div className="chat-bubble-content">{msg.content}</div>
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="chat-bubble-row assistant">
              <div className="chat-bubble-avatar">
                <Bot size={16} />
              </div>
              <div className="chat-bubble assistant">
                <div className="chat-bubble-label">VoltRide AI</div>
                <div className="chat-typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="chat-input-area">
          <div className="chat-input-wrapper">
            <input
              ref={inputRef}
              type="text"
              className="chat-input"
              id="chat-input"
              placeholder="Ask about your fleet operations..."
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              autoComplete="off"
              disabled={isLoading}
            />
            <button
              className={`chat-send-btn${isLoading ? ' disabled' : ''}`}
              id="chat-send-btn"
              onClick={handleSend}
              aria-label="Send message"
              disabled={isLoading}
            >
              <Send size={18} />
            </button>
          </div>
          <div className="chat-disclaimer">
            <span>Read-only</span> · Powered by Gemini 2.5 Flash · Responses may not always be accurate
          </div>
        </div>
      </div>
    </div>
  )
}

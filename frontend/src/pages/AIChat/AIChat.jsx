import { useState } from 'react'
import { Send, Sparkles } from 'lucide-react'
import './AIChat.css'

export default function AIChat() {
  const [message, setMessage] = useState('')

  const handleSend = () => {
    if (!message.trim()) return
    // Will connect to backend later
    setMessage('')
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="chat-page animate-fade-in">
      <div className="page-header">
        <h1 className="page-title">AI Chat</h1>
        <p className="page-subtitle">Ask questions about your fleet, customers, and operations</p>
      </div>

      <div className="chat-container">
        {/* Messages Area */}
        <div className="chat-messages" id="chat-messages">
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
              <button className="chat-suggestion" onClick={() => setMessage('How many scooters are active right now?')}>
                Active scooters
              </button>
              <button className="chat-suggestion" onClick={() => setMessage('Which batteries need replacement?')}>
                Battery health
              </button>
              <button className="chat-suggestion" onClick={() => setMessage('Show today\'s rentals')}>
                Today's rentals
              </button>
              <button className="chat-suggestion" onClick={() => setMessage('Top customers by revenue')}>
                Top customers
              </button>
            </div>
          </div>
        </div>

        {/* Input Area */}
        <div className="chat-input-area">
          <div className="chat-input-wrapper">
            <input
              type="text"
              className="chat-input"
              id="chat-input"
              placeholder="Ask about your fleet operations..."
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              autoComplete="off"
            />
            <button
              className="chat-send-btn"
              id="chat-send-btn"
              onClick={handleSend}
              aria-label="Send message"
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

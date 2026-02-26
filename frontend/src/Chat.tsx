import { useEffect, useMemo, useRef, useState } from 'react'

type ChatRole = 'user' | 'assistant' | 'supervisor' | 'system'

type ChatMessage = {
  id: string
  conversation_id: string
  role: ChatRole
  text: string
  created_at: string
}

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api'
const DEFAULT_CONVERSATION_ID = 'demo-conversation'

export function Chat() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [isSending, setIsSending] = useState(false)

  const pollIntervalMs = 1200
  const listRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    let cancelled = false

    async function fetchMessages() {
      try {
        const res = await fetch(
          `${API_BASE}/chat/${DEFAULT_CONVERSATION_ID}`,
        )
        if (!res.ok) return
        const data = await res.json()
        if (!cancelled && data?.messages) {
          setMessages(data.messages)
        }
      } catch {
        // ignore network errors for demo
      }
    }

    fetchMessages()
    const id = setInterval(fetchMessages, pollIntervalMs)
    return () => {
      cancelled = true
      clearInterval(id)
    }
  }, [])

  useEffect(() => {
    if (!listRef.current) return
    listRef.current.scrollTop = listRef.current.scrollHeight
  }, [messages])

  const handleSend = async () => {
    const text = input.trim()
    if (!text) return
    setInput('')
    setIsSending(true)

    try {
      await fetch(
        `${API_BASE}/chat/${DEFAULT_CONVERSATION_ID}`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text }),
        },
      )
    } catch {
      // best-effort; backend will sync on next poll if available
    } finally {
      setIsSending(false)
    }
  }

  const handleKeyDown: React.KeyboardEventHandler<HTMLInputElement> = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      void handleSend()
    }
  }

  const groupedMessages = useMemo(
    () => messages.sort(
      (a, b) =>
        new Date(a.created_at).getTime() -
        new Date(b.created_at).getTime(),
    ),
    [messages],
  )

  return (
    <div className="chat-root">
      <header className="chat-header">
        <div className="chat-avatar">DA</div>
        <div className="chat-header-text">
          <div className="chat-title">Dubai Activities Assistant</div>
          <div className="chat-subtitle">online</div>
        </div>
      </header>

      <div className="chat-body" ref={listRef}>
        {groupedMessages.map((m) => (
          <MessageBubble key={m.id} message={m} />
        ))}
      </div>

      <div className="chat-input-row">
        <input
          className="chat-input"
          placeholder="Type a message"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
        />
        <button
          className="chat-send-btn"
          disabled={isSending || !input.trim()}
          onClick={handleSend}
        >
          Send
        </button>
      </div>
    </div>
  )
}

function MessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === 'user'
  const isSupervisor = message.role === 'supervisor'

  const bubbleClass = isUser
    ? 'bubble bubble-user'
    : isSupervisor
      ? 'bubble bubble-supervisor'
      : 'bubble bubble-assistant'

  const metaLabel = isSupervisor ? 'Supervisor' : undefined

  return (
    <div className={`bubble-row ${isUser ? 'align-right' : 'align-left'}`}>
      <div className={bubbleClass}>
        {metaLabel && (
          <div className="bubble-meta">{metaLabel}</div>
        )}
        <div className="bubble-text">{message.text}</div>
      </div>
    </div>
  )
}


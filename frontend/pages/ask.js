import { useState, useRef, useEffect } from 'react'
import Layout from '../components/Layout'
import withAuth from '../components/withAuth'
import api from '../lib/api'
import toast from 'react-hot-toast'
import { Send, Bot, User, FileText, Loader, Sparkles } from 'lucide-react'

function Message({ msg }) {
  const isUser = msg.role === 'user'
  return (
    <div className={`flex gap-3 ${isUser ? 'justify-end' : 'justify-start'}`}>
      {!isUser && (
        <div className="w-8 h-8 bg-indigo-600 rounded-full flex items-center justify-center shrink-0 mt-1">
          <Bot size={16} className="text-white" />
        </div>
      )}
      <div className={`max-w-[80%] ${isUser ? 'order-first' : ''}`}>
        <div className={`rounded-2xl px-4 py-3 text-sm leading-relaxed
          ${isUser
            ? 'bg-indigo-600 text-white rounded-tr-sm'
            : 'bg-gray-800 text-gray-100 rounded-tl-sm'}`}>
          <p className="whitespace-pre-wrap">{msg.content}</p>
        </div>

        {/* Sources */}
        {msg.sources && msg.sources.length > 0 && (
          <div className="mt-2 space-y-1">
            <p className="text-xs text-gray-500 px-1">Sources used:</p>
            {msg.sources.map((s, i) => (
              <div key={i} className="flex items-center gap-2 bg-gray-900 border border-gray-800 rounded-lg px-3 py-1.5">
                <FileText size={12} className="text-indigo-400 shrink-0" />
                <span className="text-xs text-gray-300 truncate">{s.title}</span>
                <span className="text-xs text-gray-600 ml-auto shrink-0">{Math.round(s.similarity * 100)}%</span>
              </div>
            ))}
          </div>
        )}
      </div>
      {isUser && (
        <div className="w-8 h-8 bg-gray-700 rounded-full flex items-center justify-center shrink-0 mt-1">
          <User size={16} className="text-gray-300" />
        </div>
      )}
    </div>
  )
}

function AskPage() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = async (e) => {
    e.preventDefault()
    if (!input.trim() || loading) return
    const question = input.trim()
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: question }])
    setLoading(true)

    try {
      const { data } = await api.post('/ask', { question })
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.answer,
        sources: data.sources
      }])
    } catch {
      toast.error('Failed to get answer')
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        sources: []
      }])
    } finally {
      setLoading(false)
    }
  }

  const suggestions = [
    'What are the main topics in my knowledge base?',
    'Summarize the key concepts from my documents',
    'What information do we have about authentication?',
  ]

  return (
    <Layout>
      <div className="max-w-3xl mx-auto flex flex-col h-[calc(100vh-8rem)]">
        <div className="mb-4">
          <h1 className="text-2xl font-bold text-white">Ask AI</h1>
          <p className="text-gray-400 text-sm mt-1">Get intelligent answers powered by your knowledge base</p>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto space-y-4 pb-4">
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <div className="w-16 h-16 bg-indigo-600/20 rounded-2xl flex items-center justify-center mb-4">
                <Sparkles size={32} className="text-indigo-400" />
              </div>
              <h3 className="text-white font-semibold mb-2">Ask anything about your knowledge base</h3>
              <p className="text-gray-500 text-sm mb-6 max-w-sm">Powered by LLaMA via Groq — fast, accurate answers with source citations</p>
              <div className="space-y-2 w-full max-w-sm">
                {suggestions.map((s, i) => (
                  <button key={i} onClick={() => setInput(s)}
                    className="w-full text-left px-4 py-2.5 bg-gray-900 border border-gray-800 rounded-xl text-sm text-gray-300 hover:border-indigo-500 hover:text-white transition-colors">
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((msg, i) => <Message key={i} msg={msg} />)}

          {loading && (
            <div className="flex gap-3">
              <div className="w-8 h-8 bg-indigo-600 rounded-full flex items-center justify-center shrink-0">
                <Bot size={16} className="text-white" />
              </div>
              <div className="bg-gray-800 rounded-2xl rounded-tl-sm px-4 py-3">
                <div className="flex gap-1 items-center h-5">
                  {[0, 1, 2].map(i => (
                    <div key={i} className="w-2 h-2 bg-indigo-500 rounded-full animate-bounce"
                      style={{ animationDelay: `${i * 0.15}s` }} />
                  ))}
                </div>
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {/* Input */}
        <form onSubmit={handleSend} className="flex gap-3 pt-4 border-t border-gray-800">
          <input
            className="input flex-1"
            placeholder="Ask a question about your documents..."
            value={input}
            onChange={e => setInput(e.target.value)}
            disabled={loading}
          />
          <button type="submit" disabled={loading || !input.trim()}
            className="btn-primary px-4 shrink-0">
            <Send size={18} />
          </button>
        </form>
      </div>
    </Layout>
  )
}

export default withAuth(AskPage)

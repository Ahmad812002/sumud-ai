import { useState, useEffect, useRef } from "react"
import { sendMessage } from "../services/api"

function Spinner() {
    return (
        <div className="flex items-center gap-2 px-4 py-2">
            <div className="w-5 h-5 border-4 border-[#C8102E] border-t-transparent rounded-full animate-spin" />
            <span className="text-[#A0A0A0] text-sm">Thinking...</span>
        </div>
    )
}

export default function Chat() {
    const bottomRef = useRef(null)
    const [input, setInput] = useState('')
    const [loading, setLoading] = useState(false)

    const [messages, setMessages] = useState(() => {
        const saved = localStorage.getItem('chat_history')
        return saved ? JSON.parse(saved) : [
            { role: 'assistant', content: 'Hello! How can I help with your job search today?' }
        ]
    })

    useEffect(() => {
        localStorage.setItem('chat_history', JSON.stringify(messages))
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [messages])

    const handleSend = async () => {
        if (!input.trim() || loading) return

        const userMessage = { role: 'user', content: input }
        setMessages(prev => [...prev, userMessage])
        setInput('')
        setLoading(true)

        try {
            const res = await sendMessage(input)
            if(res.data.ai_answer == null){
                setMessages(prev => [...prev, {
                role: 'assistant',
                content: 'Sorry, something went wrong. the llm returning none response.'
            }])
            }
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: res.data.ai_answer
            }])
        } catch (err) {
            console.error(err)
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: 'Sorry, something went wrong. Please try again.'
            }])
        } finally {
            setLoading(false)
        }
    }

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            handleSend()
        }
    }

    const clearHistory = () => {
        localStorage.removeItem('chat_history')
        setMessages([{
            role: 'assistant',
            content: 'Hello! How can I help with your job search today?'
        }])
    }

    return (
        <div className="flex flex-col min-h-full text-white">

            {/* Header */}
             <div className="flex flex-row items-center justify-between h-full text-white overflow-hidden w-full px-3">
                <div>
                    <h1 className="text-xl font-bold">Chat Assistant</h1>
                    <p className="text-[#A0A0A0] text-xs">
                        Ask anything about your career or job search
                    </p>
                </div>
                <button
                    onClick={clearHistory}
                    className="flex text-xs text-[#A0A0A0] hover:text-[#C8102E] transition-colors"
                >
                    Clear history
                </button>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
                {messages.map((msg, index) => (
                    <div
                        key={index}
                        className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                        <div className={`max-w-[75%] rounded-2xl px-4 py-3 text-sm leading-relaxed
                            ${msg.role === 'user'
                                ? 'bg-[#C8102E] text-white rounded-br-none'
                                : 'bg-[#007A3D] text-white rounded-bl-none border border-[#2E2E2E]'
                            }`}
                        >
                            {msg.content}
                        </div>
                    </div>
                ))}

                {loading && (
                    <div className="flex justify-start">
                        <div className="bg-[#2A2A2A] rounded-2xl rounded-bl-none border border-[#2E2E2E]">
                            <Spinner />
                        </div>
                    </div>
                )}

                <div ref={bottomRef} />
            </div>

            {/* Input */}
            <div className="px-6 py-4 border-t border-[#2E2E2E]">
                <div className="flex gap-3 items-end">
                    <textarea
                        className="flex-1 bg-[#2A2A2A] text-white border border-[#2E2E2E] rounded-xl px-4 py-3 text-sm resize-none focus:outline-none focus:border-[#C8102E] transition-colors"
                        rows={2}
                        placeholder="Ask about your job search..."
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                    />
                    <button
                        onClick={handleSend}
                        disabled={loading || !input.trim()}
                        className="bg-[#C8102E] hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed text-white px-5 py-3 rounded-xl text-sm font-medium transition-colors"
                    >
                        Send
                    </button>
                </div>
                <p className="text-[#A0A0A0] text-xs mt-2">
                    Shift+Enter for new line, Enter to send
                </p>
            </div>
        </div>
    )
}
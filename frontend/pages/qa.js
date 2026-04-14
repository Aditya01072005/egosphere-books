import { useState, useEffect, useRef } from 'react';
import Navbar from '@/components/Navbar';
import { askQuestion, fetchQAHistory } from '@/lib/api';

function SourceBadge({ source }) {
  return (
    <a
      href={`/books/${source.book_id}`}
      className="inline-flex items-center gap-1 bg-indigo-900/40 border border-indigo-700 text-indigo-300 text-xs px-2 py-1 rounded-full hover:bg-indigo-800/40 transition-colors"
    >
      📖 {source.book_title}
      <span className="opacity-60">({(source.relevance_score * 100).toFixed(0)}%)</span>
    </a>
  );
}

function ChatMessage({ item }) {
  return (
    <div className="space-y-3">
      {/* Question */}
      <div className="flex justify-end">
        <div className="bg-indigo-600 text-white rounded-2xl rounded-tr-sm px-4 py-3 max-w-xl text-sm">
          {item.question}
        </div>
      </div>
      {/* Answer */}
      <div className="flex justify-start">
        <div className="bg-gray-800 border border-gray-700 rounded-2xl rounded-tl-sm px-4 py-3 max-w-2xl">
          <p className="text-gray-200 text-sm leading-relaxed whitespace-pre-wrap">{item.answer}</p>
          {item.cached && (
            <span className="text-xs text-gray-500 mt-1 block">⚡ Cached response</span>
          )}
          {item.sources && item.sources.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-2">
              <span className="text-xs text-gray-500">Sources:</span>
              {item.sources.map((s, i) => (
                <SourceBadge key={i} source={s} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default function QAPage() {
  const [messages, setMessages] = useState([]);
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);
  const bottomRef = useRef(null);

  useEffect(() => {
    fetchQAHistory()
      .then((res) => setHistory(res.data))
      .catch(() => {});
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleAsk = async (e) => {
    e.preventDefault();
    if (!question.trim() || loading) return;

    const q = question.trim();
    setQuestion('');
    setLoading(true);

    // Optimistically add question
    setMessages((prev) => [...prev, { question: q, answer: null }]);

    try {
      const res = await askQuestion(q);
      setMessages((prev) =>
        prev.map((m, i) =>
          i === prev.length - 1
            ? { question: q, answer: res.data.answer, sources: res.data.sources, cached: res.data.cached }
            : m
        )
      );
    } catch (err) {
      setMessages((prev) =>
        prev.map((m, i) =>
          i === prev.length - 1
            ? { question: q, answer: 'Error: Could not get a response. Is the backend running?', sources: [] }
            : m
        )
      );
    } finally {
      setLoading(false);
    }
  };

  const SAMPLE_QUESTIONS = [
    'What is the best mystery book?',
    'Recommend a book about love',
    'Which books have a dark tone?',
    'Tell me about a fantasy book',
  ];

  return (
    <div className="min-h-screen bg-gray-950 flex flex-col">
      <Navbar />

      <div className="flex flex-1 max-w-7xl mx-auto w-full px-4 py-6 gap-6">

        {/* Chat Area */}
        <div className="flex-1 flex flex-col">
          <h1 className="text-2xl font-bold text-white mb-4">💬 Ask About Books</h1>

          {/* Sample questions */}
          {messages.length === 0 && (
            <div className="mb-6">
              <p className="text-gray-500 text-sm mb-3">Try asking:</p>
              <div className="flex flex-wrap gap-2">
                {SAMPLE_QUESTIONS.map((q) => (
                  <button
                    key={q}
                    onClick={() => setQuestion(q)}
                    className="bg-gray-800 hover:bg-gray-700 border border-gray-700 text-gray-300 text-xs px-3 py-1.5 rounded-full transition-colors"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Messages */}
          <div className="flex-1 overflow-y-auto space-y-6 mb-4 min-h-[300px]">
            {messages.map((msg, i) => (
              <div key={i}>
                {msg.answer === null ? (
                  <div className="space-y-3">
                    <div className="flex justify-end">
                      <div className="bg-indigo-600 text-white rounded-2xl rounded-tr-sm px-4 py-3 max-w-xl text-sm">
                        {msg.question}
                      </div>
                    </div>
                    <div className="flex justify-start">
                      <div className="bg-gray-800 border border-gray-700 rounded-2xl rounded-tl-sm px-4 py-3">
                        <div className="flex gap-1">
                          <span className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                          <span className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                          <span className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                        </div>
                      </div>
                    </div>
                  </div>
                ) : (
                  <ChatMessage item={msg} />
                )}
              </div>
            ))}
            <div ref={bottomRef} />
          </div>

          {/* Input */}
          <form onSubmit={handleAsk} className="flex gap-3">
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Ask anything about the books..."
              className="flex-1 bg-gray-900 border border-gray-700 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-indigo-500 text-sm"
            />
            <button
              type="submit"
              disabled={loading || !question.trim()}
              className="px-6 py-3 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white rounded-xl font-medium text-sm transition-colors"
            >
              Ask
            </button>
          </form>
        </div>

        {/* History Sidebar */}
        <div className="hidden lg:block w-72 flex-shrink-0">
          <h2 className="text-sm font-semibold text-gray-400 mb-3 uppercase tracking-wider">
            Recent Questions
          </h2>
          <div className="space-y-2 overflow-y-auto max-h-[600px]">
            {history.length === 0 ? (
              <p className="text-gray-600 text-xs">No history yet.</p>
            ) : (
              history.map((h) => (
                <button
                  key={h.id}
                  onClick={() => setQuestion(h.question)}
                  className="w-full text-left bg-gray-900 border border-gray-800 hover:border-indigo-600 rounded-xl px-3 py-2.5 text-xs text-gray-400 hover:text-white transition-all"
                >
                  <p className="line-clamp-2">{h.question}</p>
                  <p className="text-gray-600 mt-1 text-xs">
                    {new Date(h.created_at).toLocaleDateString()}
                  </p>
                </button>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

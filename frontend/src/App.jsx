import { useRef, useState } from 'react'
import './App.css'

const API_BASE = 'http://localhost:8000'

const suggestions = [
  ['Clean energy', 'How do grid-scale batteries store renewable energy?'],
  ['Technology', 'How does satellite internet reach remote areas?'],
  ['Environment', 'How can cities reduce extreme heat?'],
]

const researchDetails = [
  ['Editor review', 'review'],
  ['Research plan', 'plan'],
  ['Search results', 'search_results'],
  ['Reader notes', 'reader_results'],
  ['Combined research', 'research'],
]

function App() {
  const [topic, setTopic] = useState('')
  const [history, setHistory] = useState([])
  const [selectedId, setSelectedId] = useState(null)
  const [loading, setLoading] = useState(false)
  const [showHistory, setShowHistory] = useState(false)
  const input = useRef(null)
  const view = useRef(null)
  const current = history.find((entry) => entry.id === selectedId)

  function openResearch(id) {
    setSelectedId(id)
    setShowHistory(false)
    view.current?.scrollTo(0, 0)
  }

  function newResearch() {
    openResearch(null)
    setTopic('')
    input.current?.focus()
  }

  async function submitTopic(event) {
    event.preventDefault()
    const question = topic.trim()
    if (!question || loading) return

    const id = crypto.randomUUID()
    setHistory((entries) => [{ id, question }, ...entries])
    openResearch(id)
    setTopic('')
    setLoading(true)

    let update
    try {
      const response = await fetch(`${API_BASE}/api/research`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic: question }),
      })
      const data = await response.json().catch(() => null)
      if (!response.ok || !data) {
        const message = typeof data?.detail === 'string' ? data.detail : `Request failed (${response.status}).`
        throw new Error(message)
      }
      update = { result: data }
    } catch (error) {
      update = { error: error.message }
    }

    setHistory((entries) => entries.map((entry) => (
      entry.id === id ? Object.assign({}, entry, update) : entry
    )))
    setLoading(false)
  }

  function fillTopic(question) {
    setTopic(question)
    input.current?.focus()
  }

  return (
    <div className="workspace">
      <aside className={showHistory ? 'sidebar sidebar-open' : 'sidebar'} id="history">
        <div className="brand"><span className="brand-icon" aria-hidden="true">✳</span> Research Desk</div>
        <button className="new-research" onClick={newResearch}><span aria-hidden="true">+</span> New research</button>
        <nav aria-label="Research history">
          <h2>History</h2>
          {history.length === 0 && <p className="empty-history">No research yet</p>}
          {history.map((entry) => (
            <button
              className="history-item"
              key={entry.id}
              aria-current={entry.id === selectedId ? 'true' : undefined}
              title={entry.question}
              onClick={() => openResearch(entry.id)}
            >
              {entry.question}
            </button>
          ))}
        </nav>
      </aside>

      <main className="main">
        <header className="topbar">
          <button className="history-toggle" aria-expanded={showHistory} aria-controls="history" onClick={() => setShowHistory(!showHistory)}>
            History
          </button>
          <span>Research workspace</span>
        </header>

        <div className={current ? 'view' : 'view welcome-view'} ref={view}>
          {current ? (
            <div className="conversation">
              <p className="question">{current.question}</p>
              <section className="answer" aria-label="Research response">
                <div className="answer-heading"><span className="brand-icon small-icon" aria-hidden="true">✳</span><h1>Research Desk</h1></div>
                {current.error && <p className="error" role="alert">{current.error}</p>}
                {!current.result && !current.error && <p className="working" role="status">Searching sources and drafting an article…</p>}
                {current.result && <ResearchResult result={current.result} />}
              </section>
            </div>
          ) : (
            <section className="welcome">
              <span className="brand-icon welcome-icon" aria-hidden="true">✳</span>
              <h1>What are you curious about?</h1>
              <p>Pick a topic and get a researched article with sources.</p>
              <div className="suggestions">
                {suggestions.map(([label, question]) => (
                  <button key={label} onClick={() => fillTopic(question)}>
                    <span>{label}</span>
                    {question}
                  </button>
                ))}
              </div>
            </section>
          )}
        </div>

        <footer className="composer-area">
          <form className="composer" onSubmit={submitTopic}>
            <input
              ref={input}
              value={topic}
              onChange={(event) => setTopic(event.target.value)}
              aria-label="Research topic"
              placeholder="Ask a research question…"
            />
            <button type="submit" disabled={loading || !topic.trim()}>{loading ? 'Researching…' : 'Research'}</button>
          </form>
        </footer>
      </main>
    </div>
  )
}

function ResearchResult({ result }) {
  return (
    <>
      <article className="article">
        {result.article?.split(/\n\s*\n/).map((block, index) => {
          const heading = block.match(/^(#{1,6})\s+([^\n]+)$/)
          if (heading) {
            const Heading = heading[1].length === 1 ? 'h2' : 'h3'
            return <Heading key={index}>{heading[2]}</Heading>
          }
          return <p key={index}>{articleText(block)}</p>
        })}
      </article>
      <div className="details">
        {researchDetails.map(([label, field]) => result[field] && (
          <details key={field}>
            <summary>{label}</summary>
            <p>{result[field]}</p>
          </details>
        ))}
      </div>
    </>
  )
}

function articleText(text) {
  return text.split(/(\[[^\]\n]+\]\(https?:\/\/[^\s)]+\)|\*\*[^*\n]+\*\*)/g).map((part, index) => {
    const link = part.match(/^\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)$/)
    if (link) return <a key={index} href={link[2]} target="_blank" rel="noreferrer">{link[1]}</a>
    if (part.startsWith('**') && part.endsWith('**') && part.length > 4) {
      return <strong key={index}>{part.slice(2, -2)}</strong>
    }
    return part
  })
}

export default App

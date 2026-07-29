import { useState } from 'react'
import './App.css'

const API_URL = 'http://localhost:8000/api/research'

function App() {
  const [topic, setTopic] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)

  const runPipeline = async (e) => {
    e.preventDefault()
    if (!topic.trim() || loading) return

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const res = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic }),
      })
      if (!res.ok) throw new Error(`Request failed: ${res.status}`)
      const data = await res.json()
      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page">
      <h1>Research Pipeline</h1>

      <form className="topic-form" onSubmit={runPipeline}>
        <input
          type="text"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder="Enter a research topic..."
          disabled={loading}
        />
        <button type="submit" disabled={loading || !topic.trim()}>
          {loading ? 'Researching...' : 'Run'}
        </button>
      </form>

      {error && <p className="error">Error: {error}</p>}

      {loading && <p className="status">Running search and reader agents, this can take a while...</p>}

      {result && (
        <div className="results">
          <section className="panel">
            <h2>Search Results</h2>
            <pre>{result.search_results}</pre>
          </section>

          <section className="panel">
            <h2>Reader Notes</h2>
            <pre>{result.reader_results}</pre>
          </section>

          <section className="panel">
            <h2>Combined Research</h2>
            <pre>{result.research}</pre>
          </section>
        </div>
      )}
    </div>
  )
}

export default App

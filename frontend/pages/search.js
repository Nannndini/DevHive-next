import { useState } from 'react'
import Layout from '../components/Layout'
import withAuth from '../components/withAuth'
import api from '../lib/api'
import toast from 'react-hot-toast'
import { Search, FileText, Loader } from 'lucide-react'

function SearchPage() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [searched, setSearched] = useState(false)

  const handleSearch = async (e) => {
    e.preventDefault()
    if (!query.trim()) return
    setLoading(true)
    setSearched(false)
    try {
      const { data } = await api.post('/search', { query, limit: 8 })
      setResults(data.results)
      setSearched(true)
    } catch { toast.error('Search failed') }
    finally { setLoading(false) }
  }

  const similarityColor = (score) => {
    if (score >= 0.7) return 'text-emerald-400 bg-emerald-900/30'
    if (score >= 0.5) return 'text-yellow-400 bg-yellow-900/30'
    return 'text-gray-400 bg-gray-800'
  }

  return (
    <Layout>
      <div className="max-w-3xl mx-auto space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-white">Semantic Search</h1>
          <p className="text-gray-400 text-sm mt-1">Search across your knowledge base using AI-powered semantic understanding</p>
        </div>

        <form onSubmit={handleSearch} className="flex gap-3">
          <div className="relative flex-1">
            <Search size={18} className="absolute left-3 top-3 text-gray-500" />
            <input
              className="input pl-10"
              placeholder="What are you looking for?"
              value={query}
              onChange={e => setQuery(e.target.value)}
            />
          </div>
          <button type="submit" disabled={loading || !query.trim()} className="btn-primary px-6">
            {loading ? <Loader size={18} className="animate-spin" /> : 'Search'}
          </button>
        </form>

        {/* Results */}
        {loading && (
          <div className="text-center py-12">
            <Loader size={32} className="animate-spin text-indigo-500 mx-auto mb-3" />
            <p className="text-gray-400">Searching knowledge base...</p>
          </div>
        )}

        {searched && !loading && (
          <div>
            <p className="text-sm text-gray-500 mb-4">
              Found <span className="text-white font-medium">{results.length}</span> results for "{query}"
            </p>

            {results.length === 0 ? (
              <div className="card text-center py-12">
                <Search size={40} className="mx-auto text-gray-700 mb-3" />
                <p className="text-gray-400">No results found. Try different keywords or upload more documents.</p>
              </div>
            ) : (
              <div className="space-y-3">
                {results.map((r, i) => (
                  <div key={i} className="card hover:border-gray-700 transition-colors">
                    <div className="flex items-start justify-between gap-4 mb-2">
                      <div className="flex items-center gap-2">
                        <FileText size={16} className="text-indigo-400 shrink-0" />
                        <p className="font-medium text-white text-sm">{r.title}</p>
                        <span className="text-xs text-gray-500 capitalize">({r.source})</span>
                      </div>
                      <span className={`text-xs font-medium px-2 py-0.5 rounded shrink-0 ${similarityColor(r.similarity)}`}>
                        {Math.round(r.similarity * 100)}% match
                      </span>
                    </div>
                    <p className="text-gray-300 text-sm leading-relaxed line-clamp-4">{r.chunk_text}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </Layout>
  )
}

export default withAuth(SearchPage)

import { useState, useEffect, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import Layout from '../components/Layout'
import withAuth from '../components/withAuth'
import api from '../lib/api'
import toast from 'react-hot-toast'
import { Upload, FileText, Trash2, Plus, X, AlertCircle, CheckCircle } from 'lucide-react'

function DocumentsPage() {
  const [docs, setDocs] = useState([])
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [showTextForm, setShowTextForm] = useState(false)
  const [textForm, setTextForm] = useState({ title: '', content: '' })

  const fetchDocs = async () => {
    try {
      const { data } = await api.get('/documents')
      setDocs(data.documents)
    } catch { toast.error('Failed to fetch documents') }
    finally { setLoading(false) }
  }

  useEffect(() => { fetchDocs() }, [])

  const onDrop = useCallback(async (acceptedFiles) => {
    setUploading(true)
    for (const file of acceptedFiles) {
      const formData = new FormData()
      formData.append('file', file)
      try {
        const { data } = await api.post('/documents/ingest/file', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
        if (data.duplicate) toast(`"${file.name}" already exists (duplicate)`, { icon: '⚠️' })
        else toast.success(`"${file.name}" uploaded & indexed!`)
      } catch (err) {
        toast.error(`Failed to upload "${file.name}"`)
      }
    }
    setUploading(false)
    fetchDocs()
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'], 'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'], 'text/plain': ['.txt', '.md'] },
    multiple: true
  })

  const handleTextIngest = async (e) => {
    e.preventDefault()
    if (!textForm.title || !textForm.content) return toast.error('Fill all fields')
    try {
      const { data } = await api.post('/documents/ingest/text', textForm)
      if (data.duplicate) toast('Duplicate content detected', { icon: '⚠️' })
      else toast.success('Document ingested!')
      setTextForm({ title: '', content: '' })
      setShowTextForm(false)
      fetchDocs()
    } catch { toast.error('Failed to ingest text') }
  }

  const handleDelete = async (id, title) => {
    if (!confirm(`Delete "${title}"?`)) return
    try {
      await api.delete(`/documents/${id}`)
      toast.success('Deleted')
      setDocs(docs.filter(d => d.id !== id))
    } catch { toast.error('Delete failed') }
  }

  const fileTypeColor = (type) => {
    const map = { pdf: 'text-red-400 bg-red-900/30', docx: 'text-blue-400 bg-blue-900/30', txt: 'text-green-400 bg-green-900/30', md: 'text-yellow-400 bg-yellow-900/30' }
    return map[type] || 'text-gray-400 bg-gray-800'
  }

  return (
    <Layout>
      <div className="max-w-4xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">Documents</h1>
            <p className="text-gray-400 text-sm mt-1">Upload and manage your knowledge base</p>
          </div>
          <button onClick={() => setShowTextForm(!showTextForm)} className="btn-secondary flex items-center gap-2">
            {showTextForm ? <X size={16} /> : <Plus size={16} />}
            {showTextForm ? 'Cancel' : 'Add Text'}
          </button>
        </div>

        {/* Text form */}
        {showTextForm && (
          <div className="card">
            <h3 className="font-semibold text-white mb-4">Add Text Content</h3>
            <form onSubmit={handleTextIngest} className="space-y-4">
              <div>
                <label className="label">Title</label>
                <input className="input" placeholder="Document title" value={textForm.title}
                  onChange={e => setTextForm({ ...textForm, title: e.target.value })} required />
              </div>
              <div>
                <label className="label">Content</label>
                <textarea className="input" rows={6} placeholder="Paste your content here..."
                  value={textForm.content}
                  onChange={e => setTextForm({ ...textForm, content: e.target.value })} required />
              </div>
              <button type="submit" className="btn-primary">Ingest Document</button>
            </form>
          </div>
        )}

        {/* Dropzone */}
        <div {...getRootProps()}
          className={`border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-all
            ${isDragActive ? 'border-indigo-500 bg-indigo-500/10' : 'border-gray-700 hover:border-indigo-600 hover:bg-gray-900'}`}>
          <input {...getInputProps()} />
          <Upload size={32} className={`mx-auto mb-3 ${isDragActive ? 'text-indigo-400' : 'text-gray-600'}`} />
          {uploading ? (
            <p className="text-indigo-400 font-medium">Uploading & indexing...</p>
          ) : isDragActive ? (
            <p className="text-indigo-400 font-medium">Drop files here!</p>
          ) : (
            <>
              <p className="text-gray-300 font-medium">Drag & drop files here, or click to browse</p>
              <p className="text-gray-500 text-sm mt-1">Supports PDF, DOCX, TXT, MD</p>
            </>
          )}
        </div>

        {/* Documents list */}
        <div>
          <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">
            {loading ? 'Loading...' : `${docs.length} Document${docs.length !== 1 ? 's' : ''}`}
          </h2>
          {!loading && docs.length === 0 && (
            <div className="card text-center py-12">
              <FileText size={40} className="mx-auto text-gray-700 mb-3" />
              <p className="text-gray-500">No documents yet. Upload your first file above.</p>
            </div>
          )}
          <div className="space-y-2">
            {docs.map((doc) => (
              <div key={doc.id} className="card flex items-center gap-4 py-4">
                <FileText size={20} className="text-indigo-400 shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-white truncate">{doc.title}</p>
                  <p className="text-xs text-gray-500 mt-0.5">
                    {doc.source} · {new Date(doc.created_at).toLocaleDateString()}
                  </p>
                </div>
                {doc.file_type && (
                  <span className={`text-xs font-medium px-2 py-0.5 rounded uppercase ${fileTypeColor(doc.file_type)}`}>
                    {doc.file_type}
                  </span>
                )}
                <button onClick={() => handleDelete(doc.id, doc.title)}
                  className="text-gray-600 hover:text-red-400 transition-colors p-1 shrink-0">
                  <Trash2 size={16} />
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </Layout>
  )
}

export default withAuth(DocumentsPage)

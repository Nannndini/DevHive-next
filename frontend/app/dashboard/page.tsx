export default function Dashboard() {
  return (
    <div className="min-h-screen bg-black text-cyan-400 p-8 font-mono">
      <h1 className="text-4xl font-bold mb-8 uppercase border-b border-cyan-900 pb-4">Main Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="border border-cyan-800 p-6 bg-cyan-950/20 hover:bg-cyan-900/40 transition">
          <h2 className="text-xl font-bold mb-2">Documents</h2>
          <p className="text-gray-400">Manage and view ingested knowledge vectors.</p>
        </div>
        <div className="border border-cyan-800 p-6 bg-cyan-950/20 hover:bg-cyan-900/40 transition">
          <h2 className="text-xl font-bold mb-2">Search</h2>
          <p className="text-gray-400">Query the neural embedding space.</p>
        </div>
        <div className="border border-cyan-800 p-6 bg-cyan-950/20 hover:bg-cyan-900/40 transition">
          <h2 className="text-xl font-bold mb-2">Ask AI</h2>
          <p className="text-gray-400">Generative insights based on stored context.</p>
        </div>
      </div>
    </div>
  );
}

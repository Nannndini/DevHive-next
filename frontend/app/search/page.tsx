"use client";

import { useState } from "react";

export default function Search() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || ""}/search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });
      const data = await res.json();
      setResults(data.results || []);
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-black text-cyan-400 p-8 font-mono">
      <h1 className="text-3xl font-bold mb-6 border-b border-cyan-900 pb-2">Semantic Search</h1>
      <form onSubmit={handleSearch} className="mb-8">
        <input 
          type="text" 
          value={query} 
          onChange={e => setQuery(e.target.value)} 
          placeholder="Search vectors..." 
          className="w-full bg-gray-900 border border-cyan-800 p-4 text-white focus:outline-none focus:border-cyan-400" 
          required 
        />
        <button type="submit" disabled={loading} className="mt-4 px-6 py-2 bg-cyan-900 hover:bg-cyan-700 text-white disabled:opacity-50">
          {loading ? "SEARCHING..." : "INITIATE SEARCH"}
        </button>
      </form>
      <div className="space-y-4">
        {results.map((res: any, idx) => (
          <div key={idx} className="border border-cyan-900 p-4">
            <p className="text-white">{res.content}</p>
            <p className="text-xs text-cyan-600 mt-2">Similarity: {res.score}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

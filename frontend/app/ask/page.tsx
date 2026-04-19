"use client";

import { useState } from "react";

export default function Ask() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);

  const handleAsk = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || ""}/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      const data = await res.json();
      setAnswer(data.answer || "No response generated.");
    } catch (err) {
      setAnswer("Failed to connect to the generative core.");
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-black text-cyan-400 p-8 font-mono">
      <h1 className="text-3xl font-bold mb-6 border-b border-cyan-900 pb-2">Generative Query Node</h1>
      <form onSubmit={handleAsk} className="mb-8">
        <input 
          type="text" 
          value={question} 
          onChange={e => setQuestion(e.target.value)} 
          placeholder="Enter query..." 
          className="w-full bg-gray-900 border border-cyan-800 p-4 text-white focus:outline-none focus:border-cyan-400" 
          required 
        />
        <button type="submit" disabled={loading} className="mt-4 px-6 py-2 bg-cyan-900 hover:bg-cyan-700 text-white disabled:opacity-50">
          {loading ? "GENERATING..." : "TRANSMIT QUERY"}
        </button>
      </form>
      {answer && (
        <div className="bg-gray-900/50 border border-purple-900 p-6 rounded whitespace-pre-wrap text-purple-100">
          {answer}
        </div>
      )}
    </div>
  );
}

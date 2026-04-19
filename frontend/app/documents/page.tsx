"use client";

import { useEffect, useState } from "react";

export default function Documents() {
  const [docs, setDocs] = useState([]);

  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL || ""}/documents`)
      .then(res => res.json())
      .then(data => setDocs(data.documents || []))
      .catch(console.error);
  }, []);

  return (
    <div className="min-h-screen bg-black text-cyan-400 p-8 font-mono">
      <h1 className="text-3xl font-bold mb-6 border-b border-cyan-900 pb-2">Vectorized Documents</h1>
      <div className="space-y-4">
        {docs.length === 0 ? <p className="text-gray-500">No documents indexed yet.</p> : null}
        {docs.map((doc: any) => (
          <div key={doc.id} className="border border-cyan-900 bg-gray-900/40 p-4 hover:border-cyan-500 transition">
            <h2 className="font-bold text-white">{doc.title}</h2>
            <p className="text-sm text-cyan-700 mt-1">ID: {doc.id} | Source: {doc.source}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

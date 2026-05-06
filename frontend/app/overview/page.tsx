"use client";

import { useEffect, useState } from "react";
import { Navbar } from "@/components/Navbar";

export default function OverviewDashboard() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "http://127.0.0.1:8000";
    fetch(`${backendUrl}/analytics/overview`)
      .then((res) => {
        if (!res.ok) throw new Error("Failed to fetch overview data");
        return res.json();
      })
      .then((json) => {
        setData(json);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Error loading overview:", err);
        setError("SYSTEM FAILURE: Overview unreachable.");
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-white text-black flex items-center justify-center font-sans">
        <div className="animate-pulse font-bold tracking-widest text-sm uppercase">Loading System Overview...</div>
      </div>
    );
  }

  if (error || !data) {
    return <div className="min-h-screen bg-white text-red-600 p-8 font-sans font-bold">{error}</div>;
  }

  return (
    <div className="min-h-screen bg-white text-black font-sans">
      <Navbar />
      
      <main className="max-w-7xl mx-auto px-6 py-10 space-y-12">
        <header className="border-b border-neutral-200 pb-4">
          <h1 className="text-3xl font-black tracking-tight uppercase">
            System Overview
          </h1>
          <p className="text-neutral-500 text-xs font-bold tracking-widest uppercase mt-2 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-blue-600 animate-pulse"></span>
            Neural Architecture Status | Build 1.0.4
          </p>
        </header>

        {/* 4 Stat Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="border border-neutral-200 p-6 rounded-xl flex flex-col gap-2 shadow-sm">
            <span className="text-xs font-bold text-neutral-500 uppercase tracking-widest">Total Documents</span>
            <span className="text-4xl font-black">{data.stats.total_documents}</span>
          </div>
          <div className="border border-neutral-200 p-6 rounded-xl flex flex-col gap-2 shadow-sm">
            <span className="text-xs font-bold text-neutral-500 uppercase tracking-widest">Vector Embeddings</span>
            <span className="text-4xl font-black">{data.stats.total_chunks}</span>
          </div>
          <div className="border border-neutral-200 p-6 rounded-xl flex flex-col gap-2 shadow-sm">
            <span className="text-xs font-bold text-neutral-500 uppercase tracking-widest">Active Connections</span>
            <span className="text-4xl font-black">{data.stats.active_users}</span>
          </div>
          <div className="border border-neutral-200 p-6 rounded-xl flex flex-col gap-2 shadow-sm">
            <span className="text-xs font-bold text-neutral-500 uppercase tracking-widest">System Uptime</span>
            <span className="text-4xl font-black text-green-500">{data.stats.uptime_percentage}</span>
          </div>
        </div>

        {/* Documents Table */}
        <div className="space-y-4">
          <h3 className="text-xs font-bold text-neutral-500 uppercase tracking-widest flex items-center gap-2">
            <span className="w-1.5 h-1.5 bg-neutral-300 rounded-full"></span> Node Library
          </h3>
          <div className="border border-neutral-200 rounded-xl overflow-hidden shadow-sm">
            <table className="w-full text-left text-sm">
              <thead className="bg-neutral-50 text-neutral-500 border-b border-neutral-200 text-xs uppercase tracking-widest">
                <tr>
                  <th className="px-6 py-4 font-bold">Entry</th>
                  <th className="px-6 py-4 font-bold">Status</th>
                  <th className="px-6 py-4 font-bold">Chunks</th>
                  <th className="px-6 py-4 font-bold">Protocol</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-neutral-100 bg-white">
                {data.documents.map((doc: any) => (
                  <tr key={doc.id} className="hover:bg-neutral-50 transition-colors">
                    <td className="px-6 py-4 font-medium">{doc.name}</td>
                    <td className="px-6 py-4">
                      <span className={`text-[10px] font-bold tracking-widest uppercase px-2 py-1 rounded-sm ${
                        doc.status === 'INDEXED' ? 'text-green-600 bg-green-50' :
                        doc.status === 'VECTOR_SYNC' ? 'text-blue-600 bg-blue-50' :
                        'text-neutral-500 bg-neutral-100'
                      }`}>
                        {doc.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-neutral-600 font-mono text-xs">{doc.chunks}</td>
                    <td className="px-6 py-4">
                      <span className="text-blue-600 hover:text-blue-800 cursor-pointer font-bold text-xs uppercase tracking-widest">Inspect Node</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Global Logs Table (Recent Queries) */}
        <div className="space-y-4">
          <h3 className="text-xs font-bold text-neutral-500 uppercase tracking-widest flex items-center gap-2">
            <span className="w-1.5 h-1.5 bg-neutral-300 rounded-full"></span> Global Logs
          </h3>
          <div className="border border-neutral-200 rounded-xl overflow-hidden shadow-sm">
            <table className="w-full text-left text-sm">
              <thead className="bg-neutral-50 text-neutral-500 border-b border-neutral-200 text-xs uppercase tracking-widest">
                <tr>
                  <th className="px-6 py-4 font-bold">Query Log</th>
                  <th className="px-6 py-4 font-bold">Latency</th>
                  <th className="px-6 py-4 font-bold">Context Chunks</th>
                  <th className="px-6 py-4 font-bold">Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-neutral-100 bg-white">
                {data.recent_queries.map((query: any) => (
                  <tr key={query.id} className="hover:bg-neutral-50 transition-colors">
                    <td className="px-6 py-4 font-medium text-neutral-800">{query.query}</td>
                    <td className="px-6 py-4 font-mono text-xs text-neutral-500">{query.response_time}</td>
                    <td className="px-6 py-4 text-neutral-600 font-mono text-xs">{query.chunks_used}</td>
                    <td className="px-6 py-4 text-neutral-400 text-xs">{query.timestamp}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </main>
    </div>
  );
}

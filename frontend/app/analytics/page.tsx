"use client";

import { useEffect, useState } from "react";
import { Navbar } from "@/components/Navbar";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  Cell,
} from "recharts";

export default function AnalyticsDashboard() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "http://127.0.0.1:8000";
    fetch(`${backendUrl}/analytics/dashboard`)
      .then((res) => {
        if (!res.ok) throw new Error("Failed to fetch analytics");
        return res.json();
      })
      .then((json) => {
        setData(json);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to load analytics", err);
        setError("SYSTEM FAILURE: Analytics unreachable.");
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-white text-black flex items-center justify-center font-sans">
        <div className="animate-pulse font-bold tracking-widest text-sm uppercase">Loading Neural Analytics...</div>
      </div>
    );
  }

  if (error || !data) {
    return <div className="min-h-screen bg-white text-red-600 p-8 font-sans font-bold">{error}</div>;
  }

  return (
    <div className="min-h-screen bg-white text-black font-sans">
      <Navbar />

      <main className="max-w-7xl mx-auto px-6 py-10 space-y-8">
        <header className="border-b border-neutral-200 pb-4">
          <p className="text-neutral-500 text-xs font-bold tracking-widest uppercase mb-2 flex items-center gap-2">
             <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" className="text-blue-600"><path d="M2 12h4l3-9 5 18 3-9h5"/></svg>
             Neural Intelligence Dashboard
          </p>
          <h1 className="text-3xl font-black tracking-tight">
            System Analytics
          </h1>
        </header>

        {/* 4 Stat Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="border border-neutral-200 p-6 rounded-xl flex flex-col gap-2 shadow-sm relative">
            <span className="text-xs font-bold text-neutral-500 uppercase tracking-widest">Total Queries</span>
            <span className="text-4xl font-black">{data.stats.total_queries}</span>
            <span className="absolute top-6 right-6 text-[10px] font-bold text-green-600 bg-green-50 px-2 py-1 rounded uppercase tracking-widest">+12.5%</span>
          </div>
          <div className="border border-neutral-200 p-6 rounded-xl flex flex-col gap-2 shadow-sm relative">
            <span className="text-xs font-bold text-neutral-500 uppercase tracking-widest">Avg Confidence</span>
            <span className="text-4xl font-black">{data.stats.avg_confidence}</span>
            <span className="absolute top-6 right-6 text-[10px] font-bold text-blue-600 bg-blue-50 px-2 py-1 rounded uppercase tracking-widest">STABLE</span>
          </div>
          <div className="border border-neutral-200 p-6 rounded-xl flex flex-col gap-2 shadow-sm relative">
            <span className="text-xs font-bold text-neutral-500 uppercase tracking-widest">Active Users</span>
            <span className="text-4xl font-black">{data.stats.active_users}</span>
          </div>
          <div className="border border-neutral-200 p-6 rounded-xl flex flex-col gap-2 shadow-sm relative">
            <span className="text-xs font-bold text-neutral-500 uppercase tracking-widest">System Latency</span>
            <span className="text-4xl font-black">{data.stats.system_latency}</span>
            <span className="absolute top-6 right-6 text-[10px] font-bold text-green-600 bg-green-50 px-2 py-1 rounded uppercase tracking-widest">OPTIMIZED</span>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Query Velocity Chart */}
          <div className="col-span-1 lg:col-span-2 border border-neutral-200 p-6 rounded-xl shadow-sm">
            <div className="flex items-center justify-between mb-8">
              <h3 className="text-sm font-bold text-neutral-800 flex items-center gap-2">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M2 12h4l3-9 5 18 3-9h5"/></svg>
                Query Velocity
              </h3>
              <select className="text-xs border border-neutral-200 rounded-md px-2 py-1 text-neutral-500 font-medium outline-none">
                <option>Last 7 Days</option>
              </select>
            </div>
            
            <div className="h-[300px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={data.query_velocity} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorVelocity" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#2563eb" stopOpacity={0.2}/>
                      <stop offset="95%" stopColor="#2563eb" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f5f5f5" />
                  <XAxis dataKey="day" axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: '#a3a3a3' }} dy={10} />
                  <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: '#a3a3a3' }} />
                  <Tooltip 
                    contentStyle={{ borderRadius: '8px', border: '1px solid #e5e5e5', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                  />
                  <Area 
                    type="monotone" 
                    dataKey="queries" 
                    stroke="#2563eb" 
                    strokeWidth={3}
                    fillOpacity={1} 
                    fill="url(#colorVelocity)" 
                    activeDot={{ r: 6, fill: '#2563eb', stroke: '#fff', strokeWidth: 2 }}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Top Intent Patterns Chart */}
          <div className="col-span-1 lg:col-span-1 border border-neutral-200 p-6 rounded-xl shadow-sm">
            <h3 className="text-sm font-bold text-neutral-800 flex items-center gap-2 mb-8">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
              Top Intent Patterns
            </h3>
            <div className="h-[300px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data.top_terms} layout="vertical" margin={{ top: 0, right: 20, left: 20, bottom: 0 }}>
                  <XAxis type="number" hide />
                  <YAxis dataKey="term" type="category" axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: '#525252', fontWeight: 600 }} width={110} />
                  <Tooltip 
                    cursor={{ fill: '#f5f5f5' }}
                    contentStyle={{ borderRadius: '8px', border: '1px solid #e5e5e5', fontSize: '12px' }}
                  />
                  <Bar dataKey="count" radius={[0, 4, 4, 0]} barSize={24}>
                    {data.top_terms.map((entry: any, index: number) => (
                      <Cell key={`cell-${index}`} fill={index === 0 ? '#2563eb' : '#a3a3a3'} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

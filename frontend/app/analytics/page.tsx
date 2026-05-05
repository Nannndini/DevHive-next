"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
} from "recharts";
import { Activity, ShieldCheck, Search, Zap } from "lucide-react";

const COLORS = ["#00f0ff", "#7000ff", "#ff003c"];

export default function StatsDashboard() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/analytics/dashboard")
      .then((res) => res.json())
      .then((json) => {
        setData(json);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to load analytics", err);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-black text-cyan-400 flex items-center justify-center font-mono">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ repeat: Infinity, duration: 1, ease: "linear" }}
        >
          <Zap size={48} className="text-cyan-500 drop-shadow-[0_0_15px_rgba(0,240,255,0.8)]" />
        </motion.div>
      </div>
    );
  }

  if (!data) return <div className="text-red-500 p-8 font-mono">SYSTEM FAILURE: Analytics unreachable.</div>;

  return (
    <div className="min-h-screen bg-black text-white p-8 font-mono relative overflow-hidden">
      {/* Cyberpunk Grid Background */}
      <div className="absolute inset-0 bg-[linear-gradient(rgba(0,240,255,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(0,240,255,0.03)_1px,transparent_1px)] bg-[size:30px_30px] z-0 pointer-events-none" />
      
      <div className="relative z-10 max-w-7xl mx-auto space-y-8">
        <motion.header
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="border-b border-cyan-900 pb-4 flex items-center justify-between"
        >
          <div>
            <h1 className="text-4xl font-black tracking-tighter text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-purple-600 drop-shadow-[0_0_10px_rgba(0,240,255,0.3)] uppercase">
              Neural Analytics Core
            </h1>
            <p className="text-cyan-600/80 mt-1 text-sm">System telemetry and query velocity monitoring</p>
          </div>
          <div className="flex gap-4">
            <div className="flex items-center gap-2 px-4 py-2 bg-cyan-950/30 border border-cyan-800 rounded-sm">
              <div className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
              <span className="text-cyan-400 text-xs tracking-widest">SYSTEM_ONLINE</span>
            </div>
          </div>
        </motion.header>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Query Velocity Chart */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.1 }}
            className="col-span-1 lg:col-span-2 bg-gray-900/40 backdrop-blur-md border border-cyan-900/50 p-6 rounded-xl relative group"
          >
            <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/5 to-purple-500/5 opacity-0 group-hover:opacity-100 transition-opacity rounded-xl" />
            <h3 className="flex items-center gap-2 text-xl font-bold text-cyan-50 mb-6 uppercase tracking-wider">
              <Activity className="text-cyan-400" /> Query Velocity (30 Days)
            </h3>
            <div className="h-[300px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={data.query_velocity}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" vertical={false} />
                  <XAxis dataKey="day" stroke="#4b5563" tick={{ fill: '#9ca3af' }} />
                  <YAxis stroke="#4b5563" tick={{ fill: '#9ca3af' }} />
                  <Tooltip
                    contentStyle={{ backgroundColor: 'rgba(17, 24, 39, 0.9)', borderColor: '#0891b2', color: '#fff' }}
                    itemStyle={{ color: '#22d3ee' }}
                  />
                  <Line
                    type="monotone"
                    dataKey="queries"
                    stroke="#00f0ff"
                    strokeWidth={3}
                    dot={{ fill: '#00f0ff', strokeWidth: 2, r: 4 }}
                    activeDot={{ r: 8, stroke: '#fff', strokeWidth: 2 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </motion.div>

          {/* Confidence Scores */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2 }}
            className="bg-gray-900/40 backdrop-blur-md border border-purple-900/50 p-6 rounded-xl relative group"
          >
            <div className="absolute inset-0 bg-gradient-to-br from-purple-500/5 to-pink-500/5 opacity-0 group-hover:opacity-100 transition-opacity rounded-xl" />
            <h3 className="flex items-center gap-2 text-xl font-bold text-purple-50 mb-6 uppercase tracking-wider">
              <ShieldCheck className="text-purple-400" /> Embed Confidence
            </h3>
            <div className="h-[300px] w-full flex items-center justify-center relative">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={data.confidence_scores}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={5}
                    dataKey="value"
                    stroke="none"
                  >
                    {data.confidence_scores.map((entry: any, index: number) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{ backgroundColor: 'rgba(17, 24, 39, 0.9)', borderColor: '#9333ea', borderRadius: '8px' }}
                  />
                </PieChart>
              </ResponsiveContainer>
              <div className="absolute pointer-events-none inset-0 flex items-center justify-center flex-col">
                 <span className="text-3xl font-black text-white drop-shadow-[0_0_10px_rgba(255,255,255,0.8)]">
                    {data.confidence_scores[0].value}
                 </span>
                 <span className="text-xs text-gray-400">HIGH CONF.</span>
              </div>
            </div>
          </motion.div>

          {/* Top Search Terms */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="col-span-1 lg:col-span-3 bg-gray-900/40 backdrop-blur-md border border-pink-900/50 p-6 rounded-xl relative group"
          >
             <div className="absolute inset-0 bg-gradient-to-t from-pink-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity rounded-xl" />
            <h3 className="flex items-center gap-2 text-xl font-bold text-pink-50 mb-6 uppercase tracking-wider">
              <Search className="text-pink-400" /> Top System Inquiries
            </h3>
            <div className="h-[300px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data.top_terms} layout="vertical" margin={{ top: 5, right: 30, left: 40, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" horizontal={true} vertical={false} />
                  <XAxis type="number" stroke="#4b5563" />
                  <YAxis dataKey="term" type="category" width={150} stroke="#9ca3af" tick={{ fill: '#d1d5db', fontSize: 12 }} />
                  <Tooltip
                    cursor={{ fill: 'rgba(236, 72, 153, 0.1)' }}
                    contentStyle={{ backgroundColor: 'rgba(17, 24, 39, 0.9)', borderColor: '#ec4899' }}
                  />
                  <Bar dataKey="count" fill="#ff003c" radius={[0, 4, 4, 0]} barSize={20}>
                    {data.top_terms.map((entry: any, index: number) => (
                      <Cell key={`cell-${index}`} fill={index % 2 === 0 ? '#ff003c' : '#b2002a'} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </motion.div>

        </div>
      </div>
    </div>
  );
}

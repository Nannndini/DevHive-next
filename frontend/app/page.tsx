"use client";
import Link from "next/link";
import { motion } from "framer-motion";
import { useEffect, useState } from "react";

export default function Home() {
  const [status, setStatus] = useState("Checking neural link...");

  useEffect(() => {
    fetch("http://127.0.0.1:8000/")
      .then((res) => {
        if (res.ok) setStatus("BACKEND: ONLINE");
        else setStatus("BACKEND: ERROR");
      })
      .catch(() => setStatus("BACKEND: OFFLINE"));
  }, []);

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-black text-cyan-400 font-mono relative overflow-hidden">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-cyan-900/20 via-black to-black z-0" />
      
      <div className="relative z-10 text-center space-y-8">
        <motion.h1 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-6xl font-black tracking-tighter text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-purple-600 drop-shadow-[0_0_15px_rgba(0,240,255,0.4)] uppercase"
        >
          DevHive Core
        </motion.h1>

        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className={`px-4 py-2 border ${status.includes("ONLINE") ? "border-green-500 text-green-400" : "border-red-500 text-red-400"} inline-block bg-black/50 backdrop-blur`}
        >
          {status}
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="flex flex-col sm:flex-row gap-6 mt-12 justify-center"
        >
          <Link href="/admin" className="px-8 py-4 bg-cyan-950/50 border border-cyan-500 text-cyan-400 hover:bg-cyan-500 hover:text-black hover:shadow-[0_0_20px_rgba(0,240,255,0.5)] transition-all uppercase tracking-widest font-bold">
            Ingestion Terminal
          </Link>
          <Link href="/stats" className="px-8 py-4 bg-purple-950/50 border border-purple-500 text-purple-400 hover:bg-purple-500 hover:text-black hover:shadow-[0_0_20px_rgba(168,85,247,0.5)] transition-all uppercase tracking-widest font-bold">
            Analytics Node
          </Link>
        </motion.div>
      </div>
    </div>
  );
}
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function Login() {
  const [email, setEmail] = useState("admin@devhive.ai");
  const [password, setPassword] = useState("password");
  const [error, setError] = useState("");
  const router = useRouter();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      const data = await res.json();
      
      if (res.ok) {
        document.cookie = `token=${data.token}; path=/`;
        document.cookie = `role=${data.user.role}; path=/`;
        router.push("/");
      } else {
        setError(data.detail || "Login failed");
      }
    } catch (err) {
      setError("Network error");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-black font-sans text-white">
      <div className="w-full max-w-md p-8 flex flex-col gap-10">
        
        {/* Header */}
        <div className="text-center flex flex-col gap-2">
          <h1 className="text-5xl font-black tracking-tight" style={{ fontFamily: 'Arial Black, impact, sans-serif' }}>
            DEVHIVE
          </h1>
          <p className="text-[10px] font-bold tracking-[0.4em] text-white">
            ENTERPRISE ACCESS PORTAL
          </p>
        </div>
        
        {error && <div className="text-red-500 text-sm border border-red-500 p-2 bg-red-900/20 text-center">{error}</div>}
        
        {/* Form */}
        <form onSubmit={handleLogin} className="flex flex-col gap-6">
          <div className="flex flex-col gap-2">
            <label className="text-sm font-bold tracking-widest uppercase">Identity</label>
            <input 
              type="email" 
              value={email} 
              onChange={e => setEmail(e.target.value)} 
              className="w-full bg-[#EBF0FA] text-black p-4 rounded-xl outline-none font-medium text-lg focus:ring-2 focus:ring-white transition-all" 
              required 
            />
          </div>
          
          <div className="flex flex-col gap-2">
            <label className="text-sm font-bold tracking-widest uppercase">Protocol Key</label>
            <input 
              type="password" 
              value={password} 
              onChange={e => setPassword(e.target.value)} 
              className="w-full bg-[#EBF0FA] text-black p-4 rounded-xl outline-none font-medium text-lg focus:ring-2 focus:ring-white transition-all tracking-widest" 
              required 
            />
          </div>

          <div className="flex flex-col gap-4 mt-4">
            <button type="submit" className="w-full bg-white text-black p-4 rounded-xl font-bold uppercase tracking-widest text-sm hover:bg-gray-200 transition-colors">
              Authenticate
            </button>
            <button type="button" onClick={() => router.push('/register')} className="w-full bg-black text-white p-4 rounded-xl border border-neutral-800 font-bold uppercase tracking-widest text-sm hover:bg-neutral-900 transition-colors">
              Request Access
            </button>
          </div>
        </form>

      </div>
    </div>
  );
}

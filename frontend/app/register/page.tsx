"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function Register() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [error, setError] = useState("");
  const router = useRouter();

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || ""}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password, full_name: fullName }),
      });
      const data = await res.json();
      
      if (res.ok) {
        document.cookie = `token=${data.token}; path=/`;
        document.cookie = `role=${data.user.role}; path=/`;
        router.push("/dashboard");
      } else {
        setError(data.detail || "Registration failed");
      }
    } catch (err) {
      setError("Network error");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-black text-cyan-400 font-mono">
      <form onSubmit={handleRegister} className="bg-gray-900/50 p-8 rounded border border-cyan-900 w-96">
        <h1 className="text-2xl font-bold mb-6">Initialize User</h1>
        {error && <div className="text-red-500 mb-4">{error}</div>}
        <input 
          type="text" 
          value={fullName} 
          onChange={e => setFullName(e.target.value)} 
          placeholder="Full Name" 
          className="w-full bg-black border border-cyan-800 p-2 mb-4 text-white" 
          required 
        />
        <input 
          type="email" 
          value={email} 
          onChange={e => setEmail(e.target.value)} 
          placeholder="Email" 
          className="w-full bg-black border border-cyan-800 p-2 mb-4 text-white" 
          required 
        />
        <input 
          type="password" 
          value={password} 
          onChange={e => setPassword(e.target.value)} 
          placeholder="Password" 
          className="w-full bg-black border border-cyan-800 p-2 mb-6 text-white" 
          required 
        />
        <button type="submit" className="w-full bg-cyan-900 hover:bg-cyan-700 p-2 text-white font-bold">REGISTER</button>
      </form>
    </div>
  );
}

"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Upload, FileText, CheckCircle, AlertTriangle, Zap } from "lucide-react";

export default function AdminIngestion() {
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<"idle" | "uploading" | "success" | "error">("idle");
  const [message, setMessage] = useState("");

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
      setStatus("idle");
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setStatus("uploading");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("http://127.0.0.1:8000/ingest", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();

      if (res.ok) {
        setStatus("success");
        setMessage(data.message || "File dispatched for neural processing.");
      } else {
        setStatus("error");
        setMessage(data.detail || "Ingestion pipeline failure.");
      }
    } catch (err) {
      setStatus("error");
      setMessage("Network connection severed. Check backend status.");
    }
  };

  return (
    <div className="min-h-screen bg-black text-white p-8 font-mono relative overflow-hidden">
      {/* Background FX */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-cyan-900/20 via-black to-black z-0 pointer-events-none" />

      <div className="relative z-10 max-w-4xl mx-auto space-y-12 mt-12">
        <motion.header
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="border-l-4 border-cyan-400 pl-6 py-2"
        >
          <h1 className="text-4xl font-black tracking-tighter uppercase text-white">
            Data Ingestion <span className="text-cyan-400">Terminal</span>
          </h1>
          <p className="text-cyan-600/80 mt-2 text-sm max-w-lg">
            Upload raw unstructured data. Background workers will chunk, embed, and map the context into the neural vector space.
          </p>
        </motion.header>

        <motion.div
          initial={{ opacity: 0, scale: 0.98 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1 }}
          className="bg-gray-900/40 backdrop-blur-md border border-cyan-900/50 p-10 rounded-xl relative overflow-hidden group"
        >
          <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/5 to-purple-500/5 opacity-0 group-hover:opacity-100 transition-opacity" />

          <div className="flex flex-col items-center justify-center border-2 border-dashed border-cyan-900/50 rounded-lg p-12 bg-black/50 hover:bg-cyan-950/10 transition-colors relative z-10">
            <input
              type="file"
              onChange={handleFileChange}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            />
            {file ? (
              <div className="flex flex-col items-center text-cyan-400">
                <FileText size={48} className="mb-4" />
                <p className="text-lg font-bold">{file.name}</p>
                <p className="text-sm text-cyan-700 mt-1">{(file.size / 1024).toFixed(2)} KB</p>
              </div>
            ) : (
              <div className="flex flex-col items-center text-cyan-700 group-hover:text-cyan-500 transition-colors">
                <Upload size={48} className="mb-4" />
                <p className="text-lg font-bold">DRAG & DROP SECURE FILES</p>
                <p className="text-sm mt-1">or click to browse local directory</p>
              </div>
            )}
          </div>

          <div className="mt-8 flex items-center justify-between">
            <div className="flex items-center gap-3">
              {status === "success" && (
                <motion.div initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} className="flex items-center gap-2 text-green-400 bg-green-400/10 px-4 py-2 rounded border border-green-400/20">
                  <CheckCircle size={18} /> {message}
                </motion.div>
              )}
              {status === "error" && (
                <motion.div initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} className="flex items-center gap-2 text-red-400 bg-red-400/10 px-4 py-2 rounded border border-red-400/20">
                  <AlertTriangle size={18} /> {message}
                </motion.div>
              )}
              {status === "uploading" && (
                <div className="flex items-center gap-2 text-cyan-400">
                  <Zap size={18} className="animate-pulse" /> Initiating background sequence...
                </div>
              )}
            </div>

            <button
              onClick={handleUpload}
              disabled={!file || status === "uploading"}
              className="relative px-8 py-3 bg-cyan-950 text-cyan-400 font-bold uppercase tracking-widest border border-cyan-500 hover:bg-cyan-500 hover:text-black transition-all disabled:opacity-50 disabled:cursor-not-allowed group overflow-hidden"
            >
              <div className="absolute inset-0 bg-cyan-400 translate-y-full group-hover:translate-y-0 transition-transform duration-300 ease-out z-0" />
              <span className="relative z-10">{status === "uploading" ? "PROCESSING..." : "INITIALIZE UPLOAD"}</span>
            </button>
          </div>
        </motion.div>
      </div>
    </div>
  );
}

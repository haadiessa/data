"use client";

import { useState, useEffect } from "react";
import { Search, Download, RefreshCw, Briefcase, Globe, Mail, Phone, User, CheckCircle, AlertCircle, XCircle } from "lucide-react";

const API_BASE = typeof window !== "undefined" ? window.location.origin : "";

interface Lead {
  company_name: string;
  website: string;
  name: string;
  role: string;
  profile_url: string;
  email: string;
  email_status: string; // "verified", "risky", "invalid" وغیرہ
  verified_score: number;
  lead_score: number;
  phone: string;
}

export default function Dashboard() {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState({ niche: "", location: "" });
  const [jobStatus, setJobStatus] = useState<string | null>(null);

  const fetchLeads = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/leads`);
      if (!res.ok) throw new Error("Backend not responding");
      const data = await res.json();
      setLeads(data.data || []);
    } catch (error) {
      console.error("Error fetching leads:", error);
    }
  };

  useEffect(() => {
    fetchLeads();
    const interval = setInterval(fetchLeads, 10000);
    return () => clearInterval(interval);
  }, []);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setJobStatus("Searching... Please wait.");
    try {
      const res = await fetch(`${API_BASE}/api/leads/search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(searchQuery),
      });
      const data = await res.json();
      if (data.job_id) {
        setJobStatus(`Search started! Looking for leads...`);
      }
      setTimeout(() => setJobStatus(null), 5000);
    } catch (error) {
      setJobStatus("Error: Could not start search.");
    } finally {
      setLoading(false);
    }
  };

  const handleExport = () => {
    window.open(`${API_BASE}/api/leads/export`, "_blank");
  };

  // ای میل اسٹیٹس کے لیے رنگین بیج کا فنکشن
  const renderStatusBadge = (status: string) => {
    const s = status?.toLowerCase();
    if (s === "verified" || s === "deliverable") {
      return <span className="flex items-center gap-1 text-[10px] font-bold uppercase px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"><CheckCircle className="w-3 h-3" /> Verified</span>;
    } else if (s === "risky" || s === "catch-all") {
      return <span className="flex items-center gap-1 text-[10px] font-bold uppercase px-2 py-0.5 rounded bg-amber-500/20 text-amber-400 border border-amber-500/30"><AlertCircle className="w-3 h-3" /> Risky</span>;
    } else {
      return <span className="flex items-center gap-1 text-[10px] font-bold uppercase px-2 py-0.5 rounded bg-rose-500/20 text-rose-400 border border-rose-500/30"><XCircle className="w-3 h-3" /> Invalid</span>;
    }
  };

  return (
    <main className="min-h-screen p-8 max-w-7xl mx-auto">
      <div className="flex justify-between items-center mb-12">
        <div>
          <h1 className="text-4xl font-bold gradient-text mb-2">LeadGen AI</h1>
          <p className="text-gray-400 font-medium">Core Intelligence Discovery Dashboard</p>
        </div>
        <div className="flex gap-4">
          <button onClick={fetchLeads} className="p-3 glass-card hover:bg-white/10 transition-all active:scale-95">
            <RefreshCw className={`w-5 h-5 text-indigo-400 ${loading ? "animate-spin" : ""}`} />
          </button>
          <button onClick={handleExport} className="flex items-center gap-2 px-6 py-3 btn-primary rounded-xl font-bold shadow-lg shadow-indigo-500/20 transition-all active:scale-95">
            <Download className="w-5 h-5" />
            Export CSV
          </button>
        </div>
      </div>

      <section className="glass-card p-8 mb-12 border border-white/5">
        <form onSubmit={handleSearch} className="flex flex-wrap gap-6 items-end">
          <div className="flex-1 min-w-[240px]">
            <label className="block text-sm font-semibold text-gray-400 mb-2">Business Niche</label>
            <div className="relative">
              <Briefcase className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
              <input 
                type="text" 
                placeholder="e.g. Real Estate, SaaS"
                value={searchQuery.niche}
                onChange={(e) => setSearchQuery({...searchQuery, niche: e.target.value})}
                className="w-full bg-black/40 border border-white/10 rounded-xl py-3.5 pl-12 pr-4 focus:ring-2 focus:ring-indigo-500 outline-none transition-all placeholder:text-gray-600"
                required
              />
            </div>
          </div>
          <div className="flex-1 min-w-[240px]">
            <label className="block text-sm font-semibold text-gray-400 mb-2">Location</label>
            <div className="relative">
              <Globe className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
              <input 
                type="text" 
                placeholder="e.g. New York, London"
                value={searchQuery.location}
                onChange={(e) => setSearchQuery({...searchQuery, location: e.target.value})}
                className="w-full bg-black/40 border border-white/10 rounded-xl py-3.5 pl-12 pr-4 focus:ring-2 focus:ring-indigo-500 outline-none transition-all placeholder:text-gray-600"
                required
              />
            </div>
          </div>
          <button type="submit" disabled={loading} className="px-10 py-3.5 btn-primary rounded-xl font-bold flex items-center gap-3 transition-all hover:brightness-110 disabled:opacity-50">
            {loading ? <RefreshCw className="w-5 h-5 animate-spin" /> : <Search className="w-5 h-5" />}
            Discover Leads
          </button>
        </form>
        {jobStatus && <div className="mt-4 text-sm text-indigo-300 font-medium animate-pulse flex items-center gap-2"><div className="w-2 h-2 bg-indigo-400 rounded-full"></div> {jobStatus}</div>}
      </section>

      <div className="glass-card overflow-hidden border border-white/5 shadow-2xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-white/5 border-b border-white/10">
                <th className="px-6 py-5 font-bold text-gray-300 uppercase text-xs tracking-wider">Company</th>
                <th className="px-6 py-5 font-bold text-gray-300 uppercase text-xs tracking-wider">Decision Maker</th>
                <th className="px-6 py-5 font-bold text-gray-300 uppercase text-xs tracking-wider">Contact & Status</th>
                <th className="px-6 py-5 font-bold text-gray-300 uppercase text-xs tracking-wider text-center">Score</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {leads.length > 0 ? leads.map((lead, idx) => (
                <tr key={idx} className="hover:bg-white/[0.03] transition-colors group">
                  <td className="px-6 py-6">
                    <div className="font-bold text-white text-lg group-hover:text-indigo-300 transition-colors">{lead.company_name}</div>
                    <div className="flex items-center text-sm text-gray-500 gap-1.5 mt-1">
                      <Globe className="w-3.5 h-3.5" />
                      <a href={lead.website} target="_blank" className="hover:underline decoration-indigo-500 underline-offset-4">{lead.website}</a>
                    </div>
                  </td>
                  <td className="px-6 py-6">
                    <div className="flex items-center gap-2.5 mb-1.5">
                      <div className="p-1.5 rounded-lg bg-indigo-500/10 text-indigo-400"><User className="w-4 h-4" /></div>
                      <span className="font-semibold text-gray-200">{lead.name || "N/A"}</span>
                    </div>
                    <div className="text-xs text-gray-500 font-medium ml-9">{lead.role || "Professional"}</div>
                  </td>
                  <td className="px-6 py-6">
                    <div className="flex flex-col gap-2.5">
                      <div className="flex items-center gap-3">
                        <div className="flex items-center gap-2 text-gray-300 bg-white/5 px-3 py-1 rounded-lg border border-white/5">
                          <Mail className="w-3.5 h-3.5 text-gray-500" />
                          <span className="text-sm font-medium">{lead.email}</span>
                        </div>
                        {renderStatusBadge(lead.email_status)}
                      </div>
                      {lead.phone && (
                        <div className="flex items-center gap-2 text-sm text-gray-400 ml-1">
                          <Phone className="w-3.5 h-3.5 text-indigo-400/50" />
                          <span>{lead.phone}</span>
                        </div>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-6 text-center">
                    <div className="inline-flex flex-col items-center">
                       <span className={`text-lg font-black ${lead.lead_score > 70 ? "text-emerald-400" : "text-indigo-400"}`}>
                        {lead.lead_score}%
                      </span>
                      <div className="w-12 h-1 bg-white/10 rounded-full mt-1 overflow-hidden">
                        <div className="h-full bg-indigo-500" style={{ width: `${lead.lead_score}%` }}></div>
                      </div>
                    </div>
                  </td>
                </tr>
              )) : (
                <tr>
                  <td colSpan={4} className="px-6 py-20 text-center">
                    <div className="flex flex-col items-center gap-3">
                      <div className="p-4 rounded-full bg-white/5 text-gray-600"><Search className="w-8 h-8" /></div>
                      <p className="text-gray-500 font-medium italic">No leads found. Enter a niche and location to begin discovery.</p>
                    </div>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </main>
  );
}
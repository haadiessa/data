"use client";

import { useState, useEffect } from "react";
import { Search, Download, RefreshCw, CheckCircle, AlertCircle, ExternalLink, Briefcase, Globe, Mail, Phone, User } from "lucide-react";

// آپ کا نیا لائیو بیک اینڈ لنک یہاں سیٹ کر دیا گیا ہے
const API_BASE = "https://data-one-red.vercel.app";

interface Lead {
  company_name: string;
  website: string;
  name: string;
  role: string;
  profile_url: string;
  email: string;
  email_status: string;
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
      const data = await res.json();
      setLeads(data.data || []);
    } catch (error) {
      console.error("Error fetching leads:", error);
    }
  };

  useEffect(() => {
    fetchLeads();
    const interval = setInterval(fetchLeads, 10000); // Poll every 10s
    return () => clearInterval(interval);
  }, []);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setJobStatus("Starting search...");
    try {
      const res = await fetch(`${API_BASE}/api/leads/search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(searchQuery),
      });
      const data = await res.json();
      setJobStatus(`Search started! Job ID: ${data.job_id}`);
      setTimeout(() => setJobStatus(null), 5000);
    } catch (error) {
      setJobStatus("Error starting search.");
    } finally {
      setLoading(false);
    }
  };

  const handleExport = () => {
    window.open(`${API_BASE}/api/leads/export`, "_blank");
  };

  return (
    <main className="min-h-screen p-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex justify-between items-center mb-12">
        <div>
          <h1 className="text-4xl font-bold gradient-text mb-2">LeadGen AI</h1>
          <p className="text-gray-400">Core Intelligence Discovery Dashboard</p>
        </div>
        <div className="flex gap-4">
          <button 
            onClick={fetchLeads}
            className="p-3 glass-card hover:bg-white/10 transition-colors"
          >
            <RefreshCw className="w-5 h-5 text-indigo-400" />
          </button>
          <button 
            onClick={handleExport}
            className="flex items-center gap-2 px-6 py-3 btn-primary rounded-xl font-semibold"
          >
            <Download className="w-5 h-5" />
            Export CSV
          </button>
        </div>
      </div>

      {/* Search Section */}
      <section className="glass-card p-8 mb-12">
        <form onSubmit={handleSearch} className="flex flex-wrap gap-6 items-end">
          <div className="flex-1 min-w-[240px]">
            <label className="block text-sm font-medium text-gray-400 mb-2">Business Niche</label>
            <div className="relative">
              <Briefcase className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
              <input 
                type="text" 
                placeholder="e.g. Real Estate, SaaS"
                value={searchQuery.niche}
                onChange={(e) => setSearchQuery({...searchQuery, niche: e.target.value})}
                className="w-full bg-black/30 border border-white/10 rounded-xl py-3 pl-12 pr-4 focus:ring-2 focus:ring-indigo-500 outline-none transition-all"
                required
              />
            </div>
          </div>
          <div className="flex-1 min-w-[240px]">
            <label className="block text-sm font-medium text-gray-400 mb-2">Location</label>
            <div className="relative">
              <Globe className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
              <input 
                type="text" 
                placeholder="e.g. New York, London"
                value={searchQuery.location}
                onChange={(e) => setSearchQuery({...searchQuery, location: e.target.value})}
                className="w-full bg-black/30 border border-white/10 rounded-xl py-3 pl-12 pr-4 focus:ring-2 focus:ring-indigo-500 outline-none transition-all"
                required
              />
            </div>
          </div>
          <button 
            type="submit" 
            disabled={loading}
            className="px-8 py-3 btn-primary rounded-xl font-bold flex items-center gap-3 disabled:opacity-50"
          >
            {loading ? <RefreshCw className="w-5 h-5 animate-spin" /> : <Search className="w-5 h-5" />}
            Discover Leads
          </button>
        </form>
        {jobStatus && (
          <div className="mt-4 text-sm text-indigo-300 animate-pulse">
            {jobStatus}
          </div>
        )}
      </section>

      {/* Leads Table */}
      <div className="glass-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="table-header border-b border-white/10">
                <th className="px-6 py-4 font-semibold text-gray-300">Company</th>
                <th className="px-6 py-4 font-semibold text-gray-300">Decision Maker</th>
                <th className="px-6 py-4 font-semibold text-gray-300">Contact Details</th>
                <th className="px-6 py-4 font-semibold text-gray-300">Lead Score</th>
                <th className="px-6 py-4 font-semibold text-gray-300">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {leads.map((lead, idx) => (
                <tr key={idx} className="hover:bg-white/5 transition-colors">
                  <td className="px-6 py-5">
                    <div className="font-bold text-white mb-1">{lead.company_name}</div>
                    <div className="flex items-center text-xs text-gray-400 gap-1">
                      <Globe className="w-3 h-3" />
                      <a href={lead.website} target="_blank" className="hover:text-indigo-400">{lead.website}</a>
                    </div>
                  </td>
                  <td className="px-6 py-5">
                    <div className="flex items-center gap-2 mb-1">
                      <User className="w-4 h-4 text-indigo-400" />
                      <span className="font-medium text-gray-200">{lead.name || "N/A"}</span>
                    </div>
                    <div className="text-xs text-gray-400 pl-6">{lead.role || "N/A"}</div>
                  </td>
                  <td className="px-6 py-5">
                    <div className="flex flex-col gap-2">
                      <div className="flex items-center gap-2 text-sm">
                        <Mail className="w-4 h-4 text-gray-400" />
                        <span className={lead.email_status === "VERIFIED" ? "text-emerald-400" : "text-amber-400"}>
                          {lead.email}
                        </span>
                        {lead.email_status === "VERIFIED" ? 
                          <CheckCircle className="w-3 h-3 text-emerald-500" /> : 
                          <AlertCircle className="w-3 h-3 text-amber-500" />
                        }
                      </div>
                      {lead.phone && (
                        <div className="flex items-center gap-2 text-sm text-gray-400">
                          <Phone className="w-4 h-4" />
                          {lead.phone}
                        </div>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-5">
                    <div className="flex items-center gap-2">
                      <div className="w-full bg-white/10 h-2 rounded-full min-w-[100px] overflow-hidden">
                        <div 
                          className={`h-full rounded-full ${lead.lead_score > 70 ? 'bg-emerald-500' : 'bg-indigo-500'}`}
                          style={{ width: `${lead.lead_score}%` }}
                        />
                      </div>
                      <span className="font-bold text-gray-200">{lead.lead_score}</span>
                    </div>
                  </td>
                  <td className="px-6 py-5">
                    {lead.profile_url && (
                      <a 
                        href={lead.profile_url} 
                        target="_blank"
                        className="p-2 glass-card hover:bg-white/10 transition-colors inline-block"
                      >
                        <ExternalLink className="w-4 h-4 text-gray-400" />
                      </a>
                    )}
                  </td>
                </tr>
              ))}
              {leads.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-6 py-20 text-center text-gray-500">
                    No leads found yet. Start a discovery search to populate the table.
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
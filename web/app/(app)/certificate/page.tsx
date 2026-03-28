"use client";

import { useState } from "react";
import Link from "next/link";
import { generateCOS } from "@/lib/api";

export default function CertificatePage() {
  const [attorney, setAttorney] = useState("");
  const [caseNum, setCaseNum] = useState("");
  const [recipients, setRecipients] = useState([{ name: "", attorney_name: "", method: "CM/ECF" }]);
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);

  const addRecipient = () => setRecipients([...recipients, { name: "", attorney_name: "", method: "CM/ECF" }]);
  const removeRecipient = (i: number) => setRecipients(recipients.filter((_, j) => j !== i));
  const updateRecipient = (i: number, field: string, value: string) => {
    setRecipients(recipients.map((r, j) => j === i ? { ...r, [field]: value } : r));
  };

  const generate = async () => {
    setLoading(true);
    try {
      const res = await generateCOS(attorney, caseNum, recipients.filter((r) => r.name || r.attorney_name));
      setText(res.text);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#f5f3ee]">
      <header className="bg-white border-b border-[#e8e5e0] sticky top-0 z-50">
        <div className="max-w-4xl mx-auto px-5 sm:px-6 h-14 flex items-center justify-between">
          <div className="flex items-center gap-4 sm:gap-6">
            <Link href="/file" className="flex items-center gap-2.5">
              <div className="w-7 h-7 bg-gradient-to-br from-[#1e3a5f] to-[#0f2440] rounded-lg flex items-center justify-center text-white text-[10px] font-bold">E</div>
              <span className="text-[15px] font-semibold tracking-tight text-[#1a1a1a] hidden sm:inline">ECFiler</span>
            </Link>
            <div className="h-5 w-px bg-[#e8e5e0]" />
            <span className="text-[13px] text-[#525252] font-medium">Certificate of Service</span>
          </div>
          <Link href="/file" className="text-[13px] text-[#1e3a5f] hover:text-[#162a47] transition font-medium">&larr; Back to Filing</Link>
        </div>
      </header>

      <div className="max-w-3xl mx-auto px-5 sm:px-6 py-8">
        {/* Info banner */}
        <div className="flex items-start gap-3 px-4 py-3 bg-[#f0f4fa] border border-[#bfdbfe] rounded-xl text-[12px] text-[#1e40af] mb-6">
          <svg className="w-4 h-4 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z" />
          </svg>
          <div>
            <span className="font-semibold">Certificate of Service is built into the filing flow.</span>{" "}
            Toggle it on in the review screen when <Link href="/file" className="underline font-semibold">filing a document</Link>. Use this page for standalone generation.
          </div>
        </div>

        <h1 className="text-[22px] font-bold tracking-tight text-[#1a1a1a] mb-1">Generate Certificate of Service</h1>
        <p className="text-[13px] text-[#525252] mb-6">Create a properly formatted certificate for federal court filing.</p>

        {/* Form */}
        <div className="bg-white border border-[#e8e5e0] rounded-2xl overflow-hidden shadow-sm mb-6">
          <div className="px-5 py-3 border-b border-[#f0eee9] bg-[#fafaf8]">
            <span className="text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide">Filing Information</span>
          </div>
          <div className="p-5">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-5">
              <div>
                <label className="block text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide mb-1.5">Attorney Name</label>
                <input type="text" value={attorney} onChange={(e) => setAttorney(e.target.value)} placeholder="Jane Smith, Esq." className="w-full px-3 py-2.5 border border-[#e8e5e0] rounded-xl text-[13px] outline-none focus:border-[#1e3a5f] focus:ring-2 focus:ring-[#1e3a5f]/10" />
              </div>
              <div>
                <label className="block text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide mb-1.5">Case Number</label>
                <input type="text" value={caseNum} onChange={(e) => setCaseNum(e.target.value)} placeholder="1:24-cv-01234-ABC" className="w-full px-3 py-2.5 border border-[#e8e5e0] rounded-xl text-[13px] font-mono outline-none focus:border-[#1e3a5f] focus:ring-2 focus:ring-[#1e3a5f]/10" />
              </div>
            </div>

            <div className="mb-5">
              <div className="flex items-center justify-between mb-3">
                <label className="text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide">Service Recipients</label>
                <button onClick={addRecipient} className="text-[11px] text-[#1e3a5f] font-semibold hover:underline">+ Add Recipient</button>
              </div>
              <div className="space-y-2">
                {recipients.map((r, i) => (
                  <div key={i} className="flex items-center gap-2 p-3 bg-[#fafaf8] border border-[#f0eee9] rounded-xl">
                    <div className="w-7 h-7 bg-[#e8e5e0] rounded-lg flex items-center justify-center text-[10px] font-bold text-[#8a8a8a] shrink-0">{i + 1}</div>
                    <input type="text" value={r.name} onChange={(e) => updateRecipient(i, "name", e.target.value)} placeholder="Party name" className="flex-1 px-2.5 py-1.5 border border-[#e8e5e0] rounded-lg text-[12px] outline-none focus:border-[#1e3a5f] bg-white min-w-0" />
                    <input type="text" value={r.attorney_name} onChange={(e) => updateRecipient(i, "attorney_name", e.target.value)} placeholder="Attorney" className="flex-1 px-2.5 py-1.5 border border-[#e8e5e0] rounded-lg text-[12px] outline-none focus:border-[#1e3a5f] bg-white min-w-0" />
                    <select value={r.method} onChange={(e) => updateRecipient(i, "method", e.target.value)} className="px-2 py-1.5 border border-[#e8e5e0] rounded-lg text-[12px] bg-white shrink-0">
                      <option>CM/ECF</option><option value="email">Email</option><option value="mail">US Mail</option>
                    </select>
                    {recipients.length > 1 && (
                      <button onClick={() => removeRecipient(i)} className="text-[#c4c4c4] hover:text-[#b91c1c] transition text-lg shrink-0">&times;</button>
                    )}
                  </div>
                ))}
              </div>
            </div>

            <button onClick={generate} disabled={!attorney || loading} className="px-6 py-2.5 bg-[#1e3a5f] text-white text-[13px] font-semibold rounded-xl hover:bg-[#162a47] disabled:opacity-25 transition shadow-sm">
              {loading ? "Generating..." : "Generate Certificate"}
            </button>
          </div>
        </div>

        {/* Preview */}
        {text && (
          <div className="bg-white border border-[#e8e5e0] rounded-2xl overflow-hidden shadow-sm">
            <div className="px-5 py-3 border-b border-[#f0eee9] bg-[#fafaf8] flex items-center justify-between">
              <span className="text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide">Certificate Preview</span>
              <button onClick={() => navigator.clipboard.writeText(text)} className="text-[11px] text-[#1e3a5f] font-semibold hover:underline">Copy to clipboard</button>
            </div>
            <div className="p-6 bg-white">
              <div className="border border-[#e8e5e0] rounded-xl p-6 bg-[#fafaf8] font-serif text-[14px] text-[#1a1a1a] leading-[1.8] whitespace-pre-wrap">{text}</div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

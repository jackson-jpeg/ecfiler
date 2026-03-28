"use client";

import { useState } from "react";
import { generateCOS } from "@/lib/api";

export default function CertificatePage() {
  const [attorney, setAttorney] = useState("");
  const [caseNum, setCaseNum] = useState("");
  const [recipients, setRecipients] = useState([{ name: "", attorney_name: "", method: "CM/ECF" }]);
  const [text, setText] = useState("");

  const addRecipient = () => setRecipients([...recipients, { name: "", attorney_name: "", method: "CM/ECF" }]);
  const removeRecipient = (i: number) => setRecipients(recipients.filter((_, j) => j !== i));
  const updateRecipient = (i: number, field: string, value: string) => {
    setRecipients(recipients.map((r, j) => j === i ? { ...r, [field]: value } : r));
  };

  const generate = async () => {
    const res = await generateCOS(attorney, caseNum, recipients.filter((r) => r.name || r.attorney_name));
    setText(res.text);
  };

  return (
    <div className="px-8 py-8 max-w-2xl">
      <h1 className="text-xl font-bold tracking-tight mb-1">Certificate of Service</h1>
      <p className="text-sm text-[#525252] mb-5">Generate and download as PDF.</p>

      <div className="bg-white border border-[#e8e5e0] rounded-xl p-5 mb-4">
        <div className="grid grid-cols-2 gap-3 mb-4">
          <div>
            <label className="block text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide mb-1">Attorney</label>
            <input type="text" value={attorney} onChange={(e) => setAttorney(e.target.value)} placeholder="Jane Smith, Esq." className="w-full px-3 py-2 border border-[#e8e5e0] rounded-lg text-sm outline-none focus:border-[#1e3a5f]" />
          </div>
          <div>
            <label className="block text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide mb-1">Case</label>
            <input type="text" value={caseNum} onChange={(e) => setCaseNum(e.target.value)} placeholder="1:24-cv-01234" className="w-full px-3 py-2 border border-[#e8e5e0] rounded-lg text-sm outline-none focus:border-[#1e3a5f]" />
          </div>
        </div>

        <div className="mb-4">
          <div className="flex justify-between mb-2">
            <label className="text-[10px] font-semibold text-[#8a8a8a] uppercase tracking-wide">Recipients</label>
            <button onClick={addRecipient} className="text-xs text-[#1e3a5f] font-medium">+ Add</button>
          </div>
          {recipients.map((r, i) => (
            <div key={i} className="flex gap-2 mb-2">
              <input type="text" value={r.name} onChange={(e) => updateRecipient(i, "name", e.target.value)} placeholder="Party" className="flex-1 px-2.5 py-1.5 border border-[#e8e5e0] rounded-lg text-sm outline-none" />
              <input type="text" value={r.attorney_name} onChange={(e) => updateRecipient(i, "attorney_name", e.target.value)} placeholder="Attorney" className="flex-1 px-2.5 py-1.5 border border-[#e8e5e0] rounded-lg text-sm outline-none" />
              <select value={r.method} onChange={(e) => updateRecipient(i, "method", e.target.value)} className="px-2 py-1.5 border border-[#e8e5e0] rounded-lg text-sm bg-white">
                <option>CM/ECF</option><option value="email">Email</option><option value="mail">Mail</option>
              </select>
              <button onClick={() => removeRecipient(i)} className="text-[#c4c4c4] hover:text-[#b91c1c] text-lg">×</button>
            </div>
          ))}
        </div>

        <button onClick={generate} disabled={!attorney} className="px-5 py-2 bg-[#1e3a5f] text-white text-sm font-semibold rounded-lg hover:bg-[#162a47] disabled:opacity-25 transition">
          Generate
        </button>
      </div>

      {text && (
        <div className="bg-white border border-[#e8e5e0] rounded-xl overflow-hidden">
          <div className="px-5 py-3 border-b border-[#f0eee9]">
            <span className="text-xs font-semibold text-[#8a8a8a] uppercase tracking-wide">Preview</span>
          </div>
          <pre className="p-5 text-sm whitespace-pre-wrap font-mono text-[#525252] leading-relaxed">{text}</pre>
        </div>
      )}
    </div>
  );
}

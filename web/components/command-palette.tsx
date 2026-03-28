"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";

interface Command {
  id: string;
  label: string;
  description: string;
  action: () => void;
  icon: string;
  category: string;
}

export function CommandPalette() {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const router = useRouter();

  const commands: Command[] = [
    { id: "file", label: "New Filing", description: "Drop a PDF to start filing", action: () => router.push("/file"), icon: "M12 16.5V9.75m0 0l3 3m-3-3l-3 3M6.75 19.5a4.5 4.5 0 01-1.41-8.775 5.25 5.25 0 0110.338-2.32 3 3 0 013.758 3.848A3.752 3.752 0 0118 19.5H6.75z", category: "Filing" },
    { id: "history", label: "Filing History", description: "View past filings", action: () => router.push("/history"), icon: "M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z", category: "Filing" },
    { id: "courts", label: "Court Directory", description: "Search 207 federal courts", action: () => router.push("/courts"), icon: "M12 21v-8.25M15.75 21v-8.25M8.25 21v-8.25M3 9l9-6 9 6m-1.5 12V10.332A48.36 48.36 0 0012 9.75c-2.551 0-5.056.2-7.5.582V21", category: "Tools" },
    { id: "validate", label: "Validate PDF", description: "Check CM/ECF requirements", action: () => router.push("/validate"), icon: "M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z", category: "Tools" },
    { id: "certificate", label: "Certificate of Service", description: "Generate CoS", action: () => router.push("/certificate"), icon: "M9 12h3.75M9 15h3.75M9 18h3.75m3 .75H18a2.25 2.25 0 002.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 00-1.123-.08m-5.801 0c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 00.75-.75 2.25 2.25 0 00-.1-.664m-5.8 0A2.251 2.251 0 0113.5 2.25H15c1.012 0 1.867.668 2.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V8.25m0 0H4.875c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125V9.375c0-.621-.504-1.125-1.125-1.125H8.25z", category: "Tools" },
    { id: "settings", label: "Settings", description: "PACER credentials, profile", action: () => router.push("/settings"), icon: "M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.325.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 011.37.49l1.296 2.247a1.125 1.125 0 01-.26 1.431l-1.003.827c-.293.241-.438.613-.43.992a7 7 0 010 .255c-.008.378.137.75.43.991l1.004.827c.424.35.534.955.26 1.43l-1.298 2.247a1.125 1.125 0 01-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a7 7 0 01-.22.128c-.331.183-.581.495-.644.869l-.213 1.281c-.09.543-.56.94-1.11.94h-2.594c-.55 0-1.019-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a7 7 0 01-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 01-1.369-.49l-1.297-2.247a1.125 1.125 0 01.26-1.431l1.004-.827c.292-.24.437-.613.43-.991a7 7 0 010-.255c.007-.38-.138-.751-.43-.992l-1.004-.827a1.125 1.125 0 01-.26-1.43l1.297-2.247a1.125 1.125 0 011.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044.146-.086.22-.128.332-.183.582-.495.644-.869l.214-1.28z", category: "Account" },
    { id: "resources", label: "What is CM/ECF?", description: "Learn about federal e-filing", action: () => router.push("/what-is-cmecf"), icon: "M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25", category: "Resources" },
  ];

  const filtered = query
    ? commands.filter((c) => c.label.toLowerCase().includes(query.toLowerCase()) || c.description.toLowerCase().includes(query.toLowerCase()))
    : commands;

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setOpen((o) => !o);
        setQuery("");
        setSelected(0);
      }
      if (e.key === "Escape" && open) {
        setOpen(false);
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [open]);

  useEffect(() => {
    if (open) inputRef.current?.focus();
  }, [open]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "ArrowDown") { e.preventDefault(); setSelected((s) => Math.min(s + 1, filtered.length - 1)); }
    if (e.key === "ArrowUp") { e.preventDefault(); setSelected((s) => Math.max(s - 1, 0)); }
    if (e.key === "Enter" && filtered[selected]) { filtered[selected].action(); setOpen(false); }
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-[150] flex items-start justify-center pt-[20vh]" onClick={() => setOpen(false)}>
      <div className="absolute inset-0 bg-black/30 backdrop-blur-sm" />
      <div className="relative w-[calc(100%-2rem)] sm:w-[520px] bg-white rounded-2xl shadow-2xl border border-[#e8e5e0] overflow-hidden" onClick={(e) => e.stopPropagation()}>
        <div className="p-3 border-b border-[#f0eee9] flex items-center gap-3">
          <svg className="w-4 h-4 text-[#8a8a8a] shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" />
          </svg>
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => { setQuery(e.target.value); setSelected(0); }}
            onKeyDown={handleKeyDown}
            placeholder="Search commands..."
            className="flex-1 text-[14px] outline-none bg-transparent text-[#1a1a1a] placeholder-[#c4c4c4]"
          />
          <kbd className="text-[10px] px-1.5 py-0.5 bg-[#f5f3ee] text-[#8a8a8a] rounded border border-[#e8e5e0] font-mono">esc</kbd>
        </div>
        <div className="max-h-[300px] overflow-y-auto py-2">
          {filtered.map((cmd, i) => (
            <button
              key={cmd.id}
              onClick={() => { cmd.action(); setOpen(false); }}
              onMouseEnter={() => setSelected(i)}
              className={`w-full flex items-center gap-3 px-4 py-2.5 text-left transition ${
                i === selected ? "bg-[#f0f4fa]" : "hover:bg-[#fafaf8]"
              }`}
            >
              <div className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 ${i === selected ? "bg-[#1e3a5f] text-white" : "bg-[#f5f3ee] text-[#8a8a8a]"}`}>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d={cmd.icon} />
                </svg>
              </div>
              <div className="min-w-0 flex-1">
                <div className="text-[13px] font-medium text-[#1a1a1a]">{cmd.label}</div>
                <div className="text-[11px] text-[#8a8a8a] truncate">{cmd.description}</div>
              </div>
              <span className="text-[9px] text-[#c4c4c4] font-medium shrink-0">{cmd.category}</span>
            </button>
          ))}
          {filtered.length === 0 && (
            <div className="px-4 py-6 text-center text-[13px] text-[#8a8a8a]">No matching commands</div>
          )}
        </div>
        <div className="border-t border-[#f0eee9] px-4 py-2 flex items-center gap-4 text-[10px] text-[#c4c4c4]">
          <span className="flex items-center gap-1"><kbd className="px-1 py-0.5 bg-[#f5f3ee] rounded border border-[#e8e5e0] font-mono">↑↓</kbd> navigate</span>
          <span className="flex items-center gap-1"><kbd className="px-1 py-0.5 bg-[#f5f3ee] rounded border border-[#e8e5e0] font-mono">↵</kbd> select</span>
          <span className="flex items-center gap-1"><kbd className="px-1 py-0.5 bg-[#f5f3ee] rounded border border-[#e8e5e0] font-mono">esc</kbd> close</span>
        </div>
      </div>
    </div>
  );
}

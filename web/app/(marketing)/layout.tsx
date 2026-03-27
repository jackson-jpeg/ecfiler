import Link from "next/link";

export default function MarketingLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-white">
      <nav className="border-b border-zinc-100 sticky top-0 z-50 bg-white/80 backdrop-blur-sm">
        <div className="max-w-3xl mx-auto px-6 h-14 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2.5">
            <div className="w-7 h-7 bg-zinc-900 rounded-lg flex items-center justify-center text-white text-[11px] font-bold">E</div>
            <span className="text-[15px] font-semibold tracking-tight">ECFiler</span>
          </Link>
          <Link href="/file" className="px-4 py-1.5 bg-zinc-900 text-white text-sm font-medium rounded-lg hover:bg-zinc-800 transition">
            Open App
          </Link>
        </div>
      </nav>
      <main className="max-w-3xl mx-auto px-6 py-12">
        {children}
      </main>
      <footer className="border-t border-zinc-100 max-w-3xl mx-auto px-6 py-6 text-xs text-zinc-400">
        ECFiler is a filing tool, not a legal advisor. <a href="https://github.com/jackson-jpeg/ecfiler" className="hover:text-zinc-600">GitHub</a>
      </footer>
    </div>
  );
}

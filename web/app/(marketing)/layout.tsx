import Link from "next/link";

export default function MarketingLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-[#fafaf8]">
      <nav className="bg-white/90 backdrop-blur-md border-b border-[#e8e5e0] sticky top-0 z-50">
        <div className="max-w-4xl mx-auto px-5 sm:px-8 h-14 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2.5">
            <div className="w-7 h-7 bg-gradient-to-br from-[#1e3a5f] to-[#0f2440] rounded-lg flex items-center justify-center text-white text-[10px] font-bold shadow-sm">E</div>
            <span className="text-[15px] font-semibold tracking-tight text-[#1a1a1a]">ECFiler</span>
          </Link>
          <div className="flex items-center gap-5 text-[13px]">
            <Link href="/federal-courts" className="text-[#525252] hover:text-[#1a1a1a] transition font-medium hidden sm:inline">Courts</Link>
            <Link href="/what-is-cmecf" className="text-[#525252] hover:text-[#1a1a1a] transition font-medium hidden sm:inline">Resources</Link>
            <Link href="/sign-up" className="px-4 py-1.5 bg-[#1e3a5f] text-white text-[12px] font-semibold rounded-lg hover:bg-[#162a47] transition shadow-sm">Start Filing</Link>
          </div>
        </div>
      </nav>
      <main className="max-w-4xl mx-auto px-5 sm:px-8 py-12 sm:py-16">
        {children}
      </main>
      <footer className="bg-white border-t border-[#e8e5e0]">
        <div className="max-w-4xl mx-auto px-5 sm:px-8 py-6 flex flex-col sm:flex-row items-center justify-between gap-4 text-[12px] text-[#8a8a8a]">
          <span>ECFiler is a filing tool, not a legal advisor.</span>
          <div className="flex gap-4">
            <Link href="/federal-courts" className="hover:text-[#525252] transition">Courts</Link>
            <Link href="/what-is-cmecf" className="hover:text-[#525252] transition">Resources</Link>
            <a href="https://github.com/jackson-jpeg/ecfiler" className="hover:text-[#525252] transition">GitHub</a>
          </div>
        </div>
      </footer>
    </div>
  );
}

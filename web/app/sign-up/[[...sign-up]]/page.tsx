import { SignUp } from "@clerk/nextjs";
import Link from "next/link";

export default function SignUpPage() {
  return (
    <div className="min-h-screen flex bg-[#f5f3ee]">
      {/* Left panel — value prop */}
      <div className="hidden lg:flex lg:w-[45%] bg-gradient-to-br from-[#0f1f35] to-[#1e3a5f] p-12 flex-col justify-between relative overflow-hidden">
        <div className="absolute inset-0 opacity-5" style={{ backgroundImage: "radial-gradient(circle at 1px 1px, white 1px, transparent 0)", backgroundSize: "32px 32px" }} />
        <div className="relative">
          <Link href="/" className="inline-flex items-center gap-2.5 mb-12">
            <div className="w-9 h-9 bg-white/10 rounded-xl flex items-center justify-center text-white text-[13px] font-bold border border-white/10">E</div>
            <span className="text-[18px] font-semibold text-white">ECFiler</span>
          </Link>
          <h2 className="text-[28px] font-bold text-white leading-tight mb-4">File on CM/ECF<br />in under a minute</h2>
          <p className="text-[15px] text-white/50 leading-relaxed mb-10">Drop a PDF. AI reads the document, extracts the case, court, and event code. You review and file.</p>
          <div className="space-y-4">
            {[
              "207 federal courts supported",
              "AI event code matching",
              "Rule 5.2 redaction scanning",
              "7 pre-filing safety checks",
            ].map((f) => (
              <div key={f} className="flex items-center gap-3 text-[13px] text-white/70">
                <div className="w-5 h-5 bg-white/10 rounded-full flex items-center justify-center text-[9px] text-[#bbf7d0] font-bold">&#10003;</div>
                {f}
              </div>
            ))}
          </div>
        </div>
        <div className="relative text-[11px] text-white/20">Free to use. No credit card required.</div>
      </div>

      {/* Right panel — sign up form */}
      <div className="flex-1 flex items-center justify-center px-4 py-12">
        <div className="w-full max-w-md">
          <div className="text-center mb-8 lg:hidden">
            <Link href="/" className="inline-flex items-center gap-2.5 mb-4">
              <div className="w-9 h-9 bg-gradient-to-br from-[#1e3a5f] to-[#0f2440] rounded-xl flex items-center justify-center text-white text-[13px] font-bold shadow-lg shadow-[#1e3a5f]/20">E</div>
              <span className="text-[18px] font-semibold tracking-tight text-[#1a1a1a]">ECFiler</span>
            </Link>
            <p className="text-[13px] text-[#8a8a8a]">Create your account to start filing</p>
          </div>
          <div className="hidden lg:block text-center mb-8">
            <h2 className="text-[22px] font-bold text-[#1a1a1a] mb-1">Create your account</h2>
            <p className="text-[13px] text-[#8a8a8a]">Start filing on CM/ECF in under a minute</p>
          </div>
          <SignUp
            fallbackRedirectUrl="/onboarding"
            appearance={{
              elements: {
                rootBox: "mx-auto w-full",
                card: "shadow-xl shadow-black/5 border border-[#e8e5e0] rounded-2xl bg-white",
                headerTitle: "text-[#1a1a1a]",
                headerSubtitle: "text-[#8a8a8a]",
                formButtonPrimary: "bg-[#1e3a5f] hover:bg-[#162a47] shadow-sm",
                footerActionLink: "text-[#1e3a5f] hover:text-[#162a47]",
              },
            }}
          />
          <div className="text-center mt-6">
            <Link href="/" className="text-[12px] text-[#8a8a8a] hover:text-[#525252] transition">&larr; Back to ECFiler</Link>
          </div>
        </div>
      </div>
    </div>
  );
}
